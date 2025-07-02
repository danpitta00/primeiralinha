from flask import Blueprint, jsonify, request
from services.google_sheets import GoogleSheetsService
import sys
import os

pedidos_bp = Blueprint('pedidos', __name__)
sheets_service = GoogleSheetsService()

@pedidos_bp.route('/', methods=['GET'])
def get_pedidos():
    """Retorna lista de todos os pedidos"""
    try:
        # Busca dados atualizados
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        # Converte para lista de dicionários
        pedidos = df.to_dict('records')
        
        # Converte datas para string para serialização JSON
        for pedido in pedidos:
            for key, value in pedido.items():
                if hasattr(value, 'strftime'):
                    pedido[key] = value.strftime('%Y-%m-%d') if value else None
                elif str(value) == 'nan':
                    pedido[key] = None
        
        return jsonify({
            'success': True,
            'data': pedidos,
            'total': len(pedidos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pedidos_bp.route('/filtros', methods=['GET'])
def get_pedidos_filtrados():
    """Retorna pedidos filtrados"""
    try:
        # Parâmetros de filtro
        categoria = request.args.get('categoria')
        status_pagamento = request.args.get('status_pagamento')
        cliente = request.args.get('cliente')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Busca dados
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        # Aplica filtros
        if categoria and categoria != 'todos':
            df = df[df['categoria'].str.contains(categoria, case=False, na=False)]
        
        if status_pagamento:
            if status_pagamento == 'pago':
                df = df[df['data_pagamento'].notna()]
            elif status_pagamento == 'pendente':
                df = df[df['data_pagamento'].isna()]
        
        if cliente:
            df = df[df['cliente'].str.contains(cliente, case=False, na=False)]
        
        # Filtros de data (usando data de entrega)
        if data_inicio:
            df = df[df['data_entrega'] >= data_inicio]
        
        if data_fim:
            df = df[df['data_entrega'] <= data_fim]
        
        # Converte para lista
        pedidos = df.to_dict('records')
        
        # Converte datas para string
        for pedido in pedidos:
            for key, value in pedido.items():
                if hasattr(value, 'strftime'):
                    pedido[key] = value.strftime('%Y-%m-%d') if value else None
                elif str(value) == 'nan':
                    pedido[key] = None
        
        return jsonify({
            'success': True,
            'data': pedidos,
            'total': len(pedidos),
            'filtros_aplicados': {
                'categoria': categoria,
                'status_pagamento': status_pagamento,
                'cliente': cliente,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pedidos_bp.route('/buscar', methods=['GET'])
def buscar_pedidos():
    """Busca pedidos por texto"""
    try:
        termo = request.args.get('q', '').strip()
        
        if not termo:
            return jsonify({
                'success': False,
                'error': 'Termo de busca é obrigatório'
            }), 400
        
        # Busca dados
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        # Busca em múltiplas colunas
        mask = (
            df['cliente'].str.contains(termo, case=False, na=False) |
            df['produto_servico'].str.contains(termo, case=False, na=False) |
            df['local'].str.contains(termo, case=False, na=False) |
            df['categoria'].str.contains(termo, case=False, na=False)
        )
        
        df_resultado = df[mask]
        
        # Converte para lista
        pedidos = df_resultado.to_dict('records')
        
        # Converte datas para string
        for pedido in pedidos:
            for key, value in pedido.items():
                if hasattr(value, 'strftime'):
                    pedido[key] = value.strftime('%Y-%m-%d') if value else None
                elif str(value) == 'nan':
                    pedido[key] = None
        
        return jsonify({
            'success': True,
            'data': pedidos,
            'total': len(pedidos),
            'termo_busca': termo
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pedidos_bp.route('/estatisticas', methods=['GET'])
def get_estatisticas_pedidos():
    """Retorna estatísticas dos pedidos"""
    try:
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        # Estatísticas básicas
        total_pedidos = len(df)
        pedidos_pagos = len(df[df['data_pagamento'].notna()])
        pedidos_pendentes = total_pedidos - pedidos_pagos
        
        return jsonify({
            'success': True,
            'data': {
                'resumo': {
                    'total_pedidos': total_pedidos,
                    'pedidos_pagos': pedidos_pagos,
                    'pedidos_pendentes': pedidos_pendentes,
                    'taxa_pagamento': round((pedidos_pagos / total_pedidos * 100), 2) if total_pedidos > 0 else 0
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pedidos_bp.route('/proximos-eventos', methods=['GET'])
def get_proximos_eventos():
    """Retorna eventos próximos (próximos 30 dias)"""
    try:
        from datetime import datetime, timedelta
        
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        # Filtra eventos dos próximos 30 dias
        hoje = datetime.now()
        limite = hoje + timedelta(days=30)
        
        df_proximos = df[
            (df['data_entrega'] >= hoje) & 
            (df['data_entrega'] <= limite)
        ].sort_values('data_entrega')
        
        # Converte para lista
        eventos = df_proximos.to_dict('records')
        
        # Converte datas para string
        for evento in eventos:
            for key, value in evento.items():
                if hasattr(value, 'strftime'):
                    evento[key] = value.strftime('%Y-%m-%d') if value else None
                elif str(value) == 'nan':
                    evento[key] = None
        
        return jsonify({
            'success': True,
            'data': eventos,
            'total': len(eventos)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pedidos_bp.route('/pendencias', methods=['GET'])
def get_pendencias():
    """Retorna pedidos com pendências"""
    try:
        from datetime import datetime, timedelta
        
        df = sheets_service.fetch_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Erro ao buscar dados da planilha'
            }), 500
        
        hoje = datetime.now()
        
        # Pagamentos pendentes há mais de 30 dias
        df_pagamento_atraso = df[
            (df['data_pagamento'].isna()) & 
            (df['data_entrega'] < hoje - timedelta(days=30))
        ]
        
        pendencias = {
            'pagamentos_atraso': df_pagamento_atraso.to_dict('records')
        }
        
        # Converte datas para string
        for categoria in pendencias.values():
            for item in categoria:
                for key, value in item.items():
                    if hasattr(value, 'strftime'):
                        item[key] = value.strftime('%Y-%m-%d') if value else None
                    elif str(value) == 'nan':
                        item[key] = None
        
        return jsonify({
            'success': True,
            'data': pendencias,
            'resumo': {
                'pagamentos_atraso': len(pendencias['pagamentos_atraso'])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
