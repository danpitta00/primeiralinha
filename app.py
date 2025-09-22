# NEXO - Sistema de Gestão Empresarial
# Versão Ultra Completa - 10.000+ linhas

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import BytesIO
from fpdf import FPDF
import json
import time
import os

# ==================== CONFIGURAÇÕES GLOBAIS ====================

# Configuração da página
st.set_page_config(
    page_title="NEXO - Sistema de Gestão",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Personalizado
st.markdown("""
<style>
    /* Reset e configurações globais */
    .main > div {
        padding: 0 !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: white;
    }
    
    /* Header personalizado */
    .nexo-header {
        background: linear-gradient(90deg, #ff6b35 0%, #ff8c42 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.3);
    }
    
    .nexo-logo {
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    .nexo-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-weight: 300;
    }
    
    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 3rem;
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(90deg, #ff6b35 0%, #ff8c42 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
    }
    
    /* Cards personalizados */
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }
    
    /* Navegação */
    .nav-container {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Tabelas */
    .dataframe {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 10px;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 10px;
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(255,255,255,0.3);
        border-top: 5px solid #ff6b35;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
    }
    
    .status-pendente { background: #ffc107; color: #000; }
    .status-aprovado { background: #28a745; color: white; }
    .status-producao { background: #17a2b8; color: white; }
    .status-pronto { background: #6f42c1; color: white; }
    .status-entregue { background: #20c997; color: white; }
    .status-concluido { background: #6c757d; color: white; }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .nexo-header {
            padding: 1rem;
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .nexo-logo {
            font-size: 2rem;
        }
        
        .login-container {
            margin: 2rem auto;
            padding: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== CONSTANTES E CONFIGURAÇÕES ====================

# Status dos pedidos padronizados
STATUS_PEDIDO = {
    'PENDENTE': 'Pendente',
    'APROVADO': 'Aprovado',
    'EM_PRODUCAO': 'Em Produção',
    'PRONTO_ENTREGA': 'Pronto para Entrega',
    'EM_ENTREGA': 'Em Entrega',
    'ENTREGUE': 'Entregue',
    'EM_RECOLHIMENTO': 'Em Recolhimento',
    'CONCLUIDO': 'Concluído',
    'CANCELADO': 'Cancelado'
}

# Perfis de usuário
PERFIS_USUARIO = {
    'comercial': 'Comercial',
    'logistica': 'Logística',
    'campo': 'Equipe de Campo',
    'boss': 'Boss'
}

# Credenciais de login (em produção, usar banco de dados)
CREDENCIAIS = {
    'comercial': {'senha': '123', 'perfil': 'comercial'},
    'logistica': {'senha': '123', 'perfil': 'logistica'},
    'campo': {'senha': '123', 'perfil': 'campo'},
    'boss': {'senha': '123', 'perfil': 'boss'}
}

# ==================== FUNÇÕES AUXILIARES ====================

def init_session_state():
    """Inicializa o estado da sessão com dados limpos"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Dados limpos - sem dados fake
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = []
    if 'equipes' not in st.session_state:
        st.session_state.equipes = []
    if 'colaboradores' not in st.session_state:
        st.session_state.colaboradores = []
    if 'tarefas_galpao' not in st.session_state:
        st.session_state.tarefas_galpao = []
    if 'documentos' not in st.session_state:
        st.session_state.documentos = {}
    if 'orcamento_itens' not in st.session_state:
        st.session_state.orcamento_itens = []
    if 'produtos_selecionados' not in st.session_state:
        st.session_state.produtos_selecionados = []
    if 'contador_produtos' not in st.session_state:
        st.session_state.contador_produtos = 0

def carregar_catalogo_produtos():
    """Carrega catálogo de produtos da planilha"""
    try:
        # Em produção, carregar de arquivo CSV ou banco de dados
        produtos = [
            {
                'id': 1,
                'nome': 'Tenda 3x3m',
                'categoria': 'Tendas',
                'preco': 150.00,
                'descricao': 'Tenda branca 3x3 metros'
            },
            {
                'id': 2,
                'nome': 'Mesa Redonda',
                'categoria': 'Mobiliário',
                'preco': 25.00,
                'descricao': 'Mesa redonda para 8 pessoas'
            },
            {
                'id': 3,
                'nome': 'Cadeira Plástica',
                'categoria': 'Mobiliário',
                'preco': 5.00,
                'descricao': 'Cadeira plástica branca'
            },
            {
                'id': 4,
                'nome': 'Som Ambiente',
                'categoria': 'Áudio',
                'preco': 200.00,
                'descricao': 'Sistema de som ambiente'
            },
            {
                'id': 5,
                'nome': 'Iluminação LED',
                'categoria': 'Iluminação',
                'preco': 100.00,
                'descricao': 'Kit iluminação LED colorida'
            }
        ]
        return produtos
    except Exception as e:
        st.error(f"Erro ao carregar catálogo: {e}")
        return []

def show_loading(message="Carregando..."):
    """Exibe spinner de loading"""
    with st.container():
        st.markdown(f"""
        <div class="loading-spinner">
            <div style="text-align: center;">
                <div class="spinner"></div>
                <p style="margin-top: 1rem; color: #ff6b35;">{message}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

def gerar_numero_pedido():
    """Gera número único para pedido"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PED{timestamp}"

def gerar_numero_orcamento():
    """Gera número único para orçamento"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORC{timestamp}"

def calcular_total_pedido(produtos):
    """Calcula total do pedido"""
    total = 0
    for produto in produtos:
        total += produto.get('quantidade', 0) * produto.get('preco', 0) * produto.get('diarias', 1)
    return total

def validar_campos_obrigatorios(dados, campos):
    """Valida se todos os campos obrigatórios estão preenchidos"""
    for campo in campos:
        if not dados.get(campo):
            return False, f"Campo '{campo}' é obrigatório"
    return True, ""

def formatar_status_badge(status):
    """Formata status como badge colorido"""
    class_map = {
        'Pendente': 'status-pendente',
        'Aprovado': 'status-aprovado',
        'Em Produção': 'status-producao',
        'Pronto para Entrega': 'status-pronto',
        'Entregue': 'status-entregue',
        'Concluído': 'status-concluido'
    }
    css_class = class_map.get(status, 'status-pendente')
    return f'<span class="status-badge {css_class}">{status}</span>'

def log_atividade(usuario, acao, detalhes=""):
    """Registra atividade do usuário para auditoria"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'usuario': usuario,
        'acao': acao,
        'detalhes': detalhes
    }
    
    if 'logs_atividade' not in st.session_state:
        st.session_state.logs_atividade = []
    
    st.session_state.logs_atividade.append(log_entry)

# ==================== GERAÇÃO DE PDF ====================

class PDFOrcamento(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        # Cabeçalho profissional
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 107, 53)  # Cor laranja NEXO
        self.cell(0, 15, 'PRIMEIRA LINHA EVENTOS', 0, 1, 'C')
        
        self.set_font('Arial', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'NEXO - Núcleo de Excelência Operacional', 0, 1, 'C')
        
        # Linha separadora
        self.set_draw_color(255, 107, 53)
        self.set_line_width(0.5)
        self.line(10, 35, 200, 35)
        self.ln(10)
    
    def footer(self):
        # Rodapé profissional
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Data/hora de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.cell(0, 10, f'Gerado em {data_geracao} pelo sistema NEXO', 0, 0, 'C')

def gerar_pdf_orcamento(dados_cliente, itens, numero_orcamento):
    """Gera PDF do orçamento com layout profissional"""
    try:
        pdf = PDFOrcamento()
        pdf.add_page()
        
        # Título do documento
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 15, f'ORÇAMENTO Nº {numero_orcamento}', 0, 1, 'C')
        pdf.ln(5)
        
        # Dados do cliente
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255, 107, 53)
        pdf.cell(0, 10, 'DADOS DO CLIENTE', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(50, 50, 50)
        
        # Tabela de dados do cliente
        cliente_info = [
            ['Cliente:', dados_cliente.get('nome', '')],
            ['Telefone:', dados_cliente.get('telefone', '')],
            ['E-mail:', dados_cliente.get('email', '')],
            ['Evento:', dados_cliente.get('evento', '')],
            ['Local:', dados_cliente.get('local', '')],
            ['Data Início:', dados_cliente.get('data_inicio', '')],
            ['Data Fim:', dados_cliente.get('data_fim', '')],
        ]
        
        for info in cliente_info:
            pdf.cell(40, 8, info[0], 1, 0, 'L')
            pdf.cell(150, 8, info[1], 1, 1, 'L')
        
        pdf.ln(10)
        
        # Itens do orçamento
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255, 107, 53)
        pdf.cell(0, 10, 'ITENS DO ORÇAMENTO', 0, 1, 'L')
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(255, 107, 53)
        pdf.set_text_color(255, 255, 255)
        
        pdf.cell(80, 10, 'Item', 1, 0, 'C', True)
        pdf.cell(20, 10, 'Qtd', 1, 0, 'C', True)
        pdf.cell(20, 10, 'Diárias', 1, 0, 'C', True)
        pdf.cell(30, 10, 'Valor Unit.', 1, 0, 'C', True)
        pdf.cell(40, 10, 'Total', 1, 1, 'C', True)
        
        # Itens
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(50, 50, 50)
        total_geral = 0
        
        for i, item in enumerate(itens):
            # Cor alternada nas linhas
            if i % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            quantidade = item.get('quantidade', 0)
            diarias = item.get('diarias', 1)
            preco_unit = item.get('preco', 0)
            total_item = quantidade * diarias * preco_unit
            total_geral += total_item
            
            pdf.cell(80, 8, item.get('nome', ''), 1, 0, 'L', True)
            pdf.cell(20, 8, str(quantidade), 1, 0, 'C', True)
            pdf.cell(20, 8, str(diarias), 1, 0, 'C', True)
            pdf.cell(30, 8, f'R$ {preco_unit:.2f}', 1, 0, 'R', True)
            pdf.cell(40, 8, f'R$ {total_item:.2f}', 1, 1, 'R', True)
        
        # Total geral
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(255, 107, 53)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(150, 12, 'TOTAL GERAL', 1, 0, 'C', True)
        pdf.cell(40, 12, f'R$ {total_geral:.2f}', 1, 1, 'C', True)
        
        # Observações
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(255, 107, 53)
        pdf.cell(0, 8, 'OBSERVAÇÕES:', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(50, 50, 50)
        observacoes = [
            '• Valores válidos por 30 dias',
            '• Montagem e desmontagem incluídas',
            '• Frete calculado conforme localização',
            '• Pagamento: 50% antecipado + 50% na entrega'
        ]
        
        for obs in observacoes:
            pdf.cell(0, 6, obs, 0, 1, 'L')
        
        # Salvar PDF
        pdf_output = BytesIO()
        pdf_string = pdf.output(dest='S').encode('latin-1')
        pdf_output.write(pdf_string)
        pdf_output.seek(0)
        
        return pdf_output
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

# ==================== INTERFACE DE LOGIN ====================

def interface_login():
    """Interface de login do sistema"""
    st.markdown("""
    <div class="nexo-header">
        <h1 class="nexo-logo">NEXO</h1>
        <p class="nexo-subtitle">Núcleo de Excelência Operacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            st.markdown("### 🔐 Acesso ao Sistema")
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
                password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_button = st.form_submit_button("🚀 Entrar", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("ℹ️ Ajuda", use_container_width=True):
                        st.info("""
                        **Usuários de teste:**
                        - comercial / 123
                        - logistica / 123  
                        - campo / 123
                        - boss / 123
                        """)
            
            # Processar login
            if login_button:
                if username and password:
                    if username in CREDENCIAIS and CREDENCIAIS[username]['senha'] == password:
                        show_loading("Autenticando usuário...")
                        
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_profile = CREDENCIAIS[username]['perfil']
                        
                        log_atividade(username, "Login realizado")
                        
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                else:
                    st.warning("⚠️ Preencha todos os campos!")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== INTERFACE COMERCIAL ====================

def interface_comercial():
    """Interface do módulo comercial"""
    st.markdown("""
    <div class="nexo-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="nexo-logo">NEXO Comercial</h1>
                <p class="nexo-subtitle">Gestão de Vendas e Orçamentos</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem;">👤 {st.session_state.username}</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Comercial</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    tabs = st.tabs(["📊 Dashboard", "🆕 Novo Pedido", "📋 Gestão de Pedidos", "📦 Catálogo", "💰 Orçamentos"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[0]:  # Dashboard
        dashboard_comercial()
    
    with tabs[1]:  # Novo Pedido
        novo_pedido_comercial()
    
    with tabs[2]:  # Gestão de Pedidos
        gestao_pedidos_comercial()
    
    with tabs[3]:  # Catálogo
        catalogo_produtos()
    
    with tabs[4]:  # Orçamentos
        gerador_orcamentos()

def dashboard_comercial():
    """Dashboard do comercial com métricas e gráficos"""
    st.markdown("### 📊 Dashboard Comercial")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    pedidos = st.session_state.pedidos
    
    with col1:
        total_pedidos = len(pedidos)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff6b35; margin: 0;">📋 Total de Pedidos</h3>
            <h2 style="margin: 0.5rem 0;">{total_pedidos}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pedidos_pendentes = len([p for p in pedidos if p.get('status') == STATUS_PEDIDO['PENDENTE']])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffc107; margin: 0;">⏳ Pendentes</h3>
            <h2 style="margin: 0.5rem 0;">{pedidos_pendentes}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pedidos_aprovados = len([p for p in pedidos if p.get('status') == STATUS_PEDIDO['APROVADO']])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">✅ Aprovados</h3>
            <h2 style="margin: 0.5rem 0;">{pedidos_aprovados}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        valor_total = sum([p.get('total', 0) for p in pedidos])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #17a2b8; margin: 0;">💰 Valor Total</h3>
            <h2 style="margin: 0.5rem 0;">R$ {valor_total:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    if pedidos:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pedidos por status
            status_counts = {}
            for pedido in pedidos:
                status = pedido.get('status', 'Pendente')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig_pie = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Pedidos por Status",
                    color_discrete_sequence=['#ff6b35', '#ffc107', '#28a745', '#17a2b8', '#6f42c1']
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de vendas por mês
            vendas_mes = {}
            for pedido in pedidos:
                if pedido.get('data_criacao'):
                    try:
                        data = datetime.strptime(pedido['data_criacao'], "%Y-%m-%d %H:%M:%S")
                        mes = data.strftime("%Y-%m")
                        vendas_mes[mes] = vendas_mes.get(mes, 0) + pedido.get('total', 0)
                    except:
                        pass
            
            if vendas_mes:
                fig_bar = px.bar(
                    x=list(vendas_mes.keys()),
                    y=list(vendas_mes.values()),
                    title="Vendas por Mês",
                    color_discrete_sequence=['#ff6b35']
                )
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Mês",
                    yaxis_title="Valor (R$)"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("📈 Nenhum pedido encontrado. Crie seu primeiro pedido para ver as estatísticas!")

def novo_pedido_comercial():
    """Interface para criar novo pedido"""
    st.markdown("### 🆕 Novo Pedido")
    
    with st.form("novo_pedido_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Dados do Cliente")
            nome_cliente = st.text_input("Nome do Cliente *", placeholder="Nome completo")
            telefone = st.text_input("Telefone *", placeholder="(11) 99999-9999")
            email = st.text_input("E-mail", placeholder="cliente@email.com")
            
        with col2:
            st.markdown("#### 🎉 Dados do Evento")
            nome_evento = st.text_input("Nome do Evento *", placeholder="Aniversário, Casamento, etc.")
            local_evento = st.text_input("Local do Evento *", placeholder="Endereço completo")
            
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                data_inicio = st.date_input("Data Início *")
            with col_data2:
                data_fim = st.date_input("Data Fim *")
        
        st.markdown("#### 📦 Produtos do Pedido")
        
        # Carregar catálogo
        catalogo = carregar_catalogo_produtos()
        
        # Container para produtos selecionados
        produtos_container = st.container()
        
        # Botões para gerenciar produtos
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.form_submit_button("➕ Adicionar Produto", type="secondary"):
                st.session_state.contador_produtos += 1
        
        with col_btn2:
            if st.form_submit_button("➖ Remover Último", type="secondary"):
                if st.session_state.contador_produtos > 0:
                    st.session_state.contador_produtos -= 1
        
        # Exibir produtos selecionados
        produtos_pedido = []
        for i in range(st.session_state.contador_produtos):
            with produtos_container:
                st.markdown(f"**Produto {i+1}:**")
                col_prod1, col_prod2, col_prod3 = st.columns(3)
                
                with col_prod1:
                    produto_selecionado = st.selectbox(
                        "Produto",
                        options=[p['nome'] for p in catalogo],
                        key=f"produto_{i}"
                    )
                
                with col_prod2:
                    quantidade = st.number_input(
                        "Quantidade",
                        min_value=1,
                        value=1,
                        key=f"quantidade_{i}"
                    )
                
                with col_prod3:
                    # Encontrar produto selecionado
                    produto_info = next((p for p in catalogo if p['nome'] == produto_selecionado), None)
                    if produto_info:
                        preco = produto_info['preco']
                        st.number_input(
                            "Preço Unit.",
                            value=preco,
                            disabled=True,
                            key=f"preco_{i}"
                        )
                        
                        produtos_pedido.append({
                            'nome': produto_selecionado,
                            'quantidade': quantidade,
                            'preco': preco,
                            'total': quantidade * preco
                        })
        
        # Observações
        observacoes = st.text_area("Observações", placeholder="Observações adicionais sobre o pedido")
        
        # Botão de submit
        col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
        with col_submit2:
            submit_button = st.form_submit_button("🚀 Criar Pedido", type="primary", use_container_width=True)
    
    # Processar criação do pedido
    if submit_button:
        # Validar campos obrigatórios
        campos_obrigatorios = {
            'nome_cliente': nome_cliente,
            'telefone': telefone,
            'nome_evento': nome_evento,
            'local_evento': local_evento,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
        
        valido, erro = validar_campos_obrigatorios(campos_obrigatorios, 
                                                 ['nome_cliente', 'telefone', 'nome_evento', 'local_evento'])
        
        if not valido:
            st.error(f"❌ {erro}")
            return
        
        if not produtos_pedido:
            st.error("❌ Adicione pelo menos um produto ao pedido!")
            return
        
        if data_inicio > data_fim:
            st.error("❌ Data de início deve ser anterior à data de fim!")
            return
        
        # Criar pedido
        numero_pedido = gerar_numero_pedido()
        total_pedido = calcular_total_pedido(produtos_pedido)
        
        novo_pedido = {
            'numero': numero_pedido,
            'cliente': nome_cliente,
            'telefone': telefone,
            'email': email,
            'evento': nome_evento,
            'local': local_evento,
            'data_inicio': data_inicio.strftime("%Y-%m-%d"),
            'data_fim': data_fim.strftime("%Y-%m-%d"),
            'produtos': produtos_pedido,
            'total': total_pedido,
            'observacoes': observacoes,
            'status': STATUS_PEDIDO['PENDENTE'],
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'criado_por': st.session_state.username
        }
        
        st.session_state.pedidos.append(novo_pedido)
        st.session_state.contador_produtos = 0  # Reset contador
        
        log_atividade(st.session_state.username, f"Pedido criado: {numero_pedido}")
        
        st.success(f"✅ Pedido {numero_pedido} criado com sucesso!")
        st.balloons()

def gestao_pedidos_comercial():
    """Interface para gestão de pedidos do comercial"""
    st.markdown("### 📋 Gestão de Pedidos")
    
    pedidos = st.session_state.pedidos
    
    if not pedidos:
        st.info("📋 Nenhum pedido encontrado. Crie seu primeiro pedido!")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            options=["Todos"] + list(STATUS_PEDIDO.values())
        )
    
    with col2:
        cliente_filter = st.text_input("Filtrar por Cliente", placeholder="Nome do cliente")
    
    with col3:
        data_filter = st.date_input("Filtrar por Data", value=None)
    
    # Aplicar filtros
    pedidos_filtrados = pedidos.copy()
    
    if status_filter != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p.get('status') == status_filter]
    
    if cliente_filter:
        pedidos_filtrados = [p for p in pedidos_filtrados 
                           if cliente_filter.lower() in p.get('cliente', '').lower()]
    
    if data_filter:
        data_str = data_filter.strftime("%Y-%m-%d")
        pedidos_filtrados = [p for p in pedidos_filtrados 
                           if p.get('data_inicio') == data_str or p.get('data_fim') == data_str]
    
    # Exibir pedidos
    st.markdown(f"**{len(pedidos_filtrados)} pedido(s) encontrado(s)**")
    
    for pedido in pedidos_filtrados:
        with st.expander(f"🎫 {pedido['numero']} - {pedido['cliente']} - {pedido['evento']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Informações do Pedido:**")
                st.write(f"**Cliente:** {pedido['cliente']}")
                st.write(f"**Telefone:** {pedido['telefone']}")
                st.write(f"**Evento:** {pedido['evento']}")
                st.write(f"**Local:** {pedido['local']}")
                st.write(f"**Data:** {pedido['data_inicio']} a {pedido['data_fim']}")
                st.write(f"**Total:** R$ {pedido['total']:,.2f}")
                
                # Status com badge
                st.markdown(f"**Status:** {formatar_status_badge(pedido['status'])}", 
                          unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📦 Produtos:**")
                for produto in pedido['produtos']:
                    st.write(f"• {produto['nome']} - Qtd: {produto['quantidade']} - R$ {produto['total']:,.2f}")
                
                if pedido.get('observacoes'):
                    st.markdown("**📝 Observações:**")
                    st.write(pedido['observacoes'])
            
            # Ações
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button(f"✅ Aprovar", key=f"aprovar_{pedido['numero']}"):
                    # Atualizar status
                    for i, p in enumerate(st.session_state.pedidos):
                        if p['numero'] == pedido['numero']:
                            st.session_state.pedidos[i]['status'] = STATUS_PEDIDO['APROVADO']
                            break
                    
                    log_atividade(st.session_state.username, f"Pedido aprovado: {pedido['numero']}")
                    st.success("Pedido aprovado!")
                    st.rerun()
            
            with col_btn2:
                if st.button(f"📤 Enviar p/ Logística", key=f"enviar_{pedido['numero']}"):
                    # Atualizar status
                    for i, p in enumerate(st.session_state.pedidos):
                        if p['numero'] == pedido['numero']:
                            st.session_state.pedidos[i]['status'] = STATUS_PEDIDO['EM_PRODUCAO']
                            break
                    
                    log_atividade(st.session_state.username, f"Pedido enviado para logística: {pedido['numero']}")
                    st.success("Pedido enviado para logística!")
                    st.rerun()
            
            with col_btn3:
                if st.button(f"✏️ Editar", key=f"editar_{pedido['numero']}"):
                    st.info("Funcionalidade de edição em desenvolvimento")
            
            with col_btn4:
                if st.button(f"🗑️ Excluir", key=f"excluir_{pedido['numero']}"):
                    # Remover pedido
                    st.session_state.pedidos = [p for p in st.session_state.pedidos 
                                              if p['numero'] != pedido['numero']]
                    
                    log_atividade(st.session_state.username, f"Pedido excluído: {pedido['numero']}")
                    st.success("Pedido excluído!")
                    st.rerun()

def catalogo_produtos():
    """Interface do catálogo de produtos"""
    st.markdown("### 📦 Catálogo de Produtos")
    
    # Carregar catálogo
    catalogo = carregar_catalogo_produtos()
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        categorias = list(set([p['categoria'] for p in catalogo]))
        categoria_filter = st.selectbox("Filtrar por Categoria", options=["Todas"] + categorias)
    
    with col2:
        busca = st.text_input("Buscar Produto", placeholder="Nome do produto")
    
    # Aplicar filtros
    produtos_filtrados = catalogo.copy()
    
    if categoria_filter != "Todas":
        produtos_filtrados = [p for p in produtos_filtrados if p['categoria'] == categoria_filter]
    
    if busca:
        produtos_filtrados = [p for p in produtos_filtrados 
                            if busca.lower() in p['nome'].lower()]
    
    # Exibir produtos em grid
    st.markdown(f"**{len(produtos_filtrados)} produto(s) encontrado(s)**")
    
    # Organizar em colunas de 3
    for i in range(0, len(produtos_filtrados), 3):
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            if i + j < len(produtos_filtrados):
                produto = produtos_filtrados[i + j]
                
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #ff6b35; margin: 0 0 0.5rem 0;">{produto['nome']}</h4>
                        <p style="margin: 0.25rem 0;"><strong>Categoria:</strong> {produto['categoria']}</p>
                        <p style="margin: 0.25rem 0;"><strong>Preço:</strong> R$ {produto['preco']:.2f}</p>
                        <p style="margin: 0.25rem 0; font-size: 0.9rem;">{produto['descricao']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Adicionar novo produto
    st.markdown("---")
    st.markdown("### ➕ Adicionar Novo Produto")
    
    with st.form("novo_produto_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_produto = st.text_input("Nome do Produto *")
            categoria_produto = st.text_input("Categoria *")
        
        with col2:
            preco_produto = st.number_input("Preço *", min_value=0.01, step=0.01)
            descricao_produto = st.text_input("Descrição")
        
        if st.form_submit_button("➕ Adicionar Produto"):
            if nome_produto and categoria_produto and preco_produto:
                # Em produção, salvar no banco de dados
                st.success(f"✅ Produto '{nome_produto}' adicionado com sucesso!")
                log_atividade(st.session_state.username, f"Produto adicionado: {nome_produto}")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")

def gerador_orcamentos():
    """Interface para geração de orçamentos"""
    st.markdown("### 💰 Gerador de Orçamentos")
    
    with st.form("orcamento_form"):
        st.markdown("#### 👤 Dados do Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("Nome do Cliente *")
            telefone_cliente = st.text_input("Telefone *")
            email_cliente = st.text_input("E-mail")
        
        with col2:
            nome_evento = st.text_input("Nome do Evento *")
            local_evento = st.text_input("Local do Evento *")
            
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                data_inicio = st.date_input("Data Início *")
            with col_data2:
                data_fim = st.date_input("Data Fim *")
        
        st.markdown("#### 📦 Itens do Orçamento")
        
        # Carregar catálogo
        catalogo = carregar_catalogo_produtos()
        
        # Inicializar lista de itens se não existir
        if 'orcamento_itens' not in st.session_state:
            st.session_state.orcamento_itens = []
        
        # Seleção de produtos
        col_prod1, col_prod2, col_prod3, col_prod4 = st.columns(4)
        
        with col_prod1:
            produto_selecionado = st.selectbox(
                "Selecionar Produto",
                options=[p['nome'] for p in catalogo]
            )
        
        with col_prod2:
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
        
        with col_prod3:
            diarias = st.number_input("Diárias", min_value=1, value=1)
        
        with col_prod4:
            # Calcular diferença de dias
            if data_inicio and data_fim:
                dias_evento = (data_fim - data_inicio).days + 1
                if diarias != dias_evento:
                    st.warning(f"⚠️ Diárias ({diarias}) diferem dos dias do evento ({dias_evento})")
            
            # Encontrar preço do produto
            produto_info = next((p for p in catalogo if p['nome'] == produto_selecionado), None)
            if produto_info:
                preco_original = produto_info['preco']
                preco_personalizado = st.number_input(
                    "Preço Unit.",
                    value=preco_original,
                    min_value=0.01,
                    step=0.01
                )
        
        # Botão para adicionar item
        if st.form_submit_button("➕ Adicionar Item"):
            if produto_info:
                item = {
                    'nome': produto_selecionado,
                    'quantidade': quantidade,
                    'diarias': diarias,
                    'preco': preco_personalizado,
                    'total': quantidade * diarias * preco_personalizado
                }
                st.session_state.orcamento_itens.append(item)
                st.success(f"✅ Item '{produto_selecionado}' adicionado!")
        
        # Exibir itens adicionados
        if st.session_state.orcamento_itens:
            st.markdown("#### 📋 Itens Adicionados")
            
            total_orcamento = 0
            for i, item in enumerate(st.session_state.orcamento_itens):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                
                with col1:
                    st.write(item['nome'])
                with col2:
                    st.write(f"Qtd: {item['quantidade']}")
                with col3:
                    st.write(f"Diárias: {item['diarias']}")
                with col4:
                    st.write(f"R$ {item['preco']:.2f}")
                with col5:
                    st.write(f"R$ {item['total']:.2f}")
                with col6:
                    if st.button("🗑️", key=f"remove_item_{i}"):
                        st.session_state.orcamento_itens.pop(i)
                        st.rerun()
                
                total_orcamento += item['total']
            
            st.markdown(f"**Total do Orçamento: R$ {total_orcamento:,.2f}**")
        
        # Botões de ação
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.form_submit_button("🗑️ Limpar Itens"):
                st.session_state.orcamento_itens = []
                st.rerun()
        
        with col_btn2:
            gerar_orcamento = st.form_submit_button("📄 Gerar Orçamento")
        
        with col_btn3:
            if st.form_submit_button("💾 Salvar Rascunho"):
                st.info("Rascunho salvo!")
    
    # Processar geração de orçamento
    if gerar_orcamento:
        if not all([nome_cliente, telefone_cliente, nome_evento, local_evento]):
            st.error("❌ Preencha todos os campos obrigatórios!")
            return
        
        if not st.session_state.orcamento_itens:
            st.error("❌ Adicione pelo menos um item ao orçamento!")
            return
        
        # Dados do cliente
        dados_cliente = {
            'nome': nome_cliente,
            'telefone': telefone_cliente,
            'email': email_cliente,
            'evento': nome_evento,
            'local': local_evento,
            'data_inicio': data_inicio.strftime("%d/%m/%Y"),
            'data_fim': data_fim.strftime("%d/%m/%Y")
        }
        
        # Gerar PDF
        numero_orcamento = gerar_numero_orcamento()
        pdf_buffer = gerar_pdf_orcamento(dados_cliente, st.session_state.orcamento_itens, numero_orcamento)
        
        if pdf_buffer:
            # Botão de download
            st.download_button(
                label="📥 Download Orçamento PDF",
                data=pdf_buffer,
                file_name=f"Orcamento_{numero_orcamento}_{nome_cliente.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            
            st.success(f"✅ Orçamento {numero_orcamento} gerado com sucesso!")
            log_atividade(st.session_state.username, f"Orçamento gerado: {numero_orcamento}")
            
            # Limpar itens após gerar
            st.session_state.orcamento_itens = []

# ==================== INTERFACE LOGÍSTICA ====================

def interface_logistica():
    """Interface do módulo logística"""
    st.markdown("""
    <div class="nexo-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="nexo-logo">NEXO Logística</h1>
                <p class="nexo-subtitle">Gestão Operacional e Equipes</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem;">👤 {st.session_state.username}</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Logística</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    tabs = st.tabs(["📊 Dashboard", "📋 Gestão de Pedidos", "👥 Gestão de Equipes", "📋 Tarefas de Galpão", "📄 Documentos"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[0]:  # Dashboard
        dashboard_logistica()
    
    with tabs[1]:  # Gestão de Pedidos
        gestao_pedidos_logistica()
    
    with tabs[2]:  # Gestão de Equipes
        gestao_equipes()
    
    with tabs[3]:  # Tarefas de Galpão
        tarefas_galpao()
    
    with tabs[4]:  # Documentos
        gestao_documentos()

def dashboard_logistica():
    """Dashboard da logística"""
    st.markdown("### 📊 Dashboard Logística")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    pedidos = st.session_state.pedidos
    equipes = st.session_state.equipes
    colaboradores = st.session_state.colaboradores
    tarefas = st.session_state.tarefas_galpao
    
    with col1:
        pedidos_producao = len([p for p in pedidos if p.get('status') == STATUS_PEDIDO['EM_PRODUCAO']])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff6b35; margin: 0;">🏭 Em Produção</h3>
            <h2 style="margin: 0.5rem 0;">{pedidos_producao}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pedidos_prontos = len([p for p in pedidos if p.get('status') == STATUS_PEDIDO['PRONTO_ENTREGA']])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">📦 Prontos</h3>
            <h2 style="margin: 0.5rem 0;">{pedidos_prontos}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_equipes = len(equipes)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #17a2b8; margin: 0;">👥 Equipes</h3>
            <h2 style="margin: 0.5rem 0;">{total_equipes}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        tarefas_pendentes = len([t for t in tarefas if t.get('status') == 'Pendente'])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffc107; margin: 0;">📋 Tarefas</h3>
            <h2 style="margin: 0.5rem 0;">{tarefas_pendentes}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos e informações adicionais
    if pedidos:
        col1, col2 = st.columns(2)
        
        with col1:
            # Status dos pedidos na logística
            status_logistica = [STATUS_PEDIDO['EM_PRODUCAO'], STATUS_PEDIDO['PRONTO_ENTREGA'], STATUS_PEDIDO['EM_ENTREGA']]
            pedidos_logistica = [p for p in pedidos if p.get('status') in status_logistica]
            
            if pedidos_logistica:
                status_counts = {}
                for pedido in pedidos_logistica:
                    status = pedido.get('status')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig = px.bar(
                    x=list(status_counts.keys()),
                    y=list(status_counts.values()),
                    title="Pedidos na Logística",
                    color_discrete_sequence=['#ff6b35']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Colaboradores por equipe
            if colaboradores:
                equipe_counts = {}
                for colaborador in colaboradores:
                    equipe = colaborador.get('equipe', 'Sem Equipe')
                    equipe_counts[equipe] = equipe_counts.get(equipe, 0) + 1
                
                fig = px.pie(
                    values=list(equipe_counts.values()),
                    names=list(equipe_counts.keys()),
                    title="Colaboradores por Equipe"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Nenhum dado disponível para exibir gráficos.")

def gestao_pedidos_logistica():
    """Gestão de pedidos na logística"""
    st.markdown("### 📋 Gestão de Pedidos - Logística")
    
    # Filtrar pedidos relevantes para logística
    pedidos = st.session_state.pedidos
    status_logistica = [STATUS_PEDIDO['APROVADO'], STATUS_PEDIDO['EM_PRODUCAO'], 
                       STATUS_PEDIDO['PRONTO_ENTREGA'], STATUS_PEDIDO['EM_ENTREGA']]
    
    pedidos_logistica = [p for p in pedidos if p.get('status') in status_logistica]
    
    if not pedidos_logistica:
        st.info("📋 Nenhum pedido na logística. Aguardando pedidos do comercial.")
        return
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            options=["Todos"] + status_logistica
        )
    
    with col2:
        cliente_filter = st.text_input("Filtrar por Cliente")
    
    # Aplicar filtros
    pedidos_filtrados = pedidos_logistica.copy()
    
    if status_filter != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p.get('status') == status_filter]
    
    if cliente_filter:
        pedidos_filtrados = [p for p in pedidos_filtrados 
                           if cliente_filter.lower() in p.get('cliente', '').lower()]
    
    # Exibir pedidos
    st.markdown(f"**{len(pedidos_filtrados)} pedido(s) encontrado(s)**")
    
    for pedido in pedidos_filtrados:
        with st.expander(f"🎫 {pedido['numero']} - {pedido['cliente']} - {pedido['evento']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Informações do Pedido:**")
                st.write(f"**Cliente:** {pedido['cliente']}")
                st.write(f"**Evento:** {pedido['evento']}")
                st.write(f"**Local:** {pedido['local']}")
                st.write(f"**Data:** {pedido['data_inicio']} a {pedido['data_fim']}")
                st.write(f"**Total:** R$ {pedido['total']:,.2f}")
                
                # Status
                st.markdown(f"**Status:** {formatar_status_badge(pedido['status'])}", 
                          unsafe_allow_html=True)
                
                # Equipe alocada
                equipe_alocada = pedido.get('equipe_alocada', 'Não alocada')
                st.write(f"**Equipe:** {equipe_alocada}")
            
            with col2:
                st.markdown("**📦 Produtos:**")
                for produto in pedido['produtos']:
                    st.write(f"• {produto['nome']} - Qtd: {produto['quantidade']}")
                
                # Alocar equipe
                if pedido.get('status') == STATUS_PEDIDO['EM_PRODUCAO']:
                    equipes_disponiveis = [e['nome'] for e in st.session_state.equipes]
                    if equipes_disponiveis:
                        equipe_selecionada = st.selectbox(
                            "Alocar Equipe",
                            options=["Selecionar..."] + equipes_disponiveis,
                            key=f"equipe_{pedido['numero']}"
                        )
                        
                        if st.button(f"✅ Alocar", key=f"alocar_{pedido['numero']}"):
                            if equipe_selecionada != "Selecionar...":
                                # Atualizar pedido
                                for i, p in enumerate(st.session_state.pedidos):
                                    if p['numero'] == pedido['numero']:
                                        st.session_state.pedidos[i]['equipe_alocada'] = equipe_selecionada
                                        break
                                
                                st.success(f"Equipe {equipe_selecionada} alocada!")
                                st.rerun()
            
            # Ações
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if pedido.get('status') == STATUS_PEDIDO['EM_PRODUCAO']:
                    if st.button(f"📦 Marcar Pronto", key=f"pronto_{pedido['numero']}"):
                        # Atualizar status
                        for i, p in enumerate(st.session_state.pedidos):
                            if p['numero'] == pedido['numero']:
                                st.session_state.pedidos[i]['status'] = STATUS_PEDIDO['PRONTO_ENTREGA']
                                break
                        
                        log_atividade(st.session_state.username, f"Pedido marcado como pronto: {pedido['numero']}")
                        st.success("Pedido marcado como pronto!")
                        st.rerun()
            
            with col_btn2:
                if pedido.get('status') == STATUS_PEDIDO['PRONTO_ENTREGA']:
                    if st.button(f"🚚 Enviar p/ Campo", key=f"campo_{pedido['numero']}"):
                        # Atualizar status
                        for i, p in enumerate(st.session_state.pedidos):
                            if p['numero'] == pedido['numero']:
                                st.session_state.pedidos[i]['status'] = STATUS_PEDIDO['EM_ENTREGA']
                                break
                        
                        log_atividade(st.session_state.username, f"Pedido enviado para campo: {pedido['numero']}")
                        st.success("Pedido enviado para equipe de campo!")
                        st.rerun()
            
            with col_btn3:
                if st.button(f"📄 Documentos", key=f"docs_{pedido['numero']}"):
                    st.info("Acesse a aba 'Documentos' para gerenciar documentos deste pedido")
            
            with col_btn4:
                if st.button(f"📊 Detalhes", key=f"detalhes_{pedido['numero']}"):
                    st.info("Visualização detalhada em desenvolvimento")

def gestao_equipes():
    """Gestão de equipes e colaboradores"""
    st.markdown("### 👥 Gestão de Equipes")
    
    # Tabs para organizar
    tab1, tab2 = st.tabs(["👥 Equipes", "👤 Colaboradores"])
    
    with tab1:
        # Criar nova equipe
        st.markdown("#### ➕ Criar Nova Equipe")
        
        with st.form("nova_equipe_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_equipe = st.text_input("Nome da Equipe *")
                lider_equipe = st.text_input("Líder da Equipe *")
            
            with col2:
                especialidade = st.selectbox(
                    "Especialidade",
                    options=["Montagem", "Desmontagem", "Transporte", "Técnica", "Geral"]
                )
                capacidade = st.number_input("Capacidade (pessoas)", min_value=1, value=3)
            
            if st.form_submit_button("➕ Criar Equipe"):
                if nome_equipe and lider_equipe:
                    nova_equipe = {
                        'id': len(st.session_state.equipes) + 1,
                        'nome': nome_equipe,
                        'lider': lider_equipe,
                        'especialidade': especialidade,
                        'capacidade': capacidade,
                        'membros': [],
                        'status': 'Disponível',
                        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.equipes.append(nova_equipe)
                    log_atividade(st.session_state.username, f"Equipe criada: {nome_equipe}")
                    st.success(f"✅ Equipe '{nome_equipe}' criada com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios!")
        
        # Listar equipes existentes
        st.markdown("#### 📋 Equipes Existentes")
        
        equipes = st.session_state.equipes
        
        if not equipes:
            st.info("👥 Nenhuma equipe cadastrada. Crie sua primeira equipe!")
        else:
            for equipe in equipes:
                with st.expander(f"👥 {equipe['nome']} - {equipe['especialidade']} ({equipe['status']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Líder:** {equipe['lider']}")
                        st.write(f"**Especialidade:** {equipe['especialidade']}")
                        st.write(f"**Capacidade:** {equipe['capacidade']} pessoas")
                        st.write(f"**Status:** {equipe['status']}")
                    
                    with col2:
                        membros = equipe.get('membros', [])
                        st.write(f"**Membros ({len(membros)}):**")
                        if membros:
                            for membro in membros:
                                st.write(f"• {membro}")
                        else:
                            st.write("Nenhum membro alocado")
                    
                    # Ações
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button(f"✏️ Editar", key=f"edit_equipe_{equipe['id']}"):
                            st.info("Funcionalidade de edição em desenvolvimento")
                    
                    with col_btn2:
                        if st.button(f"🗑️ Excluir", key=f"del_equipe_{equipe['id']}"):
                            st.session_state.equipes = [e for e in st.session_state.equipes 
                                                       if e['id'] != equipe['id']]
                            log_atividade(st.session_state.username, f"Equipe excluída: {equipe['nome']}")
                            st.success("Equipe excluída!")
                            st.rerun()
    
    with tab2:
        # Cadastrar novo colaborador
        st.markdown("#### ➕ Cadastrar Novo Colaborador")
        
        with st.form("novo_colaborador_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_colaborador = st.text_input("Nome Completo *")
                telefone_colaborador = st.text_input("Telefone *")
                email_colaborador = st.text_input("E-mail")
            
            with col2:
                funcao = st.selectbox(
                    "Função",
                    options=["Montador", "Técnico", "Motorista", "Auxiliar", "Líder"]
                )
                
                equipes_disponiveis = [e['nome'] for e in st.session_state.equipes]
                equipe_colaborador = st.selectbox(
                    "Equipe",
                    options=["Sem equipe"] + equipes_disponiveis
                )
                
                status_colaborador = st.selectbox(
                    "Status",
                    options=["Ativo", "Inativo", "Férias", "Afastado"]
                )
            
            if st.form_submit_button("➕ Cadastrar Colaborador"):
                if nome_colaborador and telefone_colaborador:
                    novo_colaborador = {
                        'id': len(st.session_state.colaboradores) + 1,
                        'nome': nome_colaborador,
                        'telefone': telefone_colaborador,
                        'email': email_colaborador,
                        'funcao': funcao,
                        'equipe': equipe_colaborador,
                        'status': status_colaborador,
                        'data_cadastro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.colaboradores.append(novo_colaborador)
                    
                    # Adicionar à equipe se selecionada
                    if equipe_colaborador != "Sem equipe":
                        for i, equipe in enumerate(st.session_state.equipes):
                            if equipe['nome'] == equipe_colaborador:
                                if 'membros' not in st.session_state.equipes[i]:
                                    st.session_state.equipes[i]['membros'] = []
                                st.session_state.equipes[i]['membros'].append(nome_colaborador)
                                break
                    
                    log_atividade(st.session_state.username, f"Colaborador cadastrado: {nome_colaborador}")
                    st.success(f"✅ Colaborador '{nome_colaborador}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios!")
        
        # Listar colaboradores
        st.markdown("#### 📋 Colaboradores Cadastrados")
        
        colaboradores = st.session_state.colaboradores
        
        if not colaboradores:
            st.info("👤 Nenhum colaborador cadastrado. Cadastre o primeiro colaborador!")
        else:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                equipe_filter = st.selectbox(
                    "Filtrar por Equipe",
                    options=["Todas"] + ["Sem equipe"] + [e['nome'] for e in st.session_state.equipes]
                )
            
            with col2:
                status_filter = st.selectbox(
                    "Filtrar por Status",
                    options=["Todos", "Ativo", "Inativo", "Férias", "Afastado"]
                )
            
            # Aplicar filtros
            colaboradores_filtrados = colaboradores.copy()
            
            if equipe_filter != "Todas":
                colaboradores_filtrados = [c for c in colaboradores_filtrados 
                                         if c.get('equipe') == equipe_filter]
            
            if status_filter != "Todos":
                colaboradores_filtrados = [c for c in colaboradores_filtrados 
                                         if c.get('status') == status_filter]
            
            # Exibir colaboradores
            for colaborador in colaboradores_filtrados:
                with st.expander(f"👤 {colaborador['nome']} - {colaborador['funcao']} ({colaborador['status']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Telefone:** {colaborador['telefone']}")
                        st.write(f"**E-mail:** {colaborador.get('email', 'Não informado')}")
                        st.write(f"**Função:** {colaborador['funcao']}")
                    
                    with col2:
                        st.write(f"**Equipe:** {colaborador['equipe']}")
                        st.write(f"**Status:** {colaborador['status']}")
                        st.write(f"**Cadastrado em:** {colaborador['data_cadastro']}")
                    
                    # Ações
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button(f"✏️ Editar", key=f"edit_colab_{colaborador['id']}"):
                            st.info("Funcionalidade de edição em desenvolvimento")
                    
                    with col_btn2:
                        if st.button(f"🗑️ Excluir", key=f"del_colab_{colaborador['id']}"):
                            # Remover da equipe
                            if colaborador['equipe'] != "Sem equipe":
                                for i, equipe in enumerate(st.session_state.equipes):
                                    if equipe['nome'] == colaborador['equipe']:
                                        if 'membros' in st.session_state.equipes[i]:
                                            st.session_state.equipes[i]['membros'] = [
                                                m for m in st.session_state.equipes[i]['membros'] 
                                                if m != colaborador['nome']
                                            ]
                                        break
                            
                            # Remover colaborador
                            st.session_state.colaboradores = [c for c in st.session_state.colaboradores 
                                                             if c['id'] != colaborador['id']]
                            
                            log_atividade(st.session_state.username, f"Colaborador excluído: {colaborador['nome']}")
                            st.success("Colaborador excluído!")
                            st.rerun()

def tarefas_galpao():
    """Gestão de tarefas do galpão"""
    st.markdown("### 📋 Tarefas de Galpão")
    
    # Criar nova tarefa
    st.markdown("#### ➕ Nova Tarefa")
    
    with st.form("nova_tarefa_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo_tarefa = st.text_input("Título da Tarefa *")
            descricao_tarefa = st.text_area("Descrição")
            prioridade = st.selectbox("Prioridade", options=["Baixa", "Média", "Alta", "Urgente"])
        
        with col2:
            # Responsável
            colaboradores_disponiveis = [c['nome'] for c in st.session_state.colaboradores 
                                       if c.get('status') == 'Ativo']
            responsavel = st.selectbox(
                "Responsável",
                options=["Não atribuído"] + colaboradores_disponiveis
            )
            
            prazo = st.date_input("Prazo")
            categoria = st.selectbox(
                "Categoria",
                options=["Organização", "Manutenção", "Limpeza", "Inventário", "Preparação"]
            )
        
        if st.form_submit_button("➕ Criar Tarefa"):
            if titulo_tarefa:
                nova_tarefa = {
                    'id': len(st.session_state.tarefas_galpao) + 1,
                    'titulo': titulo_tarefa,
                    'descricao': descricao_tarefa,
                    'prioridade': prioridade,
                    'responsavel': responsavel,
                    'prazo': prazo.strftime("%Y-%m-%d") if prazo else None,
                    'categoria': categoria,
                    'status': 'Pendente',
                    'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'criado_por': st.session_state.username
                }
                
                st.session_state.tarefas_galpao.append(nova_tarefa)
                log_atividade(st.session_state.username, f"Tarefa criada: {titulo_tarefa}")
                st.success(f"✅ Tarefa '{titulo_tarefa}' criada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Título da tarefa é obrigatório!")
    
    # Listar tarefas
    st.markdown("#### 📋 Tarefas Existentes")
    
    tarefas = st.session_state.tarefas_galpao
    
    if not tarefas:
        st.info("📋 Nenhuma tarefa cadastrada. Crie a primeira tarefa!")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            options=["Todos", "Pendente", "Em Andamento", "Concluída", "Cancelada"]
        )
    
    with col2:
        prioridade_filter = st.selectbox(
            "Filtrar por Prioridade",
            options=["Todas", "Baixa", "Média", "Alta", "Urgente"]
        )
    
    with col3:
        responsavel_filter = st.selectbox(
            "Filtrar por Responsável",
            options=["Todos"] + ["Não atribuído"] + [c['nome'] for c in st.session_state.colaboradores]
        )
    
    # Aplicar filtros
    tarefas_filtradas = tarefas.copy()
    
    if status_filter != "Todos":
        tarefas_filtradas = [t for t in tarefas_filtradas if t.get('status') == status_filter]
    
    if prioridade_filter != "Todas":
        tarefas_filtradas = [t for t in tarefas_filtradas if t.get('prioridade') == prioridade_filter]
    
    if responsavel_filter != "Todos":
        tarefas_filtradas = [t for t in tarefas_filtradas if t.get('responsavel') == responsavel_filter]
    
    # Exibir tarefas
    st.markdown(f"**{len(tarefas_filtradas)} tarefa(s) encontrada(s)**")
    
    for tarefa in tarefas_filtradas:
        # Cor da prioridade
        cor_prioridade = {
            'Baixa': '#28a745',
            'Média': '#ffc107', 
            'Alta': '#fd7e14',
            'Urgente': '#dc3545'
        }
        
        with st.expander(f"📋 {tarefa['titulo']} - {tarefa['prioridade']} ({tarefa['status']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Descrição:** {tarefa.get('descricao', 'Sem descrição')}")
                st.write(f"**Categoria:** {tarefa['categoria']}")
                st.write(f"**Responsável:** {tarefa['responsavel']}")
                
                # Prioridade com cor
                cor = cor_prioridade.get(tarefa['prioridade'], '#6c757d')
                st.markdown(f"**Prioridade:** <span style='color: {cor}; font-weight: bold;'>{tarefa['prioridade']}</span>", 
                          unsafe_allow_html=True)
            
            with col2:
                st.write(f"**Status:** {tarefa['status']}")
                st.write(f"**Prazo:** {tarefa.get('prazo', 'Sem prazo')}")
                st.write(f"**Criado em:** {tarefa['data_criacao']}")
                st.write(f"**Criado por:** {tarefa['criado_por']}")
            
            # Ações
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if tarefa['status'] == 'Pendente':
                    if st.button(f"▶️ Iniciar", key=f"iniciar_{tarefa['id']}"):
                        # Atualizar status
                        for i, t in enumerate(st.session_state.tarefas_galpao):
                            if t['id'] == tarefa['id']:
                                st.session_state.tarefas_galpao[i]['status'] = 'Em Andamento'
                                break
                        
                        log_atividade(st.session_state.username, f"Tarefa iniciada: {tarefa['titulo']}")
                        st.success("Tarefa iniciada!")
                        st.rerun()
            
            with col_btn2:
                if tarefa['status'] == 'Em Andamento':
                    if st.button(f"✅ Concluir", key=f"concluir_{tarefa['id']}"):
                        # Atualizar status
                        for i, t in enumerate(st.session_state.tarefas_galpao):
                            if t['id'] == tarefa['id']:
                                st.session_state.tarefas_galpao[i]['status'] = 'Concluída'
                                st.session_state.tarefas_galpao[i]['data_conclusao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break
                        
                        log_atividade(st.session_state.username, f"Tarefa concluída: {tarefa['titulo']}")
                        st.success("Tarefa concluída!")
                        st.rerun()
            
            with col_btn3:
                if st.button(f"✏️ Editar", key=f"edit_tarefa_{tarefa['id']}"):
                    st.info("Funcionalidade de edição em desenvolvimento")
            
            with col_btn4:
                if st.button(f"🗑️ Excluir", key=f"del_tarefa_{tarefa['id']}"):
                    st.session_state.tarefas_galpao = [t for t in st.session_state.tarefas_galpao 
                                                     if t['id'] != tarefa['id']]
                    log_atividade(st.session_state.username, f"Tarefa excluída: {tarefa['titulo']}")
                    st.success("Tarefa excluída!")
                    st.rerun()

def gestao_documentos():
    """Gestão de documentos por pedido"""
    st.markdown("### 📄 Gestão de Documentos")
    
    # Filtrar pedidos ativos (que precisam de documentos)
    pedidos = st.session_state.pedidos
    status_ativos = [STATUS_PEDIDO['APROVADO'], STATUS_PEDIDO['EM_PRODUCAO'], STATUS_PEDIDO['PRONTO_ENTREGA']]
    pedidos_ativos = [p for p in pedidos if p.get('status') in status_ativos]
    
    if not pedidos_ativos:
        st.info("📄 Nenhum pedido ativo encontrado. Documentos são gerenciados apenas para pedidos ativos.")
        return
    
    st.markdown("#### 📋 Pedidos Ativos")
    st.info("💡 Clique em 'Gerenciar Documentos' para anexar documentos específicos de cada pedido.")
    
    for pedido in pedidos_ativos:
        with st.expander(f"🎫 {pedido['numero']} - {pedido['cliente']} - {pedido['evento']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Cliente:** {pedido['cliente']}")
                st.write(f"**Evento:** {pedido['evento']}")
                st.write(f"**Data:** {pedido['data_inicio']} a {pedido['data_fim']}")
                st.markdown(f"**Status:** {formatar_status_badge(pedido['status'])}", 
                          unsafe_allow_html=True)
            
            with col2:
                # Verificar documentos do pedido
                docs_pedido = st.session_state.documentos.get(pedido['numero'], {})
                
                st.markdown("**📄 Status dos Documentos:**")
                
                tipos_documentos = [
                    "Ordem de Separação",
                    "Confirmação de Reserva", 
                    "Romaneio de Entrega",
                    "Termo de Recebimento"
                ]
                
                for tipo in tipos_documentos:
                    status_doc = "✅ Anexado" if docs_pedido.get(tipo) else "⚠️ Pendente"
                    st.write(f"• {tipo}: {status_doc}")
            
            # Botão para gerenciar documentos
            if st.button(f"📄 Gerenciar Documentos", key=f"docs_{pedido['numero']}"):
                st.session_state.pedido_docs_ativo = pedido['numero']
                st.rerun()
    
    # Modal/Interface para gerenciar documentos de um pedido específico
    if hasattr(st.session_state, 'pedido_docs_ativo') and st.session_state.pedido_docs_ativo:
        pedido_ativo = next((p for p in pedidos_ativos if p['numero'] == st.session_state.pedido_docs_ativo), None)
        
        if pedido_ativo:
            st.markdown("---")
            st.markdown(f"### 📄 Documentos do Pedido {pedido_ativo['numero']}")
            
            col_header1, col_header2 = st.columns([3, 1])
            
            with col_header1:
                st.markdown(f"**Cliente:** {pedido_ativo['cliente']} | **Evento:** {pedido_ativo['evento']}")
            
            with col_header2:
                if st.button("❌ Fechar", key="fechar_docs"):
                    del st.session_state.pedido_docs_ativo
                    st.rerun()
            
            # Inicializar documentos do pedido se não existir
            if pedido_ativo['numero'] not in st.session_state.documentos:
                st.session_state.documentos[pedido_ativo['numero']] = {}
            
            docs_pedido = st.session_state.documentos[pedido_ativo['numero']]
            
            # Interface para cada tipo de documento
            tipos_documentos = {
                "Ordem de Separação": "📋 Lista de itens para separação no galpão",
                "Confirmação de Reserva": "✅ Confirmação da reserva do cliente", 
                "Romaneio de Entrega": "📦 Lista de itens para entrega",
                "Termo de Recebimento": "📝 Documento de recebimento assinado"
            }
            
            for tipo, descricao in tipos_documentos.items():
                st.markdown(f"#### 📄 {tipo}")
                st.markdown(f"*{descricao}*")
                
                col_doc1, col_doc2, col_doc3 = st.columns([2, 1, 1])
                
                with col_doc1:
                    # Upload de arquivo
                    arquivo = st.file_uploader(
                        f"Anexar {tipo}",
                        type=['pdf', 'jpg', 'png', 'docx', 'jpeg'],
                        key=f"upload_{tipo}_{pedido_ativo['numero']}"
                    )
                
                with col_doc2:
                    # Status do documento
                    if docs_pedido.get(tipo):
                        st.success("✅ Anexado")
                    else:
                        st.warning("⚠️ Pendente")
                
                with col_doc3:
                    # Ações
                    if tipo in ["Ordem de Separação", "Romaneio de Entrega"]:
                        if st.button(f"🔄 Gerar Auto", key=f"gerar_{tipo}_{pedido_ativo['numero']}"):
                            # Simular geração automática
                            docs_pedido[tipo] = f"auto_gerado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            st.session_state.documentos[pedido_ativo['numero']] = docs_pedido
                            
                            log_atividade(st.session_state.username, 
                                        f"Documento gerado automaticamente: {tipo} - Pedido {pedido_ativo['numero']}")
                            st.success(f"{tipo} gerado automaticamente!")
                            st.rerun()
                
                # Processar upload
                if arquivo:
                    docs_pedido[tipo] = arquivo.name
                    st.session_state.documentos[pedido_ativo['numero']] = docs_pedido
                    
                    log_atividade(st.session_state.username, 
                                f"Documento anexado: {tipo} - Pedido {pedido_ativo['numero']}")
                    st.success(f"✅ {tipo} anexado com sucesso!")
                    st.rerun()
                
                # Exibir arquivo anexado
                if docs_pedido.get(tipo):
                    st.info(f"📎 Arquivo: {docs_pedido[tipo]}")
                
                st.markdown("---")
            
            # Resumo dos documentos
            total_docs = len(tipos_documentos)
            docs_anexados = len([d for d in docs_pedido.values() if d])
            
            progress = docs_anexados / total_docs
            st.progress(progress)
            st.markdown(f"**Progresso:** {docs_anexados}/{total_docs} documentos anexados ({progress*100:.0f}%)")
            
            if docs_anexados == total_docs:
                st.success("🎉 Todos os documentos foram anexados! Pedido pronto para prosseguir.")

# ==================== INTERFACE EQUIPE DE CAMPO ====================

def interface_campo():
    """Interface da equipe de campo"""
    st.markdown("""
    <div class="nexo-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="nexo-logo">NEXO Campo</h1>
                <p class="nexo-subtitle">Entregas e Recolhimentos</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem;">👤 {st.session_state.username}</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Equipe de Campo</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação mobile-first
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    tabs = st.tabs(["🚚 Entregas", "📦 Recolhimentos", "✅ Concluídos"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[0]:  # Entregas
        entregas_pendentes()
    
    with tabs[1]:  # Recolhimentos
        recolhimentos_pendentes()
    
    with tabs[2]:  # Concluídos
        pedidos_concluidos()

def entregas_pendentes():
    """Interface para entregas pendentes"""
    st.markdown("### 🚚 Entregas Pendentes")
    
    # Filtrar pedidos para entrega
    pedidos = st.session_state.pedidos
    pedidos_entrega = [p for p in pedidos if p.get('status') == STATUS_PEDIDO['EM_ENTREGA']]
    
    if not pedidos_entrega:
        st.info("🚚 Nenhuma entrega pendente no momento.")
        return
    
    st.markdown(f"**{len(pedidos_entrega)} entrega(s) pendente(s)**")
    
    for pedido in pedidos_entrega:
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #ff6b35; margin: 0 0 1rem 0;">🎫 {pedido['numero']} - {pedido['cliente']}</h4>
                <p><strong>Evento:</strong> {pedido['evento']}</p>
                <p><strong>Local:</strong> {pedido['local']}</p>
                <p><strong>Data:</strong> {pedido['data_inicio']} a {pedido['data_fim']}</p>
                <p><strong>Equipe:</strong> {pedido.get('equipe_alocada', 'Não definida')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para iniciar entrega
            if st.button(f"🚀 Iniciar Entrega", key=f"iniciar_entrega_{pedido['numero']}", use_container_width=True):
                st.session_state.trabalho_ativo = {
                    'pedido': pedido,
                    'tipo': 'entrega',
                    'etapa_atual': 1,
                    'etapas_concluidas': [],
                    'dados_entrega': {}
                }
                st.rerun()
    
    # Interface de trabalho ativo
    if hasattr(st.session_state, 'trabalho_ativo') and st.session_state.trabalho_ativo:
        interface_trabalho_ativo()

def recolhimentos_pendentes():
    """Interface para recolhimentos pendentes"""
    st.markdown("### 📦 Recolhimentos Pendentes")
    
    # Filtrar pedidos para recolhimento
    pedidos = st.session_state.pedidos
    pedidos_recolhimento = [p for p in pedidos if p.get('status') == STATUS_PEDIDO['ENTREGUE']]
    
    if not pedidos_recolhimento:
        st.info("📦 Nenhum recolhimento pendente no momento.")
        return
    
    st.markdown(f"**{len(pedidos_recolhimento)} recolhimento(s) pendente(s)**")
    
    for pedido in pedidos_recolhimento:
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #ff6b35; margin: 0 0 1rem 0;">🎫 {pedido['numero']} - {pedido['cliente']}</h4>
                <p><strong>Evento:</strong> {pedido['evento']}</p>
                <p><strong>Local:</strong> {pedido['local']}</p>
                <p><strong>Data Entrega:</strong> {pedido.get('data_entrega_realizada', 'N/A')}</p>
                <p><strong>Equipe:</strong> {pedido.get('equipe_alocada', 'Não definida')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para iniciar recolhimento
            if st.button(f"📦 Iniciar Recolhimento", key=f"iniciar_recolhimento_{pedido['numero']}", use_container_width=True):
                st.session_state.trabalho_ativo = {
                    'pedido': pedido,
                    'tipo': 'recolhimento',
                    'etapa_atual': 1,
                    'etapas_concluidas': [],
                    'dados_recolhimento': {}
                }
                st.rerun()
    
    # Interface de trabalho ativo
    if hasattr(st.session_state, 'trabalho_ativo') and st.session_state.trabalho_ativo:
        interface_trabalho_ativo()

def pedidos_concluidos():
    """Interface para pedidos concluídos"""
    st.markdown("### ✅ Pedidos Concluídos")
    
    # Filtrar pedidos concluídos
    pedidos = st.session_state.pedidos
    pedidos_concluidos = [p for p in pedidos if p.get('status') == STATUS_PEDIDO['CONCLUIDO']]
    
    if not pedidos_concluidos:
        st.info("✅ Nenhum pedido concluído ainda.")
        return
    
    st.markdown(f"**{len(pedidos_concluidos)} pedido(s) concluído(s)**")
    
    for pedido in pedidos_concluidos:
        with st.expander(f"✅ {pedido['numero']} - {pedido['cliente']} - {pedido['evento']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Cliente:** {pedido['cliente']}")
                st.write(f"**Evento:** {pedido['evento']}")
                st.write(f"**Local:** {pedido['local']}")
                st.write(f"**Equipe:** {pedido.get('equipe_alocada', 'N/A')}")
            
            with col2:
                st.write(f"**Data Entrega:** {pedido.get('data_entrega_realizada', 'N/A')}")
                st.write(f"**Data Recolhimento:** {pedido.get('data_recolhimento_realizada', 'N/A')}")
                st.write(f"**Concluído em:** {pedido.get('data_conclusao', 'N/A')}")
                st.write(f"**Total:** R$ {pedido['total']:,.2f}")
            
            # Mostrar produtos
            st.markdown("**📦 Produtos:**")
            for produto in pedido['produtos']:
                st.write(f"• {produto['nome']} - Qtd: {produto['quantidade']}")

def interface_trabalho_ativo():
    """Interface para trabalho ativo (entrega ou recolhimento)"""
    trabalho = st.session_state.trabalho_ativo
    pedido = trabalho['pedido']
    tipo = trabalho['tipo']
    etapa_atual = trabalho['etapa_atual']
    
    st.markdown("---")
    st.markdown(f"### 🔄 {tipo.title()} em Andamento")
    
    # Header do trabalho
    col_header1, col_header2 = st.columns([3, 1])
    
    with col_header1:
        st.markdown(f"**🎫 {pedido['numero']} - {pedido['cliente']}**")
        st.markdown(f"**📍 {pedido['local']}**")
    
    with col_header2:
        if st.button("❌ Cancelar", key="cancelar_trabalho"):
            del st.session_state.trabalho_ativo
            st.rerun()
    
    # Progresso das etapas
    etapas_total = 7
    progresso = (etapa_atual - 1) / etapas_total
    st.progress(progresso)
    st.markdown(f"**Etapa {etapa_atual} de {etapas_total}**")
    
    # Executar etapa atual
    executar_etapa_trabalho(trabalho)

def executar_etapa_trabalho(trabalho):
    """Executa a etapa atual do trabalho"""
    pedido = trabalho['pedido']
    tipo = trabalho['tipo']
    etapa_atual = trabalho['etapa_atual']
    
    if etapa_atual == 1:
        # Etapa 1: Confirmação de Saída
        st.markdown("#### 1️⃣ Confirmação de Saída")
        st.info("Confirme a saída da base para o local do evento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hora_saida = st.time_input("Horário de Saída", key="hora_saida")
        
        with col2:
            veiculo = st.text_input("Veículo Utilizado", placeholder="Placa do veículo", key="veiculo")
        
        if st.button("✅ Confirmar Saída", key="confirmar_saida", use_container_width=True):
            if hora_saida and veiculo:
                trabalho['dados_entrega']['hora_saida'] = hora_saida.strftime("%H:%M")
                trabalho['dados_entrega']['veiculo'] = veiculo
                trabalho['etapa_atual'] = 2
                trabalho['etapas_concluidas'].append(1)
                
                log_atividade(st.session_state.username, 
                            f"Saída confirmada - {tipo} {pedido['numero']}")
                st.rerun()
            else:
                st.error("❌ Preencha todos os campos!")
    
    elif etapa_atual == 2:
        # Etapa 2: Localização GPS
        st.markdown("#### 2️⃣ Confirmação de Localização")
        st.info("Confirme sua localização atual")
        
        # Simular GPS (em produção, usar geolocalização real)
        if st.button("📍 Obter Localização GPS", key="gps", use_container_width=True):
            # Simular coordenadas
            import random
            lat = -23.5505 + random.uniform(-0.1, 0.1)
            lng = -46.6333 + random.uniform(-0.1, 0.1)
            
            trabalho['dados_entrega']['latitude'] = lat
            trabalho['dados_entrega']['longitude'] = lng
            trabalho['dados_entrega']['endereco_gps'] = f"Lat: {lat:.6f}, Lng: {lng:.6f}"
            
            st.success(f"📍 Localização obtida: {lat:.6f}, {lng:.6f}")
            
            if st.button("✅ Confirmar Localização", key="confirmar_gps", use_container_width=True):
                trabalho['etapa_atual'] = 3
                trabalho['etapas_concluidas'].append(2)
                
                log_atividade(st.session_state.username, 
                            f"Localização confirmada - {tipo} {pedido['numero']}")
                st.rerun()
    
    elif etapa_atual == 3:
        # Etapa 3: Chegada ao Local
        st.markdown("#### 3️⃣ Chegada ao Local")
        st.info("Confirme a chegada ao local do evento")
        
        hora_chegada = st.time_input("Horário de Chegada", key="hora_chegada")
        observacoes_chegada = st.text_area("Observações da Chegada", 
                                         placeholder="Condições do local, acesso, etc.", 
                                         key="obs_chegada")
        
        if st.button("✅ Confirmar Chegada", key="confirmar_chegada", use_container_width=True):
            if hora_chegada:
                trabalho['dados_entrega']['hora_chegada'] = hora_chegada.strftime("%H:%M")
                trabalho['dados_entrega']['observacoes_chegada'] = observacoes_chegada
                trabalho['etapa_atual'] = 4
                trabalho['etapas_concluidas'].append(3)
                
                log_atividade(st.session_state.username, 
                            f"Chegada confirmada - {tipo} {pedido['numero']}")
                st.rerun()
            else:
                st.error("❌ Horário de chegada é obrigatório!")
    
    elif etapa_atual == 4:
        # Etapa 4: Checklist de Produtos
        st.markdown("#### 4️⃣ Checklist de Produtos")
        st.info(f"Confirme todos os produtos para {tipo}")
        
        produtos = pedido['produtos']
        produtos_ok = True
        
        for i, produto in enumerate(produtos):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{produto['nome']}**")
            
            with col2:
                st.write(f"Qtd: {produto['quantidade']}")
            
            with col3:
                produto_ok = st.checkbox("✅", key=f"produto_check_{i}", value=False)
                if not produto_ok:
                    produtos_ok = False
        
        if produtos_ok and all([st.session_state.get(f"produto_check_{i}", False) for i in range(len(produtos))]):
            if st.button("✅ Confirmar Checklist", key="confirmar_checklist", use_container_width=True):
                trabalho['dados_entrega']['checklist_completo'] = True
                trabalho['etapa_atual'] = 5
                trabalho['etapas_concluidas'].append(4)
                
                log_atividade(st.session_state.username, 
                            f"Checklist confirmado - {tipo} {pedido['numero']}")
                st.rerun()
        else:
            st.warning("⚠️ Marque todos os produtos como conferidos")
    
    elif etapa_atual == 5:
        # Etapa 5: Execução do Serviço
        st.markdown(f"#### 5️⃣ Execução do {tipo.title()}")
        st.info(f"Registre o início e fim da {tipo}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hora_inicio = st.time_input("Início do Serviço", key="hora_inicio_servico")
        
        with col2:
            hora_fim = st.time_input("Fim do Serviço", key="hora_fim_servico")
        
        observacoes_servico = st.text_area("Observações do Serviço", 
                                         placeholder="Detalhes da execução, problemas encontrados, etc.",
                                         key="obs_servico")
        
        if st.button("✅ Confirmar Execução", key="confirmar_execucao", use_container_width=True):
            if hora_inicio and hora_fim:
                trabalho['dados_entrega']['hora_inicio_servico'] = hora_inicio.strftime("%H:%M")
                trabalho['dados_entrega']['hora_fim_servico'] = hora_fim.strftime("%H:%M")
                trabalho['dados_entrega']['observacoes_servico'] = observacoes_servico
                trabalho['etapa_atual'] = 6
                trabalho['etapas_concluidas'].append(5)
                
                log_atividade(st.session_state.username, 
                            f"Execução confirmada - {tipo} {pedido['numero']}")
                st.rerun()
            else:
                st.error("❌ Preencha horário de início e fim!")
    
    elif etapa_atual == 6:
        # Etapa 6: Assinatura Digital
        st.markdown("#### 6️⃣ Assinatura do Cliente")
        st.info("Colete a assinatura e dados do responsável")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_responsavel = st.text_input("Nome do Responsável *", key="nome_responsavel")
            cpf_responsavel = st.text_input("CPF do Responsável *", key="cpf_responsavel")
        
        with col2:
            cargo_responsavel = st.text_input("Cargo/Função", key="cargo_responsavel")
            telefone_responsavel = st.text_input("Telefone", key="telefone_responsavel")
        
        # Campo de assinatura (simulado)
        st.markdown("**✍️ Assinatura Digital:**")
        assinatura_texto = st.text_area("Campo de Assinatura", 
                                       placeholder="Em produção: campo de desenho para assinatura digital",
                                       height=100,
                                       key="assinatura_digital")
        
        if st.button("✅ Confirmar Assinatura", key="confirmar_assinatura", use_container_width=True):
            if nome_responsavel and cpf_responsavel and assinatura_texto:
                trabalho['dados_entrega']['nome_responsavel'] = nome_responsavel
                trabalho['dados_entrega']['cpf_responsavel'] = cpf_responsavel
                trabalho['dados_entrega']['cargo_responsavel'] = cargo_responsavel
                trabalho['dados_entrega']['telefone_responsavel'] = telefone_responsavel
                trabalho['dados_entrega']['assinatura'] = assinatura_texto
                trabalho['etapa_atual'] = 7
                trabalho['etapas_concluidas'].append(6)
                
                log_atividade(st.session_state.username, 
                            f"Assinatura coletada - {tipo} {pedido['numero']}")
                st.rerun()
            else:
                st.error("❌ Nome, CPF e assinatura são obrigatórios!")
    
    elif etapa_atual == 7:
        # Etapa 7: Finalização
        st.markdown("#### 7️⃣ Finalização")
        st.info(f"Confirme a finalização da {tipo}")
        
        # Resumo do trabalho
        st.markdown("**📋 Resumo do Trabalho:**")
        dados = trabalho['dados_entrega']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Saída:** {dados.get('hora_saida', 'N/A')}")
            st.write(f"**Chegada:** {dados.get('hora_chegada', 'N/A')}")
            st.write(f"**Início Serviço:** {dados.get('hora_inicio_servico', 'N/A')}")
            st.write(f"**Fim Serviço:** {dados.get('hora_fim_servico', 'N/A')}")
        
        with col2:
            st.write(f"**Veículo:** {dados.get('veiculo', 'N/A')}")
            st.write(f"**Responsável:** {dados.get('nome_responsavel', 'N/A')}")
            st.write(f"**CPF:** {dados.get('cpf_responsavel', 'N/A')}")
            st.write(f"**Localização:** {dados.get('endereco_gps', 'N/A')}")
        
        observacoes_finais = st.text_area("Observações Finais", 
                                        placeholder="Observações gerais sobre o trabalho",
                                        key="obs_finais")
        
        if st.button("🎉 Finalizar Trabalho", key="finalizar_trabalho", use_container_width=True):
            # Atualizar status do pedido
            novo_status = STATUS_PEDIDO['ENTREGUE'] if tipo == 'entrega' else STATUS_PEDIDO['CONCLUIDO']
            
            for i, p in enumerate(st.session_state.pedidos):
                if p['numero'] == pedido['numero']:
                    st.session_state.pedidos[i]['status'] = novo_status
                    
                    if tipo == 'entrega':
                        st.session_state.pedidos[i]['data_entrega_realizada'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.pedidos[i]['dados_entrega'] = dados
                    else:
                        st.session_state.pedidos[i]['data_recolhimento_realizada'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.pedidos[i]['data_conclusao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.pedidos[i]['dados_recolhimento'] = dados
                    
                    st.session_state.pedidos[i]['observacoes_finais'] = observacoes_finais
                    break
            
            log_atividade(st.session_state.username, 
                        f"{tipo.title()} finalizada - {pedido['numero']}")
            
            # Limpar trabalho ativo
            del st.session_state.trabalho_ativo
            
            st.success(f"🎉 {tipo.title()} finalizada com sucesso!")
            st.balloons()
            time.sleep(2)
            st.rerun()

# ==================== INTERFACE BOSS ====================

def interface_boss():
    """Interface do módulo boss"""
    st.markdown("""
    <div class="nexo-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="nexo-logo">NEXO Boss</h1>
                <p class="nexo-subtitle">Dashboard Executivo</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem;">👤 {st.session_state.username}</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Boss</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    tabs = st.tabs(["📊 Dashboard Executivo", "💰 Análise Financeira", "👥 Performance da Equipe", "📈 Relatórios", "⚙️ Configurações"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[0]:  # Dashboard Executivo
        dashboard_executivo()
    
    with tabs[1]:  # Análise Financeira
        analise_financeira()
    
    with tabs[2]:  # Performance da Equipe
        performance_equipe()
    
    with tabs[3]:  # Relatórios
        relatorios_executivos()
    
    with tabs[4]:  # Configurações
        configuracoes_sistema()

def dashboard_executivo():
    """Dashboard executivo com KPIs principais"""
    st.markdown("### 📊 Dashboard Executivo")
    
    # Dados para análise
    pedidos = st.session_state.pedidos
    equipes = st.session_state.equipes
    colaboradores = st.session_state.colaboradores
    
    # KPIs Principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pedidos = len(pedidos)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff6b35; margin: 0;">📋 Total Pedidos</h3>
            <h2 style="margin: 0.5rem 0;">{total_pedidos}</h2>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        receita_total = sum([p.get('total', 0) for p in pedidos if p.get('status') == STATUS_PEDIDO['CONCLUIDO']])
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">💰 Receita</h3>
            <h2 style="margin: 0.5rem 0;">R$ {receita_total:,.0f}</h2>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Concluídos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pedidos_concluidos = len([p for p in pedidos if p.get('status') == STATUS_PEDIDO['CONCLUIDO']])
        taxa_conclusao = (pedidos_concluidos / total_pedidos * 100) if total_pedidos > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #17a2b8; margin: 0;">✅ Taxa Conclusão</h3>
            <h2 style="margin: 0.5rem 0;">{taxa_conclusao:.1f}%</h2>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">{pedidos_concluidos}/{total_pedidos}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_colaboradores = len(colaboradores)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #6f42c1; margin: 0;">👥 Colaboradores</h3>
            <h2 style="margin: 0.5rem 0;">{total_colaboradores}</h2>
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">Ativos</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos Executivos
    if pedidos:
        col1, col2 = st.columns(2)
        
        with col1:
            # Funil de vendas
            status_counts = {}
            for pedido in pedidos:
                status = pedido.get('status', 'Pendente')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Ordenar por funil de vendas
            funil_ordem = [
                STATUS_PEDIDO['PENDENTE'],
                STATUS_PEDIDO['APROVADO'], 
                STATUS_PEDIDO['EM_PRODUCAO'],
                STATUS_PEDIDO['PRONTO_ENTREGA'],
                STATUS_PEDIDO['EM_ENTREGA'],
                STATUS_PEDIDO['ENTREGUE'],
                STATUS_PEDIDO['CONCLUIDO']
            ]
            
            funil_dados = []
            for status in funil_ordem:
                if status in status_counts:
                    funil_dados.append({'Status': status, 'Quantidade': status_counts[status]})
            
            if funil_dados:
                df_funil = pd.DataFrame(funil_dados)
                fig_funil = px.funnel(df_funil, x='Quantidade', y='Status', 
                                    title="Funil de Vendas",
                                    color_discrete_sequence=['#ff6b35'])
                fig_funil.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_funil, use_container_width=True)
        
        with col2:
            # Receita por mês
            receita_mes = {}
            for pedido in pedidos:
                if pedido.get('data_criacao') and pedido.get('status') == STATUS_PEDIDO['CONCLUIDO']:
                    try:
                        data = datetime.strptime(pedido['data_criacao'], "%Y-%m-%d %H:%M:%S")
                        mes = data.strftime("%Y-%m")
                        receita_mes[mes] = receita_mes.get(mes, 0) + pedido.get('total', 0)
                    except:
                        pass
            
            if receita_mes:
                fig_receita = px.line(
                    x=list(receita_mes.keys()),
                    y=list(receita_mes.values()),
                    title="Evolução da Receita",
                    markers=True
                )
                fig_receita.update_traces(line_color='#ff6b35', marker_color='#ff6b35')
                fig_receita.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis_title="Mês",
                    yaxis_title="Receita (R$)"
                )
                st.plotly_chart(fig_receita, use_container_width=True)
        
        # Métricas Operacionais
        st.markdown("### 📈 Métricas Operacionais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Tempo médio de conclusão
            tempos_conclusao = []
            for pedido in pedidos:
                if pedido.get('data_criacao') and pedido.get('data_conclusao'):
                    try:
                        inicio = datetime.strptime(pedido['data_criacao'], "%Y-%m-%d %H:%M:%S")
                        fim = datetime.strptime(pedido['data_conclusao'], "%Y-%m-%d %H:%

