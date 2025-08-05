"""
NEXO - NÚCLEO DE EXCELÊNCIA OPERACIONAL
Sistema Unificado v1.0 - Design Nubank-inspired
4 Interfaces em 1: Comercial | Logística | Campo | Boss
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
import base64

# Configuração da página
st.set_page_config(
    page_title="NEXO - Núcleo de Excelência Operacional",
    page_icon="https://i.imgur.com/J3y2D4z.png", # Favicon da Nexo
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO - NUBANK INSPIRED ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* --- GERAL -- */
    .stApp {
        background-color: #121212; /* Fundo escuro */
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    /* --- HEADER -- */
    .main-header {
        background-color: #1C1C1C;
        padding: 1.5rem 2rem;
        border-radius: 18px;
        border: 1px solid #2A2A2A;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .main-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }

    .main-header p {
        font-size: 1rem;
        color: #A1A1A1;
        margin: 0;
    }

    /* --- LOGIN -- */
    .login-container {
        background-color: #1C1C1C;
        padding: 3rem;
        border-radius: 24px;
        border: 1px solid #2A2A2A;
        text-align: center;
        margin: 2rem auto;
        max-width: 450px;
    }

    .login-container h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .login-container p {
        color: #A1A1A1;
        margin-bottom: 2rem;
    }

    /* --- CARDS -- */
    .metric-card {
        background-color: #1C1C1C;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #2A2A2A;
        color: white;
        text-align: left;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: #FF6B00; /* Laranja Nexo */
        transform: translateY(-3px);
    }

    .metric-card h4 {
        font-size: 0.9rem;
        font-weight: 500;
        color: #A1A1A1;
        margin-bottom: 0.5rem;
    }

    .metric-card h2 {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* --- BOTÕES -- */
    .stButton > button {
        background-color: #FF6B00; /* Laranja Nexo */
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #E66000;
        transform: scale(1.03);
    }

    /* --- SIDEBAR -- */
    [data-testid="stSidebar"] {
        background-color: #1C1C1C;
        border-right: 1px solid #2A2A2A;
    }

    /* --- TABS -- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #A1A1A1;
        padding: 0 1rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2A2A2A;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2A2A2A;
        color: #FFFFFF;
        font-weight: 600;
    }

    /* --- CAMPO -- */
    .etapa-card {
        background-color: #1C1C1C;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #2A2A2A;
        margin-bottom: 1rem;
        border-left: 4px solid #666;
    }

    .etapa-ativa {
        border-left-color: #FF6B00;
        box-shadow: 0 0 15px rgba(255, 107, 0, 0.3);
    }

    .etapa-concluida {
        border-left-color: #00C853;
        opacity: 0.7;
    }

    .etapa-bloqueada {
        opacity: 0.4;
    }

    /* --- CHAT -- */
    .chat-container {
        background-color: #1C1C1C;
        border-radius: 16px;
        padding: 1rem;
        height: 500px;
        overflow-y: auto;
        border: 1px solid #2A2A2A;
    }

    .chat-message {
        background-color: #2A2A2A;
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        max-width: 70%;
        clear: both;
    }

    .chat-message.sent {
        background-color: #FF6B00;
        color: #FFFFFF;
        float: right;
    }

    .chat-message.received {
        background-color: #333333;
        float: left;
    }

    /* --- GPS -- */
    .gps-button {
        background-color: #333333;
        border: 1px solid #444444;
        color: #FFFFFF;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
    }

</style>
""", unsafe_allow_html=True)

# --- DADOS E FUNÇÕES GLOBAIS ---

# Usuários (em produção, usar banco de dados)
USUARIOS = {
    'comercial': {'senha': 'com123', 'nome': 'Equipe Comercial', 'perfil': 'comercial'},
    'marcelao': {'senha': 'log123', 'nome': 'Marcelão', 'perfil': 'logistica'},
    'joao': {'senha': 'campo123', 'nome': 'João Silva', 'perfil': 'campo'},
    'carlos': {'senha': 'campo123', 'nome': 'Carlos Santos', 'perfil': 'campo'},
    'pedro': {'senha': 'campo123', 'nome': 'Pedro Lima', 'perfil': 'campo'},
    'boss': {'senha': 'boss123', 'nome': 'Diretor', 'perfil': 'boss'}
}

# Colaboradores
COLABORADORES = [
    {'nome': 'João Silva', 'funcao': 'Montador Senior', 'status': 'Disponível'},
    {'nome': 'Carlos Santos', 'funcao': 'Técnico Audio/Video', 'status': 'Ocupado'},
    {'nome': 'Pedro Lima', 'funcao': 'Auxiliar Geral', 'status': 'Disponível'},
    {'nome': 'Ana Costa', 'funcao': 'Decoradora', 'status': 'Disponível'},
    {'nome': 'Roberto Alves', 'funcao': 'Motorista', 'status': 'Disponível'}
]

# Etapas da Equipe de Campo
ETAPAS_CAMPO = [
    {'id': 1, 'titulo': 'Check-in no Local', 'obrigatorio': ['gps', 'foto']},
    {'id': 2, 'titulo': 'Conferência de Material', 'obrigatorio': ['checklist', 'foto']},
    {'id': 3, 'titulo': 'Início da Montagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 4, 'titulo': 'Montagem Concluída', 'obrigatorio': ['foto', 'assinatura']},
    {'id': 5, 'titulo': 'Início da Desmontagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 6, 'titulo': 'Recolhimento de Material', 'obrigatorio': ['checklist', 'foto']},
    {'id': 7, 'titulo': 'Check-out do Local', 'obrigatorio': ['gps', 'relatorio']}
]

# Documentos da Logística
DOCUMENTOS_LOGISTICA = ["Ordem de Separação", "Confirmação de Reserva", "Romaneio de Entrega", "Termo de Recebimento", "Ordem de Recolhimento", "Relatório de Inspeção"]

# Tarefas de Galpão
TIPOS_TAREFA_GALPAO = ["Limpeza Geral", "Organização de Estoque", "Manutenção de Equipamentos", "Inventário"]

# Função para carregar produtos (simulado)
@st.cache_data(ttl=300)
def carregar_produtos():
    return pd.DataFrame([
        {'produto': 'Stand Octanorme', 'unidades': 10, 'valor_diaria': 250, 'categoria': 'Estruturas'},
        {'produto': 'Palco Tablado 6x3', 'unidades': 5, 'valor_diaria': 800, 'categoria': 'Palcos'},
        {'produto': 'Monitor/TV 50"', 'unidades': 20, 'valor_diaria': 150, 'categoria': 'Audio/Video'}
    ])

# Função para carregar pedidos (simulado)
@st.cache_data(ttl=600)
def carregar_pedidos():
    return pd.DataFrame([
        {'numero_pedido': 'PED001', 'cliente': 'Caixa Econômica', 'valor': 1850.0, 'data_entrega': '2024-12-15', 'data_criacao': '2024-12-14 15:30:00', 'status': 'Finalizado', 'status_logistica': 'Docs Completos', 'status_campo': 'Concluído', 'equipe_alocada': ['João Silva'], 'regime_pagamento': 'Padrão'},
        {'numero_pedido': 'PED002', 'cliente': 'Sec. da Mulher', 'valor': 4560.0, 'data_entrega': '2024-12-20', 'data_criacao': '2024-12-20 08:00:00', 'status': 'Confirmado', 'status_logistica': 'Enviado Campo', 'status_campo': 'Em Andamento', 'equipe_alocada': ['Carlos Santos'], 'regime_pagamento': '1%'},
        {'numero_pedido': 'PED003', 'cliente': 'Sempre por Elas', 'valor': 9080.0, 'data_entrega': '2025-01-11', 'data_criacao': '2025-01-10 16:00:00', 'status': 'Confirmado', 'status_logistica': 'Pendente Docs', 'status_campo': 'Pendente', 'equipe_alocada': [], 'regime_pagamento': '3%'}
    ])

# Função de login
def fazer_login(usuario, senha):
    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        return USUARIOS[usuario]
    return None

# Função para obter logo em base64
@st.cache_data
def get_base64_logo(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# --- COMPONENTES DE UI ---

def ui_header(usuario):
    perfil_config = {
        'comercial': {'icon': '🛒', 'title': 'Comercial'},
        'logistica': {'icon': '🚚', 'title': 'Logística'},
        'campo': {'icon': '👷', 'title': 'Equipe de Campo'},
        'boss': {'icon': '📊', 'title': 'Diretoria'}
    }
    config = perfil_config[usuario['perfil']]
    
    # Carregar logo
    # logo_base64 = get_base64_logo("nexo_logo.png") # Assumindo que a logo está no mesmo diretório
    # st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="100">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="main-header">
        <div>
            <h1>NEXO</h1>
            <p>Núcleo de Excelência Operacional</p>
        </div>
        <div>
            <p style="text-align: right;"><strong>{config['title']}</strong></p>
            <p style="text-align: right;">{usuario['nome']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def ui_login():
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem;">
        <h1>Bem-vindo ao NEXO</h1>
        <p style="color: #A1A1A1;">Núcleo de Excelência Operacional</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="login-container">
            <h2>Acesse sua conta</h2>
            <p>Use suas credenciais para entrar no sistema.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="ex: marcelao")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            
            if st.form_submit_button("Entrar no NEXO"):
                dados_usuario = fazer_login(usuario, senha)
                if dados_usuario:
                    st.session_state.usuario_logado = dados_usuario
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# --- INTERFACES POR PERFIL ---

def interface_comercial():
    st.sidebar.title("Menu Comercial")
    abas = ["Dashboard", "Pedidos", "Orçamentos", "Catálogo", "Chat"]
    icones = ["📊", "📦", "🎯", "🛠️", "💬"]
    
    selecao = st.sidebar.radio("Navegação", abas, format_func=lambda x: f"{icones[abas.index(x)]} {x}")

    if selecao == "Dashboard":
        st.header("Dashboard Comercial")
        st.info("KPIs de vendas, metas e performance.")
    elif selecao == "Pedidos":
        st.header("Gestão de Pedidos")
        st.info("Criação, edição e acompanhamento de pedidos.")
    # ... outras abas

def interface_logistica():
    st.sidebar.title("Menu Logística")
    abas = ["Dashboard", "Pedidos", "Equipes", "Galpão", "Chat"]
    icones = ["📊", "📦", "👥", "🧹", "💬"]
    
    selecao = st.sidebar.radio("Navegação", abas, format_func=lambda x: f"{icones[abas.index(x)]} {x}")

    if selecao == "Dashboard":
        st.header("Dashboard Logístico")
        st.info("Visão geral das operações, alertas e status.")
    elif selecao == "Pedidos":
        st.header("Gestão de Pedidos")
        st.info("Alocação de equipes, gestão de documentos e datas.")
    # ... outras abas

def interface_campo(usuario):
    st.sidebar.title(f"Menu de Campo")
    st.sidebar.markdown(f"**Operador:** {usuario['nome']}")
    
    abas = ["Meus Trabalhos", "Relatórios", "Chat"]
    icones = ["📋", "📸", "💬"]
    
    selecao = st.sidebar.radio("Navegação", abas, format_func=lambda x: f"{icones[abas.index(x)]} {x}")

    if selecao == "Meus Trabalhos":
        st.header("Meus Trabalhos")
        st.info("Lista de trabalhos do dia com etapas obrigatórias.")
    # ... outras abas

def interface_boss():
    st.sidebar.title("Menu Diretoria")
    abas = ["Dashboard Executivo", "Financeiro", "Performance", "Relatórios"]
    icones = ["📊", "💰", "👥", "📈"]
    
    selecao = st.sidebar.radio("Navegação", abas, format_func=lambda x: f"{icones[abas.index(x)]} {x}")

    if selecao == "Dashboard Executivo":
        st.header("Dashboard Executivo")
        st.info("KPIs estratégicos e visão geral da empresa.")
    # ... outras abas

# --- FUNÇÃO PRINCIPAL ---

def main():
    # Inicializar session state
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None

    # Roteamento de interface
    if not st.session_state.usuario_logado:
        ui_login()
    else:
        usuario = st.session_state.usuario_logado
        ui_header(usuario)
        
        if st.sidebar.button("Sair do NEXO"):
            st.session_state.usuario_logado = None
            st.rerun()
        
        st.sidebar.divider()

        perfil = usuario['perfil']
        if perfil == 'comercial':
            interface_comercial()
        elif perfil == 'logistica':
            interface_logistica()
        elif perfil == 'campo':
            interface_campo(usuario)
        elif perfil == 'boss':
            interface_boss()

if __name__ == "__main__":
    main()


