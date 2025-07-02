"""
Dashboard Primeira Linha Eventos - Backend Otimizado
Versão 2.0 - Sistema Empresarial Completo

Este arquivo substitui o app.py atual do Streamlit por um backend Flask robusto
com APIs avançadas e funcionalidades empresariais.
"""

import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Importa as rotas
from routes.analytics import analytics_bp
from routes.pedidos import pedidos_bp

# Configuração da aplicação
app = Flask(__name__, static_folder='../frontend')
app.config['SECRET_KEY'] = 'primeira-linha-eventos-2024'

# Habilita CORS para todas as rotas (necessário para frontend)
CORS(app, origins="*")

# Registra blueprints das APIs
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Primeira Linha Eventos v2.0 funcionando',
        'version': '2.0.0',
        'features': [
            'KPIs empresariais avançados',
            'Sistema de alertas inteligente',
            'Análises preditivas',
            'Gestão completa de pedidos',
            'Dashboard executivo responsivo'
        ]
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Informações sobre as APIs disponíveis"""
    return jsonify({
        'apis_disponiveis': {
            'analytics': {
                'kpis': '/api/analytics/kpis',
                'dashboard_executivo': '/api/analytics/dashboard-executivo',
                'evolucao_temporal': '/api/analytics/evolucao-temporal',
                'top_produtos': '/api/analytics/top-produtos',
                'top_clientes': '/api/analytics/top-clientes',
                'alertas': '/api/analytics/alertas',
                'previsoes': '/api/analytics/previsoes'
            },
            'pedidos': {
                'listar': '/api/pedidos/',
                'filtros': '/api/pedidos/filtros',
                'buscar': '/api/pedidos/buscar',
                'estatisticas': '/api/pedidos/estatisticas',
                'proximos_eventos': '/api/pedidos/proximos-eventos',
                'pendencias': '/api/pedidos/pendencias'
            }
        },
        'documentacao': 'Consulte o manual do usuário para detalhes'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve o frontend (dashboard) ou arquivos estáticos"""
    static_folder_path = app.static_folder
    
    if static_folder_path is None:
        return jsonify({
            'error': 'Frontend não configurado',
            'message': 'Acesse /api/health para verificar se a API está funcionando'
        }), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Serve o dashboard principal
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Dashboard Primeira Linha Eventos v2.0',
                'status': 'Backend funcionando',
                'frontend': 'Não encontrado - coloque index.html na pasta frontend/',
                'api_health': '/api/health',
                'api_info': '/api/info'
            })

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'message': 'Consulte /api/info para ver endpoints disponíveis'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Verifique os logs para mais detalhes'
    }), 500

if __name__ == '__main__':
    # Configuração para desenvolvimento e produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🎪 Iniciando Dashboard Primeira Linha Eventos v2.0")
    print(f"📡 Servidor rodando na porta {port}")
    print(f"🔧 Modo debug: {debug}")
    print("📊 APIs disponíveis em /api/info")
    print("🏠 Dashboard em /")
    
    app.run(
        host='0.0.0.0',  # Necessário para Render.com
        port=port,
        debug=debug
    )
