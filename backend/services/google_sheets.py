import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class GoogleSheetsService:
    def __init__(self):
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1H07FB3X_tkSLSoHx-F2kyDmNQIGR4EyyTjnF-u19G3c/export?format=csv&gid=0"
        self.data = None
        self.last_update = None
        
    def fetch_data(self ):
        """Busca dados da planilha do Google Sheets"""
        try:
            # Lê dados da planilha
            df = pd.read_csv(self.sheet_url)
            
            # Limpa e padroniza os dados
            df = self._clean_data(df)
            
            self.data = df
            self.last_update = datetime.now()
            return df
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None
    
    def _clean_data(self, df):
        """Limpa e padroniza os dados"""
        # Renomeia colunas para padrão
        column_mapping = {
            'nº do pedido': 'numero_pedido',
            'cliente/projeto': 'cliente',
            'categoria': 'categoria',
            'produto/serviço': 'produto_servico',
            'valor': 'valor',
            'custos do pedido': 'custos',
            'diária de equipe': 'diarias_equipe',
            'local': 'local',
            'data de entrega': 'data_entrega',
            'data de recolhimento': 'data_recolhimento',
            'data de pagamento': 'data_pagamento'
        }
        
        # Renomeia colunas se existirem
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Limpa valores monetários
        if 'valor' in df.columns:
            df['valor'] = df['valor'].apply(self._clean_currency)
        if 'custos' in df.columns:
            df['custos'] = df['custos'].apply(self._clean_currency)
        
        # Limpa diárias de equipe
        if 'diarias_equipe' in df.columns:
            df['diarias_equipe'] = df['diarias_equipe'].apply(self._clean_numeric)
        
        # Converte datas
        date_columns = ['data_entrega', 'data_recolhimento', 'data_pagamento']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%d/%m', errors='coerce')
                # Assume ano atual se não especificado
                current_year = datetime.now().year
                df[col] = df[col].apply(lambda x: x.replace(year=current_year) if pd.notna(x) else x)
        
        # Remove linhas vazias
        df = df.dropna(subset=['cliente'], how='all')
        
        return df
    
    def _clean_currency(self, value):
        """Limpa valores monetários"""
        if pd.isna(value) or value == '':
            return 0.0
        
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto vírgula e ponto
            value = re.sub(r'[^\d,.]', '', str(value))
            # Substitui vírgula por ponto
            value = value.replace(',', '.')
            
        try:
            return float(value)
        except:
            return 0.0
    
    def _clean_numeric(self, value):
        """Limpa valores numéricos"""
        if pd.isna(value) or value == '':
            return 0
        
        if isinstance(value, str):
            # Extrai apenas números
            numbers = re.findall(r'\d+', str(value))
            if numbers:
                return int(numbers[0])
        
        try:
            return int(float(value))
        except:
            return 0
    
    def get_kpis(self):
        """Calcula KPIs principais"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # KPIs básicos
        total_receita = df['valor'].sum()
        total_custos = df['custos'].sum()
        lucro_bruto = total_receita - total_custos
        margem_lucro = (lucro_bruto / total_receita * 100) if total_receita > 0 else 0
        total_pedidos = len(df)
        ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else 0
        
        # KPIs avançados
        pedidos_pagos = df[df['data_pagamento'].notna()]
        pedidos_pendentes = df[df['data_pagamento'].isna()]
        taxa_inadimplencia = len(pedidos_pendentes) / total_pedidos * 100 if total_pedidos > 0 else 0
        
        # Análise por categoria
        receita_por_categoria = df.groupby('categoria')['valor'].sum().to_dict()
        margem_por_categoria = df.groupby('categoria').apply(
            lambda x: (x['valor'].sum() - x['custos'].sum()) / x['valor'].sum() * 100 if x['valor'].sum() > 0 else 0
        ).to_dict()
        
        return {
            'financeiro': {
                'total_receita': total_receita,
                'total_custos': total_custos,
                'lucro_bruto': lucro_bruto,
                'margem_lucro': margem_lucro,
                'ticket_medio': ticket_medio
            },
            'operacional': {
                'total_pedidos': total_pedidos,
                'pedidos_pagos': len(pedidos_pagos),
                'pedidos_pendentes': len(pedidos_pendentes),
                'taxa_inadimplencia': taxa_inadimplencia
            },
            'categorias': {
                'receita_por_categoria': receita_por_categoria,
                'margem_por_categoria': margem_por_categoria
            }
        }
    
    def get_evolucao_temporal(self):
        """Retorna evolução temporal das métricas"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data.copy()
        
        # Usa data de entrega como referência
        df['mes'] = df['data_entrega'].dt.to_period('M')
        
        evolucao = df.groupby('mes').agg({
            'valor': 'sum',
            'custos': 'sum',
            'numero_pedido': 'count'
        }).reset_index()
        
        evolucao['lucro'] = evolucao['valor'] - evolucao['custos']
        evolucao['mes'] = evolucao['mes'].astype(str)
        
        return evolucao.to_dict('records')
    
    def get_top_produtos(self, limit=10):
        """Retorna top produtos por receita"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # Agrupa por produto/serviço
        produtos = df.groupby('produto_servico').agg({
            'valor': 'sum',
            'custos': 'sum',
            'numero_pedido': 'count'
        }).reset_index()
        
        produtos['lucro'] = produtos['valor'] - produtos['custos']
        produtos['margem'] = produtos['lucro'] / produtos['valor'] * 100
        
        return produtos.nlargest(limit, 'valor').to_dict('records')
    
    def get_top_clientes(self, limit=10):
        """Retorna top clientes por receita"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # Agrupa por cliente
        clientes = df.groupby('cliente').agg({
            'valor': 'sum',
            'custos': 'sum',
            'numero_pedido': 'count'
        }).reset_index()
        
        clientes['lucro'] = clientes['valor'] - clientes['custos']
        clientes['ticket_medio'] = clientes['valor'] / clientes['numero_pedido']
        
        return clientes.nlargest(limit, 'valor').to_dict('records')
    
    def get_analise_locais(self):
        """Retorna análise por localização"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # Agrupa por local
        locais = df.groupby('local').agg({
            'valor': 'sum',
            'custos': 'sum',
            'numero_pedido': 'count'
        }).reset_index()
        
        locais['lucro'] = locais['valor'] - locais['custos']
        locais['margem'] = locais['lucro'] / locais['valor'] * 100
        
        return locais.to_dict('records')
    
    def get_alertas(self):
        """Retorna alertas importantes"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        alertas = []
        
        # Pagamentos em atraso (mais de 30 dias da entrega)
        hoje = datetime.now()
        df_atraso = df[
            (df['data_pagamento'].isna()) & 
            (df['data_entrega'] < hoje - timedelta(days=30))
        ]
        
        if len(df_atraso) > 0:
            valor_atraso = df_atraso['valor'].sum()
            alertas.append({
                'tipo': 'pagamento_atraso',
                'titulo': f'{len(df_atraso)} pagamentos em atraso',
                'descricao': f'Total de R$ {valor_atraso:,.2f} em atraso',
                'criticidade': 'alta'
            })
        
        # Eventos próximos (próximos 7 dias)
        df_proximos = df[
            (df['data_entrega'] >= hoje) & 
            (df['data_entrega'] <= hoje + timedelta(days=7))
        ]
        
        if len(df_proximos) > 0:
            alertas.append({
                'tipo': 'eventos_proximos',
                'titulo': f'{len(df_proximos)} eventos nos próximos 7 dias',
                'descricao': 'Verificar preparação de equipamentos',
                'criticidade': 'media'
            })
        
        # Margem baixa (menos de 10%)
        df_margem_baixa = df[
            (df['valor'] > 0) & 
            ((df['valor'] - df['custos']) / df['valor'] < 0.1)
        ]
        
        if len(df_margem_baixa) > 0:
            alertas.append({
                'tipo': 'margem_baixa',
                'titulo': f'{len(df_margem_baixa)} pedidos com margem baixa',
                'descricao': 'Revisar precificação',
                'criticidade': 'media'
            })
        
        return alertas
    
    def get_previsoes(self):
        """Retorna previsões baseadas em dados históricos"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # Receita média mensal
        df['mes'] = df['data_entrega'].dt.to_period('M')
        receita_mensal = df.groupby('mes')['valor'].sum()
        
        if len(receita_mensal) > 0:
            media_mensal = receita_mensal.mean()
            
            # Projeção próximos 3 meses
            projecoes = []
            for i in range(1, 4):
                mes_futuro = datetime.now() + timedelta(days=30*i)
                projecoes.append({
                    'mes': mes_futuro.strftime('%Y-%m'),
                    'receita_projetada': media_mensal,
                    'confianca': max(0.5, 1 - (i * 0.1))  # Diminui confiança com tempo
                })
            
            return projecoes
        
        return []
