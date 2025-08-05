"""
PWA PRIMEIRA LINHA EVENTOS - SISTEMA UNIFICADO
4 Interfaces em 1 Aplicativo: Comercial + Logística + Campo + Boss
Versão 1.0 - PWA Completo com Login por Perfil
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import io
import os
import json
import hashlib

# Configuração da página
st.set_page_config(
    page_title="Primeira Linha Eventos - Sistema Completo",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - PWA Unificado
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        color: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #1e1b4b 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
        border: 2px solid #D4AF37;
    }
    
    .login-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 2px solid #D4AF37;
    }
    
    .profile-card {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .profile-card:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.3);
    }
    
    .profile-comercial { border-left: 4px solid #10b981; }
    .profile-logistica { border-left: 4px solid #f59e0b; }
    .profile-campo { border-left: 4px solid #3b82f6; }
    .profile-boss { border-left: 4px solid #8b5cf6; }
    
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border-left: 4px solid #D4AF37;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.2);
    }
    
    .metric-card.green { border-left-color: #10b981; }
    .metric-card.blue { border-left-color: #3b82f6; }
    .metric-card.purple { border-left-color: #8b5cf6; }
    .metric-card.orange { border-left-color: #f59e0b; }
    .metric-card.red { border-left-color: #ef4444; }
    
    /* Interface Campo - Mobile First */
    .campo-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 1rem;
        border-radius: 15px;
        border: 2px solid #D4AF37;
        margin: 0.5rem 0;
    }
    
    .etapa-card {
        background: #374151;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #6b7280;
        position: relative;
        min-height: 80px;
        display: flex;
        align-items: center;
    }
    
    .etapa-ativa {
        border-left-color: #D4AF37;
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        animation: pulse 2s infinite;
    }
    
    .etapa-concluida {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }
    
    .etapa-bloqueada {
        border-left-color: #6b7280;
        background: #4b5563;
        opacity: 0.6;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #374151;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #D4AF37 0%, #B8941F 100%);
        transition: width 0.3s ease;
    }
    
    /* Interface Boss - Executiva */
    .boss-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        border: 2px solid #D4AF37;
        box-shadow: 0 8px 32px rgba(30, 27, 75, 0.3);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-pendente { background: #f59e0b; color: #1f2937; }
    .status-andamento { background: #3b82f6; color: white; }
    .status-concluido { background: #10b981; color: white; }
    .status-urgente { background: #ef4444; color: white; }
    .status-weekend { background: #8b5cf6; color: white; }
    
    .chat-container {
        background: #1f2937;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .chat-message {
        background: #374151;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #D4AF37;
    }
    
    .chat-message.sent {
        background: #1e3a8a;
        border-left-color: #3b82f6;
        margin-left: 2rem;
    }
    
    .notification-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
    }
    
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header { padding: 1rem; }
        .login-container { padding: 2rem; margin: 1rem; }
        .profile-card { padding: 1rem; }
        .metric-card { padding: 1rem; }
        .campo-container { padding: 0.75rem; }
        .etapa-card { padding: 0.75rem; min-height: 60px; }
        .boss-card { padding: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# Dados de usuários (em produção seria banco de dados)
USUARIOS = {
    'comercial': {'senha': 'com123', 'nome': 'Equipe Comercial', 'perfil': 'comercial'},
    'marcelao': {'senha': 'log123', 'nome': 'Marcelão', 'perfil': 'logistica'},
    'joao': {'senha': 'campo123', 'nome': 'João Silva', 'perfil': 'campo'},
    'carlos': {'senha': 'campo123', 'nome': 'Carlos Santos', 'perfil': 'campo'},
    'pedro': {'senha': 'campo123', 'nome': 'Pedro Lima', 'perfil': 'campo'},
    'boss': {'senha': 'boss123', 'nome': 'Diretor', 'perfil': 'boss'}
}

# Lista de colaboradores
COLABORADORES = [
    {'nome': 'João Silva', 'funcao': 'Montador Senior', 'disponibilidade': 'Seg-Sex', 'especialidade': 'Estruturas, Palcos', 'status': 'Disponível'},
    {'nome': 'Carlos Santos', 'funcao': 'Técnico Audio/Video', 'disponibilidade': 'Ter-Sab', 'especialidade': 'Som, Iluminação', 'status': 'Ocupado'},
    {'nome': 'Pedro Lima', 'funcao': 'Auxiliar Geral', 'disponibilidade': 'Seg-Dom', 'especialidade': 'Montagem, Transporte', 'status': 'Disponível'},
    {'nome': 'Ana Costa', 'funcao': 'Decoradora', 'disponibilidade': 'Qua-Dom', 'especialidade': 'Decoração, Arranjos', 'status': 'Disponível'},
    {'nome': 'Roberto Alves', 'funcao': 'Motorista', 'disponibilidade': 'Seg-Sex', 'especialidade': 'Transporte, Logística', 'status': 'Disponível'}
]

# Etapas obrigatórias da equipe de campo
ETAPAS_CAMPO = [
    {'id': 1, 'titulo': '🚛 Check-in Chegada', 'descricao': 'Registrar chegada no local com GPS e foto', 'obrigatorio': ['gps', 'foto']},
    {'id': 2, 'titulo': '📦 Conferência Material', 'descricao': 'Verificar todos os equipamentos com checklist', 'obrigatorio': ['checklist', 'foto']},
    {'id': 3, 'titulo': '🔧 Início Montagem', 'descricao': 'Registrar início da montagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 4, 'titulo': '✅ Montagem Concluída', 'descricao': 'Finalizar montagem com assinatura do cliente', 'obrigatorio': ['foto', 'assinatura']},
    {'id': 5, 'titulo': '📤 Início Desmontagem', 'descricao': 'Registrar início da desmontagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 6, 'titulo': '🚚 Material Recolhido', 'descricao': 'Conferir recolhimento com checklist', 'obrigatorio': ['checklist', 'foto']},
    {'id': 7, 'titulo': '🏁 Check-out Saída', 'descricao': 'Registrar saída com GPS e relatório final', 'obrigatorio': ['gps', 'relatorio']}
]

# Documentos da logística
DOCUMENTOS_LOGISTICA = ["Ordem de Separação", "Confirmação de Reserva", "Romaneio de Entrega", "Termo de Recebimento", "Ordem de Recolhimento", "Relatório de Inspeção"]

# Tipos de tarefas de galpão
TIPOS_TAREFA_GALPAO = ["🧹 Limpeza Geral", "📦 Organização de Estoque", "🔧 Manutenção de Equipamentos", "📋 Inventário", "🚛 Organização de Veículos", "⚡ Verificação Elétrica", "🏗️ Manutenção Estrutural"]

# Função para carregar produtos da planilha
@st.cache_data(ttl=300)
def carregar_produtos_sheets():
    """Carrega produtos da planilha Google Sheets"""
    try:
        sheet_id = "1pxBGsaeCuWR_4bdD2_mWBLyxRUqGSJlztH0wnFAtNaw"
        gid = "1527827989"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        df = pd.read_csv(url)
        df.columns = ['produto', 'unidades', 'valor_diaria', 'categoria']
        df = df.dropna(subset=['produto'])
        df['valor_diaria'] = pd.to_numeric(df['valor_diaria'], errors='coerce').fillna(0)
        df['unidades'] = pd.to_numeric(df['unidades'], errors='coerce').fillna(0)
        df['categoria'] = df['categoria'].fillna('outros')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

# Dados de pedidos com classificação automática
@st.cache_data(ttl=600)
def gerar_dados_pedidos():
    """Dados de pedidos com classificação automática"""
    pedidos = [
        {
            'numero_pedido': 'PED001',
            'cliente': 'Caixa Econômica Federal',
            'categoria': 'Público Extra',
            'produto_servico': 'Stand Octanorme, Banqueta, Púlpito',
            'valor': 1850.0,
            'custos': 1200.0,
            'local': 'Hotel Ramada',
            'data_entrega': '2024-12-15',
            'data_criacao': '2024-12-14 15:30:00',
            'status': 'Finalizado',
            'status_logistica': 'Docs Completos',
            'status_campo': 'Concluído',
            'regime_pagamento': 'Padrão',
            'equipe_alocada': ['João Silva', 'Pedro Lima'],
            'urgencia': False,
            'weekend': False
        },
        {
            'numero_pedido': 'PED002',
            'cliente': 'Sec. da Mulher',
            'categoria': 'Público Extra',
            'produto_servico': 'Palco Tablado 6x3, Brinquedo Inflável',
            'valor': 4560.0,
            'custos': 2800.0,
            'local': 'Torre de TV',
            'data_entrega': '2024-12-20',
            'data_criacao': '2024-12-20 08:00:00',
            'status': 'Confirmado',
            'status_logistica': 'Enviado Campo',
            'status_campo': 'Em Andamento',
            'regime_pagamento': '1%',
            'equipe_alocada': ['Carlos Santos', 'Ana Costa'],
            'urgencia': True,
            'weekend': False
        },
        {
            'numero_pedido': 'PED003',
            'cliente': 'Programa Sempre por Elas',
            'categoria': 'Público Extra',
            'produto_servico': 'Carrinho de Pipoca, Monitor/TV',
            'valor': 9080.0,
            'custos': 5500.0,
            'local': 'Curralinho',
            'data_entrega': '2025-01-11',
            'data_criacao': '2025-01-10 16:00:00',
            'status': 'Confirmado',
            'status_logistica': 'Pendente Docs',
            'status_campo': 'Pendente',
            'regime_pagamento': '3%',
            'equipe_alocada': ['João Silva', 'Roberto Alves'],
            'urgencia': False,
            'weekend': True
        }
    ]
    return pd.DataFrame(pedidos)

# Função de login
def fazer_login(usuario, senha):
    """Valida login e retorna dados do usuário"""
    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        return USUARIOS[usuario]
    return None

# Função para classificar regime automaticamente
def classificar_regime_automatico(data_criacao, data_entrega):
    """Classifica regime de pagamento automaticamente"""
    try:
        dt_criacao = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
        dt_entrega = datetime.strptime(data_entrega, '%Y-%m-%d')
        
        # Verifica se é final de semana (sábado=5, domingo=6)
        if dt_entrega.weekday() >= 5:
            return '3%', True, False
        
        # Verifica se é mesmo dia
        if dt_criacao.date() == dt_entrega.date():
            return '1%', False, True
        
        # Verifica se foi criado até 22h do dia anterior
        limite_22h = dt_entrega.replace(hour=22, minute=0, second=0) - timedelta(days=1)
        if dt_criacao <= limite_22h:
            return 'Padrão', False, False
        else:
            return '1%', False, True
            
    except:
        return 'Padrão', False, False

# Função para obter progresso das etapas
def obter_progresso_etapas(numero_pedido):
    """Obtém o progresso das etapas de um pedido"""
    if f'etapas_{numero_pedido}' not in st.session_state:
        st.session_state[f'etapas_{numero_pedido}'] = {
            'etapa_atual': 1,
            'etapas_concluidas': [],
            'dados_etapas': {}
        }
    return st.session_state[f'etapas_{numero_pedido}']

# Função para avançar etapa
def avancar_etapa(numero_pedido, etapa_id, dados_etapa):
    """Avança para próxima etapa após validação"""
    progresso = obter_progresso_etapas(numero_pedido)
    
    # Salvar dados da etapa
    progresso['dados_etapas'][etapa_id] = dados_etapa
    progresso['etapas_concluidas'].append(etapa_id)
    
    # Avançar para próxima etapa
    if etapa_id < 7:
        progresso['etapa_atual'] = etapa_id + 1
    else:
        progresso['etapa_atual'] = 'finalizado'
    
    st.session_state[f'etapas_{numero_pedido}'] = progresso

# Função para gerar documento PDF
def gerar_documento_logistica(tipo_documento, dados_pedido, dados_logistica):
    """Gera documentos da logística em PDF"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Cabeçalho
    cor_azul = HexColor('#1E3A8A')
    cor_dourado = HexColor('#D4AF37')
    
    c.setFillColor(cor_azul)
    c.rect(0, height - 80, width, 80, fill=1)
    
    c.setFillColor(cor_dourado)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 40, "PRIMEIRA LINHA EVENTOS")
    
    c.setFillColor('white')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 60, tipo_documento.upper())
    
    # Conteúdo específico
    y_position = height - 120
    c.setFillColor('black')
    
    if tipo_documento == "Ordem de Separação":
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, f"ORDEM DE SEPARAÇÃO - {dados_pedido['numero_pedido']}")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Cliente: {dados_pedido['cliente']}")
        y_position -= 20
        c.drawString(50, y_position, f"Local: {dados_pedido['local']}")
        y_position -= 20
        c.drawString(50, y_position, f"Regime: {dados_pedido.get('regime_pagamento', 'Padrão')}")
        y_position -= 20
        
        # Equipe alocada
        equipe = dados_pedido.get('equipe_alocada', [])
        if equipe:
            c.drawString(50, y_position, f"Equipe: {', '.join(equipe)}")
            y_position -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "EQUIPAMENTOS A SEPARAR:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        produtos = dados_pedido['produto_servico'].split(', ')
        for produto in produtos:
            c.drawString(70, y_position, f"• {produto}")
            y_position -= 15
    
    # Rodapé
    c.setFillColor(cor_azul)
    c.rect(0, 0, width, 60, fill=1)
    
    c.setFillColor('white')
    c.setFont("Helvetica", 9)
    c.drawString(50, 35, "Primeira Linha Eventos - Sistema Unificado PWA")
    c.drawString(50, 25, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    c.drawString(50, 15, "primeiralinhaeventos@gmail.com | (61) 991334258")
    
    c.save()
    buffer.seek(0)
    return buffer

# Função principal
def main():
    # Inicializar session state
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if 'novos_pedidos' not in st.session_state:
        st.session_state.novos_pedidos = []
    
    if 'tarefas_galpao' not in st.session_state:
        st.session_state.tarefas_galpao = [
            {
                'id': 'TG001',
                'titulo': 'Limpeza Geral Semanal',
                'tipo': '🧹 Limpeza Geral',
                'descricao': 'Limpeza completa do galpão',
                'responsavel': 'Pedro Lima',
                'data_criacao': '2025-01-05',
                'data_prazo': '2025-01-07',
                'status': 'Em Andamento',
                'prioridade': 'Normal'
            }
        ]
    
    # Tela de Login
    if not st.session_state.usuario_logado:
        st.markdown("""
        <div class="main-header">
            <h1>🎪 PRIMEIRA LINHA EVENTOS</h1>
            <h3>Sistema Unificado PWA v1.0</h3>
            <p>4 Interfaces em 1 Aplicativo</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-container">
            <h2>🔐 Login no Sistema</h2>
            <p>Selecione seu perfil e faça login</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards de perfil
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="profile-card profile-comercial">
                <h3>🏢 COMERCIAL</h3>
                <p>Vendas e Orçamentos</p>
                <small>Login: comercial | Senha: com123</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="profile-card profile-logistica">
                <h3>🚚 LOGÍSTICA</h3>
                <p>Marcelão - Gestão Completa</p>
                <small>Login: marcelao | Senha: log123</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="profile-card profile-campo">
                <h3>👷 EQUIPE DE CAMPO</h3>
                <p>João, Carlos, Pedro</p>
                <small>Login: joao/carlos/pedro | Senha: campo123</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="profile-card profile-boss">
                <h3>📊 DIRETOR</h3>
                <p>Dashboard Executivo</p>
                <small>Login: boss | Senha: boss123</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                usuario = st.text_input("👤 Usuário")
            
            with col2:
                senha = st.text_input("🔒 Senha", type="password")
            
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                dados_usuario = fazer_login(usuario, senha)
                if dados_usuario:
                    st.session_state.usuario_logado = dados_usuario
                    st.success(f"✅ Bem-vindo, {dados_usuario['nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
        
        return
    
    # Interface após login
    usuario = st.session_state.usuario_logado
    perfil = usuario['perfil']
    
    # Header personalizado por perfil
    perfil_config = {
        'comercial': {'icon': '🏢', 'color': '#10b981', 'title': 'COMERCIAL'},
        'logistica': {'icon': '🚚', 'color': '#f59e0b', 'title': 'LOGÍSTICA'},
        'campo': {'icon': '👷', 'color': '#3b82f6', 'title': 'EQUIPE DE CAMPO'},
        'boss': {'icon': '📊', 'color': '#8b5cf6', 'title': 'DIRETOR'}
    }
    
    config = perfil_config[perfil]
    
    st.markdown(f"""
    <div class="main-header">
        <h1>{config['icon']} {config['title']} - PRIMEIRA LINHA EVENTOS</h1>
        <h3>Bem-vindo, {usuario['nome']}!</h3>
        <p>Sistema Unificado PWA - Interface {config['title'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown(f"### {config['icon']} {usuario['nome']}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.usuario_logado = None
        st.rerun()
    
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    df_produtos = carregar_produtos_sheets()
    df_pedidos = gerar_dados_pedidos()
    
    # Combinar pedidos
    todos_pedidos = df_pedidos.copy()
    if st.session_state.novos_pedidos:
        novos_df = pd.DataFrame(st.session_state.novos_pedidos)
        todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
    
    # Interface específica por perfil
    if perfil == 'comercial':
        # INTERFACE COMERCIAL
        st.sidebar.markdown("### 🎯 Menu Comercial")
        
        if st.sidebar.button("📝 NOVO PEDIDO", use_container_width=True):
            st.session_state.show_novo_pedido = True
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "📊 Dashboard Comercial",
            "📦 Gestão de Pedidos", 
            "🎯 Gerador de Orçamentos",
            "🛠️ Catálogo de Produtos",
            "💬 Chat da Equipe"
        ])
        
        # Formulário novo pedido
        if st.session_state.get('show_novo_pedido', False):
            st.markdown("### ➕ Novo Pedido")
            
            with st.form("novo_pedido"):
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente = st.text_input("Cliente*")
                    categoria = st.selectbox("Categoria*", ["Público Extra", "Corporativo", "Particular"])
                    produtos_selecionados = st.multiselect("Produtos*", df_produtos['produto'].tolist() if not df_produtos.empty else [])
                    valor = st.number_input("Valor (R$)*", min_value=0.0)
                    
                    # Classificação automática baseada na data
                    data_entrega = st.date_input("Data Entrega*")
                    data_criacao_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    regime_auto, weekend, urgencia = classificar_regime_automatico(data_criacao_str, data_entrega.strftime('%Y-%m-%d'))
                    
                    st.info(f"💰 Regime automático: **{regime_auto}** {'(Weekend)' if weekend else '(Urgente)' if urgencia else '(Padrão)'}")
                    regime = st.selectbox("Regime de Pagamento*", ["Padrão", "1%", "3%"], index=["Padrão", "1%", "3%"].index(regime_auto))
                
                with col2:
                    custos = st.number_input("Custos (R$)", min_value=0.0)
                    local = st.text_input("Local*")
                    status = st.selectbox("Status", ["Em Negociação", "Confirmado", "Finalizado"])
                    equipe = st.selectbox("Equipe Responsável", [c['nome'] for c in COLABORADORES])
                    observacoes = st.text_area("Observações")
                
                if st.form_submit_button("💾 Salvar Pedido"):
                    if cliente and categoria and produtos_selecionados and valor > 0 and local:
                        novo_numero = f"PED{len(todos_pedidos) + 1:03d}"
                        
                        novo_pedido = {
                            'numero_pedido': novo_numero,
                            'cliente': cliente,
                            'categoria': categoria,
                            'produto_servico': ', '.join(produtos_selecionados),
                            'valor': valor,
                            'custos': custos,
                            'local': local,
                            'data_entrega': data_entrega.strftime('%Y-%m-%d'),
                            'data_criacao': data_criacao_str,
                            'status': status,
                            'status_logistica': 'Pendente Docs',
                            'status_campo': 'Pendente',
                            'regime_pagamento': regime,
                            'equipe_alocada': [equipe],
                            'urgencia': urgencia,
                            'weekend': weekend
                        }
                        
                        st.session_state.novos_pedidos.append(novo_pedido)
                        st.success(f"✅ Pedido {novo_numero} criado com sucesso!")
                        st.session_state.show_novo_pedido = False
                        st.rerun()
                    else:
                        st.error("❌ Preencha todos os campos obrigatórios")
            
            if st.button("❌ Fechar"):
                st.session_state.show_novo_pedido = False
                st.rerun()
            
            st.divider()
        
        # Módulos do comercial
        if opcao == "📊 Dashboard Comercial":
            st.markdown("### 📊 Dashboard Comercial")
            
            if not todos_pedidos.empty:
                # KPIs Comerciais
                col1, col2, col3, col4, col5 = st.columns(5)
                
                receita_total = todos_pedidos['valor'].sum()
                custos_totais = todos_pedidos['custos'].sum()
                lucro_total = receita_total - custos_totais
                margem = (lucro_total / receita_total * 100) if receita_total > 0 else 0
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card green">
                        <h4>💰 Receita Total</h4>
                        <h2>R$ {receita_total:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card blue">
                        <h4>📈 Lucro Total</h4>
                        <h2>R$ {lucro_total:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card purple">
                        <h4>📊 Margem</h4>
                        <h2>{margem:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card orange">
                        <h4>📦 Total Pedidos</h4>
                        <h2>{len(todos_pedidos)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    ticket_medio = receita_total / len(todos_pedidos) if len(todos_pedidos) > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>🎯 Ticket Médio</h4>
                        <h2>R$ {ticket_medio:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráficos
                col1, col2 = st.columns(2)
                
                with col1:
                    # Receita por categoria
                    receita_categoria = todos_pedidos.groupby('categoria')['valor'].sum().reset_index()
                    fig_categoria = px.pie(
                        receita_categoria,
                        values='valor',
                        names='categoria',
                        title="💰 Receita por Categoria"
                    )
                    fig_categoria.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_categoria, use_container_width=True)
                
                with col2:
                    # Distribuição por regime
                    regime_counts = todos_pedidos['regime_pagamento'].value_counts().reset_index()
                    fig_regime = px.bar(
                        regime_counts,
                        x='regime_pagamento',
                        y='count',
                        title="💎 Distribuição por Regime",
                        color='count',
                        color_continuous_scale=['#1e3a8a', '#D4AF37']
                    )
                    fig_regime.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_regime, use_container_width=True)
        
        elif opcao == "📦 Gestão de Pedidos":
            st.markdown("### 📦 Gestão de Pedidos")
            
            if not todos_pedidos.empty:
                st.markdown(f"**📊 Total:** {len(todos_pedidos)} pedidos")
                
                # Lista de pedidos
                for i, (idx, pedido) in enumerate(todos_pedidos.iterrows()):
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{pedido['numero_pedido']}** - {pedido['cliente']}")
                        st.markdown(f"📍 {pedido['local']}")
                    
                    with col2:
                        st.markdown(f"💰 R$ {pedido['valor']:,.2f}")
                        st.markdown(f"📅 {pedido['data_entrega']}")
                    
                    with col3:
                        regime = pedido.get('regime_pagamento', 'Padrão')
                        if regime == '3%':
                            st.markdown("💎 3%")
                        elif regime == '1%':
                            st.markdown("🥈 1%")
                        else:
                            st.markdown("⚪ Padrão")
                    
                    with col4:
                        status = pedido.get('status', 'Pendente')
                        if status == 'Finalizado':
                            st.markdown("✅ Finalizado")
                        elif status == 'Confirmado':
                            st.markdown("🔄 Confirmado")
                        else:
                            st.markdown("⏳ Negociação")
                    
                    with col5:
                        if st.button("✏️ Editar", key=f"edit_{pedido['numero_pedido']}"):
                            st.info(f"Editar {pedido['numero_pedido']}")
                    
                    st.divider()
            else:
                st.info("📦 Nenhum pedido encontrado")
        
        elif opcao == "🎯 Gerador de Orçamentos":
            st.markdown("### 🎯 Gerador de Orçamentos")
            st.info("💡 Módulo de orçamentos - Funcionalidade mantida do sistema anterior")
        
        elif opcao == "🛠️ Catálogo de Produtos":
            st.markdown("### 🛠️ Catálogo de Produtos")
            
            if not df_produtos.empty:
                st.markdown(f"**📊 Total:** {len(df_produtos)} produtos")
                
                # Filtros
                col1, col2 = st.columns(2)
                
                with col1:
                    categoria_filtro = st.selectbox("Categoria:", ["Todas"] + list(df_produtos['categoria'].unique()))
                
                with col2:
                    busca = st.text_input("🔍 Buscar produto:")
                
                # Aplicar filtros
                df_filtrado = df_produtos.copy()
                
                if categoria_filtro != "Todas":
                    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
                
                if busca:
                    df_filtrado = df_filtrado[df_filtrado['produto'].str.contains(busca, case=False, na=False)]
                
                # Mostrar produtos
                for i in range(0, len(df_filtrado), 3):
                    cols = st.columns(3)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(df_filtrado):
                            produto = df_filtrado.iloc[i + j]
                            
                            with col:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h5>{produto['produto']}</h5>
                                    <p><strong>Categoria:</strong> {produto['categoria']}</p>
                                    <p><strong>Unidades:</strong> {produto['unidades']}</p>
                                    <p><strong>Valor/Diária:</strong> R$ {produto['valor_diaria']:,.2f}</p>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.error("❌ Erro ao carregar catálogo")
        
        elif opcao == "💬 Chat da Equipe":
            st.markdown("### 💬 Chat da Equipe")
            
            # Chat comercial
            canal = "comercial_geral"
            
            if f'chat_{canal}' not in st.session_state:
                st.session_state[f'chat_{canal}'] = [
                    {
                        'usuario': 'Sistema',
                        'mensagem': 'Chat comercial iniciado',
                        'timestamp': datetime.now().isoformat(),
                        'tipo': 'sistema'
                    }
                ]
            
            # Mostrar mensagens
            chat_messages = st.session_state[f'chat_{canal}']
            
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in chat_messages[-15:]:
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
                
                st.markdown(f"""
                <div class="chat-message">
                    <strong>{msg['usuario']}</strong> <small>{timestamp}</small><br>
                    {msg['mensagem']}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Campo para nova mensagem
            with st.form("chat_form_comercial"):
                nova_mensagem = st.text_input("💬 Digite sua mensagem:")
                if st.form_submit_button("📤 Enviar"):
                    if nova_mensagem:
                        chat_messages.append({
                            'usuario': 'Comercial',
                            'mensagem': nova_mensagem,
                            'timestamp': datetime.now().isoformat(),
                            'tipo': 'comercial'
                        })
                        st.session_state[f'chat_{canal}'] = chat_messages
                        st.rerun()
    
    elif perfil == 'logistica':
        # INTERFACE LOGÍSTICA (usar código do app dedicado)
        st.sidebar.markdown("### 🚚 Menu Logística")
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "📊 Dashboard Logístico",
            "📦 Gestão de Pedidos", 
            "👥 Gestão de Equipes",
            "🧹 Tarefas de Galpão",
            "📄 Documentos",
            "💬 Chat Integrado"
        ])
        
        # Implementar módulos da logística (código similar ao app dedicado)
        if opcao == "📊 Dashboard Logístico":
            st.markdown("### 📊 Dashboard Logístico")
            
            if not todos_pedidos.empty:
                # KPIs Logísticos
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_pedidos = len(todos_pedidos)
                pendentes_docs = len(todos_pedidos[todos_pedidos['status_logistica'] == 'Pendente Docs'])
                urgentes = len(todos_pedidos[todos_pedidos.get('urgencia', False) == True])
                weekend = len(todos_pedidos[todos_pedidos.get('weekend', False) == True])
                equipes_ativas = len([c for c in COLABORADORES if c['status'] == 'Ocupado'])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📦 Total Pedidos</h4>
                        <h2>{total_pedidos}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card orange">
                        <h4>📋 Pendentes Docs</h4>
                        <h2>{pendentes_docs}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card red">
                        <h4>🚨 Urgentes (1%)</h4>
                        <h2>{urgentes}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card purple">
                        <h4>🌅 Weekend (3%)</h4>
                        <h2>{weekend}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                    <div class="metric-card green">
                        <h4>👥 Equipes Ativas</h4>
                        <h2>{equipes_ativas}/5</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Alertas
                if pendentes_docs > 0:
                    st.markdown(f"""
                    <div class="warning-box">
                        ⚠️ <strong>{pendentes_docs} pedido(s) pendente(s) de documentação!</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                if urgentes > 0:
                    st.markdown(f"""
                    <div class="notification-box">
                        🚨 <strong>{urgentes} pedido(s) urgente(s) (mesmo dia)!</strong>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif opcao == "🧹 Tarefas de Galpão":
            st.markdown("### 🧹 Tarefas de Galpão")
            
            # Dashboard de tarefas
            tarefas = st.session_state.tarefas_galpao
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_tarefas = len(tarefas)
            pendentes = len([t for t in tarefas if t['status'] == 'Pendente'])
            andamento = len([t for t in tarefas if t['status'] == 'Em Andamento'])
            concluidas = len([t for t in tarefas if t['status'] == 'Concluída'])
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📋 Total</h4>
                    <h2>{total_tarefas}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card orange">
                    <h4>⏳ Pendentes</h4>
                    <h2>{pendentes}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card blue">
                    <h4>🔄 Andamento</h4>
                    <h2>{andamento}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card green">
                    <h4>✅ Concluídas</h4>
                    <h2>{concluidas}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Formulário para nova tarefa
            st.markdown("#### ➕ Criar Nova Tarefa")
            
            with st.form("nova_tarefa_galpao"):
                col1, col2 = st.columns(2)
                
                with col1:
                    titulo = st.text_input("Título da Tarefa*")
                    tipo = st.selectbox("Tipo de Tarefa*", TIPOS_TAREFA_GALPAO)
                    descricao = st.text_area("Descrição*")
                
                with col2:
                    responsavel = st.selectbox("Responsável*", [c['nome'] for c in COLABORADORES])
                    data_prazo = st.date_input("Data Prazo*")
                    prioridade = st.selectbox("Prioridade", ["Normal", "Alta", "Baixa"])
                
                if st.form_submit_button("📝 Criar Tarefa"):
                    if titulo and tipo and descricao and responsavel:
                        novo_id = f"TG{len(st.session_state.tarefas_galpao) + 1:03d}"
                        
                        nova_tarefa = {
                            'id': novo_id,
                            'titulo': titulo,
                            'tipo': tipo,
                            'descricao': descricao,
                            'responsavel': responsavel,
                            'data_criacao': datetime.now().strftime('%Y-%m-%d'),
                            'data_prazo': data_prazo.strftime('%Y-%m-%d'),
                            'status': 'Pendente',
                            'prioridade': prioridade
                        }
                        
                        st.session_state.tarefas_galpao.append(nova_tarefa)
                        st.success(f"✅ Tarefa {novo_id} criada!")
                        
                        st.markdown(f"""
                        <div class="notification-box">
                            📲 <strong>Notificação enviada para:</strong> {responsavel}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.rerun()
                    else:
                        st.error("❌ Preencha todos os campos obrigatórios")
        
        # Outros módulos da logística...
        else:
            st.info(f"💡 Módulo {opcao} - Em desenvolvimento")
    
    elif perfil == 'campo':
        # INTERFACE EQUIPE DE CAMPO (Mobile-First)
        st.sidebar.markdown(f"### 👷 {usuario['nome']}")
        
        # Filtrar pedidos da equipe
        pedidos_equipe = todos_pedidos[todos_pedidos['equipe_alocada'].apply(lambda x: usuario['nome'] in x if isinstance(x, list) else False)]
        
        if not pedidos_equipe.empty:
            # Seletor de trabalho
            trabalhos_opcoes = [f"{row['numero_pedido']} - {row['cliente']}" for _, row in pedidos_equipe.iterrows()]
            trabalho_selecionado = st.selectbox("📋 Selecionar Trabalho:", trabalhos_opcoes)
            
            if trabalho_selecionado:
                numero_pedido = trabalho_selecionado.split(' - ')[0]
                dados_pedido = pedidos_equipe[pedidos_equipe['numero_pedido'] == numero_pedido].iloc[0]
                
                # Card do trabalho
                st.markdown(f"""
                <div class="campo-container">
                    <h4>📦 {dados_pedido['numero_pedido']} - {dados_pedido['cliente']}</h4>
                    <p><strong>📍 Local:</strong> {dados_pedido['local']}</p>
                    <p><strong>📅 Data:</strong> {dados_pedido['data_entrega']}</p>
                    <p><strong>💰 Regime:</strong> {dados_pedido['regime_pagamento']}</p>
                    <p><strong>🛠️ Produtos:</strong> {dados_pedido['produto_servico']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Obter progresso das etapas
                progresso = obter_progresso_etapas(numero_pedido)
                etapa_atual = progresso['etapa_atual']
                etapas_concluidas = progresso['etapas_concluidas']
                
                # Barra de progresso
                if etapa_atual == 'finalizado':
                    progresso_pct = 100
                else:
                    progresso_pct = (len(etapas_concluidas) / 7) * 100
                
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progresso_pct}%"></div>
                </div>
                <p style="text-align: center; margin: 0.5rem 0;">
                    <strong>Progresso: {progresso_pct:.0f}% ({len(etapas_concluidas)}/7 etapas)</strong>
                </p>
                """, unsafe_allow_html=True)
                
                # Mostrar etapas
                st.markdown("#### 📋 Etapas do Trabalho")
                
                for etapa in ETAPAS_CAMPO:
                    etapa_id = etapa['id']
                    
                    # Determinar status da etapa
                    if etapa_id in etapas_concluidas:
                        status_class = "etapa-concluida"
                        status_icon = "✅"
                        disabled = True
                    elif etapa_id == etapa_atual:
                        status_class = "etapa-ativa"
                        status_icon = "🔄"
                        disabled = False
                    else:
                        status_class = "etapa-bloqueada"
                        status_icon = "⏳"
                        disabled = True
                    
                    # Card da etapa
                    st.markdown(f"""
                    <div class="etapa-card {status_class}">
                        <div style="flex: 1;">
                            <h5>{status_icon} {etapa['titulo']}</h5>
                            <p style="margin: 0; opacity: 0.8;">{etapa['descricao']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Formulário da etapa ativa
                    if etapa_id == etapa_atual and not disabled:
                        with st.expander(f"📝 Executar {etapa['titulo']}", expanded=True):
                            with st.form(f"etapa_{etapa_id}_{numero_pedido}"):
                                dados_etapa = {}
                                
                                # Campos específicos por etapa
                                if 'gps' in etapa['obrigatorio']:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        dados_etapa['latitude'] = st.number_input("Latitude", format="%.6f")
                                    with col2:
                                        dados_etapa['longitude'] = st.number_input("Longitude", format="%.6f")
                                
                                if 'foto' in etapa['obrigatorio']:
                                    dados_etapa['foto'] = st.file_uploader(
                                        "📸 Foto Obrigatória", 
                                        type=['jpg', 'jpeg', 'png'],
                                        key=f"foto_{etapa_id}_{numero_pedido}"
                                    )
                                
                                if 'checklist' in etapa['obrigatorio']:
                                    st.markdown("**📋 Checklist de Equipamentos:**")
                                    produtos = dados_pedido['produto_servico'].split(', ')
                                    checklist_items = []
                                    for produto in produtos:
                                        checked = st.checkbox(f"✅ {produto}", key=f"check_{produto}_{etapa_id}_{numero_pedido}")
                                        checklist_items.append({'produto': produto, 'ok': checked})
                                    dados_etapa['checklist'] = checklist_items
                                
                                if 'assinatura' in etapa['obrigatorio']:
                                    dados_etapa['cliente_nome'] = st.text_input("Nome do Cliente/Responsável")
                                    dados_etapa['assinatura_ok'] = st.checkbox("✍️ Cliente assinou o documento")
                                
                                if 'horario' in etapa['obrigatorio']:
                                    dados_etapa['horario'] = st.time_input("⏰ Horário")
                                
                                if 'relatorio' in etapa['obrigatorio']:
                                    dados_etapa['observacoes'] = st.text_area("📝 Observações e Relatório Final")
                                    dados_etapa['problemas'] = st.text_area("⚠️ Problemas Encontrados (se houver)")
                                
                                # Botão para concluir etapa
                                if st.form_submit_button(f"✅ Concluir {etapa['titulo']}", use_container_width=True):
                                    # Validar campos obrigatórios
                                    valido = True
                                    
                                    if 'foto' in etapa['obrigatorio'] and not dados_etapa.get('foto'):
                                        st.error("❌ Foto obrigatória não anexada!")
                                        valido = False
                                    
                                    if 'gps' in etapa['obrigatorio'] and (not dados_etapa.get('latitude') or not dados_etapa.get('longitude')):
                                        st.error("❌ Localização GPS obrigatória!")
                                        valido = False
                                    
                                    if 'checklist' in etapa['obrigatorio']:
                                        todos_ok = all(item['ok'] for item in dados_etapa.get('checklist', []))
                                        if not todos_ok:
                                            st.error("❌ Todos os itens do checklist devem ser marcados!")
                                            valido = False
                                    
                                    if 'assinatura' in etapa['obrigatorio'] and not dados_etapa.get('assinatura_ok'):
                                        st.error("❌ Assinatura do cliente obrigatória!")
                                        valido = False
                                    
                                    if valido:
                                        # Adicionar timestamp
                                        dados_etapa['timestamp'] = datetime.now().isoformat()
                                        dados_etapa['equipe'] = usuario['nome']
                                        
                                        # Avançar etapa
                                        avancar_etapa(numero_pedido, etapa_id, dados_etapa)
                                        
                                        st.success(f"✅ {etapa['titulo']} concluída com sucesso!")
                                        st.balloons()
                                        st.rerun()
                
                # Botão finalizar trabalho (só aparece após todas as etapas)
                if etapa_atual == 'finalizado':
                    st.markdown("""
                    <div class="success-box">
                        🎉 <strong>TRABALHO CONCLUÍDO COM SUCESSO!</strong><br>
                        Todas as etapas foram executadas corretamente.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📤 Enviar Relatório Final", use_container_width=True):
                        st.success("✅ Relatório enviado para a logística!")
                        st.balloons()
                
                # Chat do trabalho
                st.markdown("#### 💬 Chat do Trabalho")
                
                # Inicializar chat
                if f'chat_{numero_pedido}' not in st.session_state:
                    st.session_state[f'chat_{numero_pedido}'] = [
                        {
                            'usuario': 'Sistema',
                            'mensagem': f'Chat iniciado para o trabalho {numero_pedido}',
                            'timestamp': datetime.now().isoformat(),
                            'tipo': 'sistema'
                        }
                    ]
                
                # Mostrar mensagens
                chat_messages = st.session_state[f'chat_{numero_pedido}']
                
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for msg in chat_messages[-10:]:
                    tipo_class = "sent" if msg['usuario'] == usuario['nome'] else ""
                    timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
                    
                    st.markdown(f"""
                    <div class="chat-message {tipo_class}">
                        <strong>{msg['usuario']}</strong> <small>{timestamp}</small><br>
                        {msg['mensagem']}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Campo para nova mensagem
                with st.form(f"chat_form_{numero_pedido}"):
                    nova_mensagem = st.text_input("💬 Digite sua mensagem:", key=f"msg_{numero_pedido}")
                    if st.form_submit_button("📤 Enviar"):
                        if nova_mensagem:
                            chat_messages.append({
                                'usuario': usuario['nome'],
                                'mensagem': nova_mensagem,
                                'timestamp': datetime.now().isoformat(),
                                'tipo': 'equipe'
                            })
                            st.session_state[f'chat_{numero_pedido}'] = chat_messages
                            st.rerun()
        else:
            st.info(f"📋 Nenhum trabalho encontrado para {usuario['nome']}")
    
    elif perfil == 'boss':
        # INTERFACE BOSS (Dashboard Executivo)
        st.sidebar.markdown("### 📊 Menu Executivo")
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "📊 Dashboard Executivo",
            "💰 Análise Financeira", 
            "👥 Performance da Equipe",
            "📈 Relatórios Gerenciais",
            "🎯 KPIs Estratégicos"
        ])
        
        if opcao == "📊 Dashboard Executivo":
            st.markdown("### 📊 Dashboard Executivo - Visão Geral")
            
            if not todos_pedidos.empty:
                # KPIs Executivos
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                receita_total = todos_pedidos['valor'].sum()
                custos_totais = todos_pedidos['custos'].sum()
                lucro_total = receita_total - custos_totais
                margem = (lucro_total / receita_total * 100) if receita_total > 0 else 0
                
                # KPIs por regime
                regime_counts = todos_pedidos['regime_pagamento'].value_counts()
                urgentes = len(todos_pedidos[todos_pedidos.get('urgencia', False) == True])
                weekend = len(todos_pedidos[todos_pedidos.get('weekend', False) == True])
                
                with col1:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>💰 Receita Total</h4>
                        <h2>R$ {receita_total:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>📈 Lucro Total</h4>
                        <h2>R$ {lucro_total:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>📊 Margem</h4>
                        <h2>{margem:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>📦 Pedidos</h4>
                        <h2>{len(todos_pedidos)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>🚨 Urgentes</h4>
                        <h2>{urgentes}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col6:
                    st.markdown(f"""
                    <div class="boss-card">
                        <h4>🌅 Weekend</h4>
                        <h2>{weekend}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráficos executivos
                col1, col2 = st.columns(2)
                
                with col1:
                    # Receita vs Custos
                    fig_financeiro = go.Figure()
                    fig_financeiro.add_trace(go.Bar(name='Receita', x=['Total'], y=[receita_total], marker_color='#10b981'))
                    fig_financeiro.add_trace(go.Bar(name='Custos', x=['Total'], y=[custos_totais], marker_color='#ef4444'))
                    fig_financeiro.add_trace(go.Bar(name='Lucro', x=['Total'], y=[lucro_total], marker_color='#D4AF37'))
                    
                    fig_financeiro.update_layout(
                        title="💰 Análise Financeira",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_financeiro, use_container_width=True)
                
                with col2:
                    # Distribuição por regime (executivo)
                    fig_regime_exec = px.pie(
                        values=regime_counts.values,
                        names=regime_counts.index,
                        title="💎 Distribuição por Regime de Pagamento",
                        color_discrete_map={
                            'Padrão': '#10b981',
                            '1%': '#f59e0b', 
                            '3%': '#8b5cf6'
                        }
                    )
                    fig_regime_exec.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_regime_exec, use_container_width=True)
                
                # Alertas executivos
                st.markdown("#### 🚨 Alertas Executivos")
                
                if urgentes > 0:
                    st.markdown(f"""
                    <div class="warning-box">
                        🚨 <strong>{urgentes} pedido(s) urgente(s)</strong> - Impacto na margem (1%)
                    </div>
                    """, unsafe_allow_html=True)
                
                if weekend > 0:
                    st.markdown(f"""
                    <div class="notification-box">
                        🌅 <strong>{weekend} pedido(s) em final de semana</strong> - Regime especial (3%)
                    </div>
                    """, unsafe_allow_html=True)
                
                # Performance da equipe
                st.markdown("#### 👥 Performance da Equipe")
                
                equipes_disponiveis = len([c for c in COLABORADORES if c['status'] == 'Disponível'])
                equipes_ocupadas = len([c for c in COLABORADORES if c['status'] == 'Ocupado'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card green">
                        <h4>🟢 Disponíveis</h4>
                        <h2>{equipes_disponiveis}/5</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card red">
                        <h4>🔴 Ocupados</h4>
                        <h2>{equipes_ocupadas}/5</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    utilizacao = (equipes_ocupadas / 5 * 100) if 5 > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card blue">
                        <h4>📊 Utilização</h4>
                        <h2>{utilizacao:.0f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.info(f"💡 Módulo {opcao} - Em desenvolvimento")

if __name__ == "__main__":
    main()
