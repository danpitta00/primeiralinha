"""
Dashboard Primeira Linha Eventos - Aplicação Principal
Versão 2.0 - Sistema Flask Completo

Este arquivo substitui o Streamlit por um sistema Flask robusto
que serve tanto o backend (APIs) quanto o frontend (dashboard).
"""

import os
import sys
from flask import Flask, send_from_directory, jsonify, send_file
from flask_cors import CORS

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importa as rotas do backend
try:
    from routes.analytics import analytics_bp
    from routes.pedidos import pedidos_bp
except ImportError as e:
    print(f"Erro ao importar rotas: {e}")
    # Cria blueprints vazios para evitar erro
    from flask import Blueprint
    analytics_bp = Blueprint('analytics', __name__)
    pedidos_bp = Blueprint('pedidos', __name__)

# Configuração da aplicação Flask
app = Flask(__name__, 
           static_folder='frontend',
           static_url_path='')

app.config['SECRET_KEY'] = 'primeira-linha-eventos-2024'

# Habilita CORS para todas as rotas
CORS(app, origins="*")

# Registra blueprints das APIs
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')

@app.route('/')
def index():
    """Serve o dashboard principal"""
    try:
        return send_file('frontend/index.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Dashboard Primeira Linha Eventos</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
            <h1>🎪 Dashboard Primeira Linha Eventos</h1>
            <h2>Sistema em Inicialização...</h2>
            <p>Erro: {str(e)}</p>
            <p>Verifique se o arquivo frontend/index.html existe.</p>
            <hr>
            <p><a href="/api/health">Verificar API</a> | <a href="/api/info">Informações do Sistema</a></p>
        </body>
        </html>
        """

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'message': 'Dashboard Primeira Linha Eventos v2.0 funcionando',
        'version': '2.0.0',
        'sistema': 'Flask + APIs + Dashboard Responsivo',
        'features': [
            'KPIs empresariais avançados',
            'Sistema de alertas inteligente', 
            'Análises preditivas',
            'Gestão completa de pedidos',
            'Dashboard executivo responsivo',
            'Integração Google Sheets automática'
        ]
    })

@app.route('/api/info')
def api_info():
    """Informações sobre as APIs disponíveis"""
    return jsonify({
        'sistema': 'Dashboard Primeira Linha Eventos v2.0',
        'tecnologia': 'Flask + HTML5 + JavaScript',
        'apis_disponiveis': {
            'analytics': {
                '/api/analytics/kpis': 'KPIs principais do negócio',
                '/api/analytics/evolucao-temporal': 'Evolução temporal das métricas',
                '/api/analytics/top-produtos': 'Top produtos por receita',
                '/api/analytics/top-clientes': 'Top clientes por receita',
                '/api/analytics/alertas': 'Alertas importantes',
                '/api/analytics/dashboard-executivo': 'Dashboard completo'
            },
            'pedidos': {
                '/api/pedidos/': 'Lista todos os pedidos',
                '/api/pedidos/filtros': 'Pedidos filtrados',
                '/api/pedidos/buscar': 'Busca pedidos por texto',
                '/api/pedidos/estatisticas': 'Estatísticas dos pedidos',
                '/api/pedidos/proximos-eventos': 'Eventos próximos',
                '/api/pedidos/pendencias': 'Pedidos com pendências'
            }
        },
        'frontend': {
            '/': 'Dashboard principal',
            '/api/health': 'Status da aplicação',
            '/api/info': 'Esta página'
        }
    })

@app.route('/dashboard')
def dashboard_redirect():
    """Redireciona para o dashboard principal"""
    return index()

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'message': 'Consulte /api/info para ver endpoints disponíveis',
        'dashboard': 'Acesse / para o dashboard principal'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Verifique os logs para mais detalhes',
        'dashboard': 'Acesse / para o dashboard principal'
    }), 500

if __name__ == '__main__':
    # Configuração para desenvolvimento e produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🎪" + "="*60)
    print("🚀 INICIANDO DASHBOARD PRIMEIRA LINHA EVENTOS v2.0")
    print("="*62)
    print(f"📡 Servidor rodando na porta: {port}")
    print(f"🔧 Modo debug: {debug}")
    print(f"🏠 Dashboard principal: http://localhost:{port}/" )
    print(f"📊 APIs disponíveis: http://localhost:{port}/api/info" )
    print(f"💚 Status da aplicação: http://localhost:{port}/api/health" )
    print("="*62)
    print("✨ FUNCIONALIDADES ATIVAS:")
    print("   • Dashboard executivo responsivo")
    print("   • 15+ KPIs empresariais")
    print("   • Gráficos interativos")
    print("   • Sistema de alertas")
    print("   • Gestão completa de pedidos")
    print("   • Integração Google Sheets")
    print("="*62)
    
    app.run(
        host='0.0.0.0',  # Necessário para Render.com
        port=port,
        debug=debug
    )
