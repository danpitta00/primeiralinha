import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import uuid
import time
import os

# Configuração da página
st.set_page_config(
    page_title="NEXO - Núcleo de Excelência Operacional",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado - Design Neutro Preto com Acentos Laranja
st.markdown("""
<style>
    /* Reset e Base */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Cores Principais */
    :root {
        --nexo-orange: #FF6B00;
        --nexo-dark: #1a1a1a;
        --nexo-gray: #2d2d2d;
        --nexo-light-gray: #404040;
        --nexo-white: #ffffff;
        --nexo-text: #e0e0e0;
    }
    
    /* Background Principal */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: var(--nexo-text);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: var(--nexo-dark);
        border-right: 2px solid var(--nexo-orange);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--nexo-white) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Cards Personalizados */
    .metric-card {
        background: linear-gradient(135deg, var(--nexo-gray) 0%, var(--nexo-light-gray) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--nexo-orange);
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.1);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 107, 0, 0.2);
        border-color: var(--nexo-orange);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--nexo-orange) 0%, #ff8533 100%);
        color: var(--nexo-white);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff8533 0%, var(--nexo-orange) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.3);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background: var(--nexo-gray);
        color: var(--nexo-white);
        border: 1px solid var(--nexo-light-gray);
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--nexo-orange);
        box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.2);
    }
    
    /* Tabelas */
    .stDataFrame {
        background: var(--nexo-gray);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Loading Spinner */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
        flex-direction: column;
    }
    
    .loading-spinner {
        border: 4px solid var(--nexo-light-gray);
        border-top: 4px solid var(--nexo-orange);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Login Page */
    .login-container {
        background: var(--nexo-orange);
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .login-box {
        background: var(--nexo-white);
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        max-width: 400px;
        width: 100%;
        text-align: center;
    }
    
    .login-logo {
        width: 120px;
        height: auto;
        margin-bottom: 2rem;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .status-pendente {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-andamento {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .status-concluido {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-urgente {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Chat Interface */
    .chat-container {
        background: var(--nexo-gray);
        border-radius: 12px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        border: 1px solid var(--nexo-light-gray);
    }
    
    .chat-message {
        background: var(--nexo-light-gray);
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--nexo-orange);
    }
    
    /* Progress Bar */
    .progress-container {
        background: var(--nexo-light-gray);
        border-radius: 10px;
        padding: 4px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, var(--nexo-orange) 0%, #ff8533 100%);
        height: 20px;
        border-radius: 6px;
        transition: width 0.3s ease;
    }
    
    /* Mobile Responsivo */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .login-box {
            padding: 2rem;
            margin: 1rem;
        }
    }
    
    /* Alertas */
    .alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid var(--nexo-orange);
    }
    
    .alert-info {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
    }
    
    .alert-success {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
    }
    
    .alert-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
    }
    
    .alert-error {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Logo NEXO em Base64 (versão simplificada)
NEXO_LOGO_BASE64 = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjgwIiB2aWV3Qm94PSIwIDAgMTIwIDgwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0iMTIwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjRkY2QjAwIi8+Cjx0ZXh0IHg9IjYwIiB5PSI0NSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjI0IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk5FWE88L3RleHQ+Cjwvc3ZnPgo="

# Inicialização do Session State
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = []
    if 'produtos' not in st.session_state:
        st.session_state.produtos = [
            {"nome": "Tenda 3x3", "categoria": "Tendas", "preco": 150.00},
            {"nome": "Tenda 6x6", "categoria": "Tendas", "preco": 300.00},
            {"nome": "Mesa Redonda", "categoria": "Mobiliário", "preco": 25.00},
            {"nome": "Cadeira Plástica", "categoria": "Mobiliário", "preco": 5.00},
            {"nome": "Som Ambiente", "categoria": "Áudio", "preco": 200.00},
            {"nome": "Iluminação LED", "categoria": "Iluminação", "preco": 100.00}
        ]
    if 'equipes' not in st.session_state:
        st.session_state.equipes = [
            {"nome": "João Silva", "especialidade": "Montagem", "status": "Disponível"},
            {"nome": "Carlos Santos", "especialidade": "Elétrica", "status": "Ocupado"},
            {"nome": "Pedro Lima", "especialidade": "Logística", "status": "Disponível"},
            {"nome": "Ana Costa", "especialidade": "Decoração", "status": "Disponível"},
            {"nome": "Marcelão", "especialidade": "Supervisão", "status": "Disponível"}
        ]
    if 'tarefas_galpao' not in st.session_state:
        st.session_state.tarefas_galpao = []
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

# Função de Login
def login_page():
    # Container centralizado simples
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Logo NEXO
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="background: #FF6B00; color: white; padding: 1rem 2rem; border-radius: 8px; display: inline-block; font-size: 24px; font-weight: bold; margin-bottom: 1rem;">
                NEXO
            </div>
            <p style="color: #888; margin: 0;">Núcleo de Excelência Operacional</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Acesso ao Sistema")
        
        # Formulário com Enter funcional
        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                # Validação de credenciais
                credenciais = {
                    "comercial": {"senha": "com123", "tipo": "comercial", "nome": "Equipe Comercial"},
                    "marcelao": {"senha": "log123", "tipo": "logistica", "nome": "Marcelão"},
                    "joao": {"senha": "campo123", "tipo": "campo", "nome": "João Silva"},
                    "carlos": {"senha": "campo123", "tipo": "campo", "nome": "Carlos Santos"},
                    "pedro": {"senha": "campo123", "tipo": "campo", "nome": "Pedro Lima"},
                    "boss": {"senha": "boss123", "tipo": "boss", "nome": "Diretor Executivo"}
                }
                
                if usuario in credenciais and credenciais[usuario]["senha"] == senha:
                    st.session_state.authenticated = True
                    st.session_state.user_type = credenciais[usuario]["tipo"]
                    st.session_state.user_name = credenciais[usuario]["nome"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")

# Função para carregar catálogo de produtos
def carregar_catalogo_produtos():
    try:
        df = pd.read_csv('/home/ubuntu/produtos_catalogo.csv')
        produtos = []
        for _, row in df.iterrows():
            produto = {
                'nome': row['produto'],
                'categoria': row['categoria'],
                'preco': float(row['valor/diária']) if pd.notna(row['valor/diária']) else 0.0
            }
            produtos.append(produto)
        return produtos
    except:
        # Fallback para produtos básicos se não conseguir carregar
        return [
            {"nome": "Tenda 3x3", "categoria": "estrutura", "preco": 150.0},
            {"nome": "Tenda 6x6", "categoria": "estrutura", "preco": 300.0},
            {"nome": "Mesa Redonda", "categoria": "mobiliário", "preco": 25.0},
            {"nome": "Cadeira Plástica", "categoria": "mobiliário", "preco": 5.0},
            {"nome": "Som Ambiente", "categoria": "eletrônico", "preco": 200.0},
            {"nome": "Iluminação LED", "categoria": "eletrônico", "preco": 100.0}
        ]

# Função de Loading
def show_loading():
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p style="color: var(--nexo-orange); font-weight: 600;">Carregando NEXO...</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)

# Função para classificação automática de regime
def classificar_regime(data_evento):
    agora = datetime.now()
    data_evento = datetime.strptime(data_evento, "%Y-%m-%d")
    
    # Diferença em horas
    diff_horas = (data_evento - agora).total_seconds() / 3600
    
    # Se é final de semana
    if data_evento.weekday() >= 5:  # Sábado ou Domingo
        return "3%"
    # Se é no mesmo dia (menos de 24h)
    elif diff_horas < 24:
        return "1%"
    else:
        return "Padrão"

# Função para gerar PDF do orçamento
def gerar_pdf_orcamento(dados):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Estilo personalizado para cabeçalho
    titulo_style = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B00'),
        alignment=1,  # Centralizado
        spaceAfter=30
    )
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'SubtituloCustom',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.black,
        alignment=1,
        spaceAfter=20
    )
    
    # Cabeçalho
    story.append(Paragraph("PRIMEIRA LINHA EVENTOS", titulo_style))
    story.append(Paragraph("NEXO - Núcleo de Excelência Operacional", subtitulo_style))
    story.append(Spacer(1, 20))
    
    # Linha separadora
    story.append(Paragraph("<hr/>", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph("ORÇAMENTO", titulo_style))
    story.append(Spacer(1, 20))
    
    # Dados do cliente
    cliente_data = [
        ["Cliente:", dados['cliente']],
        ["Evento:", dados['evento']],
        ["Data:", dados['data']],
        ["Local:", dados.get('local', 'Não informado')]
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FF6B00')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(cliente_table)
    story.append(Spacer(1, 30))
    
    # Tabela de itens
    story.append(Paragraph("ITENS DO ORÇAMENTO", subtitulo_style))
    story.append(Spacer(1, 10))
    
    # Cabeçalho da tabela
    table_data = [["Item", "Qtd", "Diárias", "Valor Unit.", "Total"]]
    
    # Itens
    for item in dados['itens']:
        table_data.append([
            item['produto'],
            str(item['quantidade']),
            str(item['diarias']),
            f"R$ {item['preco']:.2f}",
            f"R$ {item['total']:.2f}"
        ])
    
    # Total
    table_data.append(["", "", "", "TOTAL GERAL:", f"R$ {dados['total']:.2f}"])
    
    # Criar tabela
    items_table = Table(table_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B00')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Itens
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('ALIGN', (1, 1), (-1, -2), 'CENTER'),
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),
        
        # Total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FF6B00')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Cores alternadas nas linhas
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey])
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 40))
    
    # Rodapé
    story.append(Paragraph("<hr/>", styles['Normal']))
    story.append(Spacer(1, 10))
    
    rodape_style = ParagraphStyle(
        'RodapeCustom',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1
    )
    
    story.append(Paragraph("PRIMEIRA LINHA EVENTOS - NEXO", rodape_style))
    story.append(Paragraph("Núcleo de Excelência Operacional", rodape_style))
    story.append(Paragraph(f"Orçamento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", rodape_style))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
# Interface Comercial
def interface_comercial():
    st.title("NEXO - Comercial")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Bem-vindo, {st.session_state.user_name}!")
        opcao = st.selectbox("Navegação", [
            "Dashboard",
            "Novo Pedido",
            "Gestão de Pedidos",
            "Gerador de Orçamentos",
            "Catálogo de Produtos",
            "Acompanhamento de Eventos"
        ])
    
    if opcao == "Dashboard":
        st.header("Dashboard Comercial")
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Pedidos Ativos</h3>
                <h2 style="margin: 0.5rem 0;">12</h2>
                <p style="margin: 0; color: #22c55e;">↑ 15% vs mês anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Receita Mensal</h3>
                <h2 style="margin: 0.5rem 0;">R$ 45.200</h2>
                <p style="margin: 0; color: #22c55e;">↑ 8% vs mês anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Orçamentos</h3>
                <h2 style="margin: 0.5rem 0;">28</h2>
                <p style="margin: 0; color: #f59e0b;">↓ 3% vs mês anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Taxa Conversão</h3>
                <h2 style="margin: 0.5rem 0;">42.8%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 5% vs mês anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vendas por Mês")
            dados_vendas = pd.DataFrame({
                'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                'Vendas': [35000, 42000, 38000, 45000, 41000, 45200]
            })
            fig = px.line(dados_vendas, x='Mês', y='Vendas', 
                         color_discrete_sequence=['#FF6B00'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Pedidos por Status")
            dados_status = pd.DataFrame({
                'Status': ['Pendente', 'Em Andamento', 'Concluído'],
                'Quantidade': [5, 7, 15]
            })
            fig = px.pie(dados_status, values='Quantidade', names='Status',
                        color_discrete_sequence=['#FF6B00', '#ff8533', '#ffb366'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif opcao == "Novo Pedido":
        st.header("Novo Pedido")
        
        with st.form("novo_pedido_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Nome do Cliente")
                evento = st.text_input("Tipo de Evento")
                data_evento = st.date_input("Data do Evento")
                local = st.text_input("Local do Evento")
            
            with col2:
                contato = st.text_input("Contato/Telefone")
                email = st.text_input("E-mail")
                observacoes = st.text_area("Observações")
            
            # Seleção de produtos
            st.subheader("Produtos do Pedido")
            
            # Sistema dinâmico de produtos (sem limitação)
            if 'num_produtos_pedido' not in st.session_state:
                st.session_state.num_produtos_pedido = 3
            
            # Carregar catálogo atualizado
            produtos_catalogo = carregar_catalogo_produtos()
            produtos_selecionados = []
            
            for i in range(st.session_state.num_produtos_pedido):
                st.markdown(f"**Produto {i+1}:**")
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    produto = st.selectbox(f"Produto {i+1}", 
                                         [""] + [p["nome"] for p in produtos_catalogo],
                                         key=f"produto_{i}")
                
                with col2:
                    quantidade = st.number_input(f"Qtd", min_value=0, value=0, key=f"qtd_{i}")
                
                with col3:
                    diarias = st.number_input(f"Diárias", min_value=1, value=1, key=f"diarias_{i}")
                
                with col4:
                    if produto:
                        preco_produto = next((p["preco"] for p in produtos_catalogo if p["nome"] == produto), 0)
                        preco = st.number_input(f"Preço Unit.", value=preco_produto, key=f"preco_{i}")
                    else:
                        preco = st.number_input(f"Preço Unit.", value=0.0, key=f"preco_{i}")
                
                if produto and quantidade > 0:
                    produtos_selecionados.append({
                        "produto": produto,
                        "quantidade": quantidade,
                        "diarias": diarias,
                        "preco": preco,
                        "total": quantidade * diarias * preco
                    })
            
            # Botões para adicionar/remover produtos
            col1, col2 = st.columns(2)
            with col1:
                add_produto = st.form_submit_button("+ Adicionar Produto", key="add_produto_btn")
            with col2:
                remove_produto = st.form_submit_button("- Remover Produto", key="remove_produto_btn")
            
            # Classificação automática
            if data_evento:
                regime = classificar_regime(str(data_evento))
                st.info(f"Regime de Pagamento Classificado: **{regime}**")
            
            # Botão principal
            submitted = st.form_submit_button("✅ Criar Pedido", type="primary", key="criar_pedido_btn")
            
        # Processar ações fora do formulário
        if add_produto:
            st.session_state.num_produtos_pedido += 1
            st.rerun()
        
        if remove_produto and st.session_state.num_produtos_pedido > 1:
            st.session_state.num_produtos_pedido -= 1
            st.rerun()
            
        if submitted and cliente and evento:
            # Resetar contador de produtos para próximo pedido
            st.session_state.num_produtos_pedido = 3
            
            novo_pedido = {
                "id": len(st.session_state.pedidos) + 1,
                "cliente": cliente,
                "evento": evento,
                "data_evento": str(data_evento),
                "local": local,
                "contato": contato,
                "email": email,
                "observacoes": observacoes,
                "produtos": produtos_selecionados,
                "regime": regime if data_evento else "Padrão",
                "status": "Pendente",
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total": sum([p["total"] for p in produtos_selecionados])
            }
            
            st.session_state.pedidos.append(novo_pedido)
            st.success("Pedido criado com sucesso!")
            st.rerun()
    
    elif opcao == "Gestão de Pedidos":
        st.header("Gestão de Pedidos")
        
        if st.session_state.pedidos:
            for pedido in st.session_state.pedidos:
                with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} - {pedido['evento']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido['cliente']}")
                        st.write(f"**Evento:** {pedido['evento']}")
                        st.write(f"**Data:** {pedido['data_evento']}")
                        st.write(f"**Local:** {pedido['local']}")
                    
                    with col2:
                        st.write(f"**Contato:** {pedido['contato']}")
                        st.write(f"**E-mail:** {pedido['email']}")
                        st.write(f"**Regime:** {pedido['regime']}")
                        st.write(f"**Status:** {pedido['status']}")
                    
                    with col3:
                        st.write(f"**Total:** R$ {pedido['total']:.2f}")
                        st.write(f"**Criado em:** {pedido['data_criacao']}")
                        
                        # Botões de ação
                        if st.button(f"Editar Pedido #{pedido['id']}", key=f"edit_{pedido['id']}"):
                            st.info("Funcionalidade de edição em desenvolvimento")
                        
                        if st.button(f"Enviar para Logística", key=f"send_{pedido['id']}"):
                            pedido['status'] = "Na Logística"
                            st.success("Pedido enviado para logística!")
                            st.rerun()
                    
                    # Produtos do pedido
                    if pedido['produtos']:
                        st.subheader("Produtos:")
                        df_produtos = pd.DataFrame(pedido['produtos'])
                        st.dataframe(df_produtos, use_container_width=True)
        else:
            st.info("Nenhum pedido encontrado. Crie um novo pedido para começar.")
    
    elif opcao == "Gerador de Orçamentos":
        st.header("Gerador de Orçamentos")
        
        # Dados do cliente
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Nome do Cliente")
            evento = st.text_input("Tipo de Evento")
            data_evento = st.date_input("Data do Evento")
        
        with col2:
            local = st.text_input("Local do Evento")
            contato = st.text_input("Contato")
            observacoes = st.text_area("Observações")
        
        # Adição de itens
        st.subheader("Adicionar Itens ao Orçamento")
        
        if 'orcamento_itens' not in st.session_state:
            st.session_state.orcamento_itens = []
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            produtos_catalogo = carregar_catalogo_produtos()
            produto_selecionado = st.selectbox("Produto", 
                                             [p["nome"] for p in produtos_catalogo])
        
        with col2:
            quantidade = st.number_input("Qtd", min_value=1, value=1)
        
        with col3:
            diarias = st.number_input("Diárias", min_value=1, value=1)
        
        with col4:
            preco_produto = next((p["preco"] for p in produtos_catalogo if p["nome"] == produto_selecionado), 0)
            preco = st.number_input("Preço Unit.", value=preco_produto)
        
        with col5:
            if st.button("Adicionar Item"):
                item = {
                    "produto": produto_selecionado,
                    "quantidade": quantidade,
                    "diarias": diarias,
                    "preco": preco,
                    "total": quantidade * diarias * preco
                }
                st.session_state.orcamento_itens.append(item)
                st.rerun()
        
        # Validação de diárias vs datas
        if data_evento and st.session_state.orcamento_itens:
            dias_evento = 1  # Simplificado - pode ser calculado com data fim
            for item in st.session_state.orcamento_itens:
                if item['diarias'] != dias_evento:
                    st.warning(f"⚠️ Item '{item['produto']}': {item['diarias']} diárias não batem com {dias_evento} dia(s) do evento!")
        
        # Lista de itens adicionados
        if st.session_state.orcamento_itens:
            st.subheader("Itens do Orçamento")
            df_itens = pd.DataFrame(st.session_state.orcamento_itens)
            st.dataframe(df_itens, use_container_width=True)
            
            total_orcamento = sum([item['total'] for item in st.session_state.orcamento_itens])
            st.metric("Total do Orçamento", f"R$ {total_orcamento:.2f}")
            
            # Gerar PDF
            if st.button("Gerar Orçamento PDF"):
                if cliente and evento:
                    dados_orcamento = {
                        "cliente": cliente,
                        "evento": evento,
                        "data": str(data_evento),
                        "local": local,
                        "itens": st.session_state.orcamento_itens,
                        "total": total_orcamento
                    }
                    
                    pdf_buffer = gerar_pdf_orcamento(dados_orcamento)
                    
                    st.success("Orçamento gerado com sucesso!")
                    st.download_button(
                        label="📥 Download do Orçamento PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"Orcamento_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Preencha pelo menos o nome do cliente e tipo de evento!")
            
            if st.button("Limpar Orçamento"):
                st.session_state.orcamento_itens = []
                st.rerun()
    
    elif opcao == "Catálogo de Produtos":
        st.header("Catálogo de Produtos")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            produtos_catalogo = carregar_catalogo_produtos()
            categorias = list(set([p["categoria"] for p in produtos_catalogo]))
            categoria_filtro = st.selectbox("Filtrar por Categoria", ["Todas"] + categorias)
        
        with col2:
            busca = st.text_input("Buscar Produto")
        
        # Produtos filtrados
        produtos_filtrados = carregar_catalogo_produtos()
        
        if categoria_filtro != "Todas":
            produtos_filtrados = [p for p in produtos_filtrados if p["categoria"] == categoria_filtro]
        
        if busca:
            produtos_filtrados = [p for p in produtos_filtrados if busca.lower() in p["nome"].lower()]
        
        # Exibição em grid (3 colunas)
        cols = st.columns(3)
        
        for i, produto in enumerate(produtos_filtrados):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: var(--nexo-orange); margin: 0;">{produto['nome']}</h4>
                    <p style="margin: 0.5rem 0; color: #888;">{produto['categoria']}</p>
                    <h3 style="margin: 0; color: var(--nexo-white);">R$ {produto['preco']:.2f}</h3>
                </div>
                """, unsafe_allow_html=True)
        
        # Adicionar novo produto
        with st.expander("Adicionar Novo Produto"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                novo_nome = st.text_input("Nome do Produto")
            
            with col2:
                nova_categoria = st.text_input("Categoria")
            
            with col3:
                novo_preco = st.number_input("Preço", min_value=0.0, value=0.0)
            
            if st.button("Adicionar Produto"):
                if novo_nome and nova_categoria and novo_preco > 0:
                    novo_produto = {
                        "nome": novo_nome,
                        "categoria": nova_categoria,
                        "preco": novo_preco
                    }
                    st.session_state.produtos.append(novo_produto)
                    st.success("Produto adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos!")
    
    elif opcao == "Acompanhamento de Eventos":
        st.header("Acompanhamento de Eventos")
        
        # Eventos em andamento
        eventos_andamento = [p for p in st.session_state.pedidos if p['status'] in ['Em Andamento', 'Na Logística']]
        
        if eventos_andamento:
            for evento in eventos_andamento:
                with st.expander(f"🎪 {evento['evento']} - {evento['cliente']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Data:** {evento['data_evento']}")
                        st.write(f"**Local:** {evento['local']}")
                        st.write(f"**Status:** {evento['status']}")
                    
                    with col2:
                        st.write(f"**Contato:** {evento['contato']}")
                        st.write(f"**Total:** R$ {evento['total']:.2f}")
                    
                    # Status do evento
                    st.subheader("Status da Execução")
                    
                    status_opcoes = ["Não Iniciado", "Montagem", "Em Andamento", "Desmontagem", "Finalizado"]
                    status_atual = st.selectbox(f"Status do Evento {evento['id']}", 
                                              status_opcoes, 
                                              key=f"status_evento_{evento['id']}")
                    
                    # Observações da execução
                    st.subheader("Observações da Execução")
                    observacao = st.text_area(f"Observações do evento {evento['id']}", 
                                            key=f"obs_{evento['id']}")
                    
                    if st.button(f"Salvar Observações", key=f"save_obs_{evento['id']}"):
                        if observacao:
                            st.success("Observações salvas!")
                        else:
                            st.warning("Digite uma observação!")
        else:
            st.info("Nenhum evento em andamento no momento.")

# Interface Logística
def interface_logistica():
    st.title("NEXO - Logística")
    
    with st.sidebar:
        st.markdown(f"### Bem-vindo, {st.session_state.user_name}!")
        opcao = st.selectbox("Navegação", [
            "Dashboard",
            "Gestão de Pedidos",
            "Gestão de Equipes",
            "Tarefas de Galpão",
            "Documentos"
        ])
        
        if st.button("🚪 Sair do Sistema"):
            st.session_state.authenticated = False
            st.rerun()
    
    if opcao == "Dashboard":
        st.header("Dashboard Logístico")
        
        # KPIs Logísticos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Entregas Hoje</h3>
                <h2 style="margin: 0.5rem 0;">5</h2>
                <p style="margin: 0; color: #22c55e;">↑ 2 vs ontem</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Equipes Ativas</h3>
                <h2 style="margin: 0.5rem 0;">0/5</h2>
                <p style="margin: 0; color: #f59e0b;">Nenhuma equipe cadastrada</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Documentos Pendentes</h3>
                <h2 style="margin: 0.5rem 0;">3</h2>
                <p style="margin: 0; color: #ef4444;">Requer atenção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Eficiência</h3>
                <h2 style="margin: 0.5rem 0;">94%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 2% vs semana anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Próximas entregas
        st.subheader("Próximas Entregas (48h)")
        
        proximas_entregas = [
            {"cliente": "Hotel Ramada", "evento": "Convenção Médica", "data": "Hoje 14:00", "equipe": "Não designada"},
            {"cliente": "Clube Atlético", "evento": "Festa Junina", "data": "Amanhã 08:00", "equipe": "Não designada"},
            {"cliente": "Empresa XYZ", "evento": "Confraternização", "data": "Amanhã 16:00", "equipe": "Não designada"}
        ]
        
        for entrega in proximas_entregas:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{entrega['cliente']}**")
            with col2:
                st.write(entrega['evento'])
            with col3:
                st.write(entrega['data'])
            with col4:
                if entrega['equipe'] == "Não designada":
                    st.warning("⚠️ Sem equipe")
                else:
                    st.success("✅ Designada")
        
        # Alertas
        st.subheader("Alertas Operacionais")
        
        alertas = [
            {"tipo": "warning", "mensagem": "3 documentos pendentes de upload"},
            {"tipo": "info", "mensagem": "Nenhuma equipe cadastrada no sistema"},
            {"tipo": "error", "mensagem": "5 entregas sem equipe designada"}
        ]
        
        for alerta in alertas:
            if alerta['tipo'] == 'warning':
                st.warning(f"⚠️ {alerta['mensagem']}")
            elif alerta['tipo'] == 'info':
                st.info(f"ℹ️ {alerta['mensagem']}")
            elif alerta['tipo'] == 'error':
                st.error(f"🚨 {alerta['mensagem']}")
    
    elif opcao == "Gestão de Pedidos":
        st.header("Gestão de Pedidos - Logística")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.selectbox("Filtrar por Status", 
                                       ["Todos", "Na Logística", "Preparando", "No Campo", "Entregue", "Concluído"],
                                       key="filtro_status_logistica")
        with col2:
            filtro_cliente = st.selectbox("Filtrar por Cliente", 
                                        ["Todos"] + list(set([p['cliente'] for p in st.session_state.pedidos])),
                                        key="filtro_cliente_logistica")
        
        # Pedidos vindos do comercial
        pedidos_filtrados = st.session_state.pedidos
        
        if filtro_status != "Todos":
            pedidos_filtrados = [p for p in pedidos_filtrados if p['status'] == filtro_status]
        
        if filtro_cliente != "Todos":
            pedidos_filtrados = [p for p in pedidos_filtrados if p['cliente'] == filtro_cliente]
        
        if pedidos_filtrados:
            for i, pedido in enumerate(pedidos_filtrados):
                with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} - {pedido['evento']} - Status: {pedido['status']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido['cliente']}")
                        st.write(f"**Evento:** {pedido['evento']}")
                        st.write(f"**Data do Evento:** {pedido['data_evento']}")
                        st.write(f"**Local:** {pedido['local']}")
                        st.write(f"**Regime:** {pedido['regime']}")
                    
                    with col2:
                        st.write(f"**Contato:** {pedido['contato']}")
                        st.write(f"**E-mail:** {pedido['email']}")
                        st.write(f"**Total:** R$ {pedido['total']:.2f}")
                        st.write(f"**Status Atual:** {pedido['status']}")
                    
                    # Produtos do pedido
                    if pedido['produtos']:
                        st.subheader("Produtos do Pedido:")
                        df_produtos = pd.DataFrame(pedido['produtos'])
                        st.dataframe(df_produtos, use_container_width=True)
                    
                    # Datas específicas de logística
                    st.subheader("Configurações de Logística")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        data_entrega = st.date_input(f"Data de Entrega", key=f"data_entrega_log_{pedido['id']}_{i}")
                        hora_entrega = st.time_input(f"Hora de Entrega", key=f"hora_entrega_log_{pedido['id']}_{i}")
                        responsavel_recepcao = st.text_input(f"Responsável pela Recepção", key=f"resp_recepcao_log_{pedido['id']}_{i}")
                    
                    with col2:
                        data_recolhimento = st.date_input(f"Data de Recolhimento", key=f"data_recolhimento_log_{pedido['id']}_{i}")
                        hora_recolhimento = st.time_input(f"Hora de Recolhimento", key=f"hora_recolhimento_log_{pedido['id']}_{i}")
                        responsavel_liberacao = st.text_input(f"Responsável pela Liberação", key=f"resp_liberacao_log_{pedido['id']}_{i}")
                    
                    # Observações específicas
                    observacoes_logistica = st.text_area(f"Observações da Logística", key=f"obs_logistica_{pedido['id']}_{i}")
                    
                    # Alocação de equipes
                    st.subheader("Alocação de Equipes")
                    
                    if 'equipes' not in st.session_state or not st.session_state.equipes:
                        st.warning("⚠️ Nenhuma equipe cadastrada. Cadastre equipes na seção 'Gestão de Equipes'")
                    else:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Equipe para Entrega:**")
                            equipe_entrega = st.multiselect(
                                "Selecionar colaboradores para entrega",
                                [e['nome'] for e in st.session_state.equipes if e['status'] == 'Disponível'],
                                key=f"equipe_entrega_log_{pedido['id']}_{i}"
                            )
                        
                        with col2:
                            st.write("**Equipe para Recolhimento:**")
                            equipe_recolhimento = st.multiselect(
                                "Selecionar colaboradores para recolhimento",
                                [e['nome'] for e in st.session_state.equipes if e['status'] == 'Disponível'],
                                key=f"equipe_recolhimento_log_{pedido['id']}_{i}"
                            )
                    
                    # Ações do pedido
                    st.subheader("Ações")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📋 Preparar Pedido", key=f"preparar_pedido_{pedido['id']}_{i}"):
                            pedido['status'] = "Preparando"
                            st.success("Pedido marcado como 'Preparando'!")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🚚 Enviar para Campo", key=f"enviar_campo_{pedido['id']}_{i}"):
                            if equipe_entrega:
                                pedido['status'] = "No Campo"
                                pedido['equipe_entrega'] = equipe_entrega
                                st.success("Pedido enviado para o campo!")
                                st.rerun()
                            else:
                                st.error("Selecione uma equipe para entrega!")
                    
                    with col3:
                        if st.button(f"📄 Gerar Documentos", key=f"gerar_docs_{pedido['id']}_{i}"):
                            st.info("Documentos serão gerados na seção 'Documentos'")
        else:
            st.info("Nenhum pedido encontrado com os filtros selecionados.")
    
    elif opcao == "Gestão de Equipes":
        st.header("Gestão de Equipes")
        
        # Inicializar equipes vazias
        if 'equipes' not in st.session_state:
            st.session_state.equipes = []
        
        # Adicionar novo colaborador
        st.subheader("Adicionar Novo Colaborador")
        
        with st.form("novo_colaborador_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo")
                especialidade = st.selectbox("Especialidade", [
                    "Montagem", "Elétrica", "Logística", "Decoração", 
                    "Supervisão", "Som e Luz", "Segurança", "Limpeza"
                ])
                telefone = st.text_input("Telefone")
            
            with col2:
                email = st.text_input("E-mail")
                status = st.selectbox("Status Inicial", ["Disponível", "Ocupado", "Férias", "Afastado"])
                observacoes = st.text_area("Observações")
            
            submitted = st.form_submit_button("✅ Adicionar Colaborador", type="primary")
            
            if submitted and nome:
                novo_colaborador = {
                    "id": len(st.session_state.equipes) + 1,
                    "nome": nome,
                    "especialidade": especialidade,
                    "telefone": telefone,
                    "email": email,
                    "status": status,
                    "observacoes": observacoes,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
                    "trabalhos_concluidos": 0,
                    "avaliacao_media": 0.0
                }
                
                st.session_state.equipes.append(novo_colaborador)
                st.success(f"Colaborador {nome} adicionado com sucesso!")
                st.rerun()
        
        # Lista de colaboradores
        st.subheader("Equipe Atual")
        
        if st.session_state.equipes:
            for i, colaborador in enumerate(st.session_state.equipes):
                with st.expander(f"{colaborador['nome']} - {colaborador['especialidade']} ({colaborador['status']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Nome:** {colaborador['nome']}")
                        st.write(f"**Especialidade:** {colaborador['especialidade']}")
                        st.write(f"**Status:** {colaborador['status']}")
                    
                    with col2:
                        st.write(f"**Telefone:** {colaborador['telefone']}")
                        st.write(f"**E-mail:** {colaborador['email']}")
                        st.write(f"**Cadastrado em:** {colaborador['data_cadastro']}")
                    
                    with col3:
                        st.write(f"**Trabalhos:** {colaborador['trabalhos_concluidos']}")
                        st.write(f"**Avaliação:** {colaborador['avaliacao_media']:.1f}/5.0")
                        
                        # Alterar status
                        novo_status = st.selectbox(
                            "Alterar Status",
                            ["Disponível", "Ocupado", "Férias", "Afastado"],
                            index=["Disponível", "Ocupado", "Férias", "Afastado"].index(colaborador['status']),
                            key=f"status_equipe_{colaborador['id']}_{i}"
                        )
                        
                        if novo_status != colaborador['status']:
                            colaborador['status'] = novo_status
                            st.success("Status atualizado!")
                            st.rerun()
                    
                    # Botões de ação
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"✏️ Editar", key=f"edit_colaborador_{colaborador['id']}_{i}"):
                            st.session_state[f'editing_{colaborador["id"]}'] = True
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🗑️ Excluir", key=f"delete_colaborador_{colaborador['id']}_{i}"):
                            st.session_state.equipes.remove(colaborador)
                            st.success("Colaborador removido!")
                            st.rerun()
                    
                    # Formulário de edição
                    if st.session_state.get(f'editing_{colaborador["id"]}', False):
                        st.subheader("Editar Colaborador")
                        
                        with st.form(f"edit_form_{colaborador['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                novo_nome = st.text_input("Nome", value=colaborador['nome'])
                                nova_especialidade = st.selectbox("Especialidade", 
                                                                ["Montagem", "Elétrica", "Logística", "Decoração", 
                                                                 "Supervisão", "Som e Luz", "Segurança", "Limpeza"],
                                                                index=["Montagem", "Elétrica", "Logística", "Decoração", 
                                                                       "Supervisão", "Som e Luz", "Segurança", "Limpeza"].index(colaborador['especialidade']))
                                novo_telefone = st.text_input("Telefone", value=colaborador['telefone'])
                            
                            with col2:
                                novo_email = st.text_input("E-mail", value=colaborador['email'])
                                novas_observacoes = st.text_area("Observações", value=colaborador['observacoes'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Salvar Alterações"):
                                    colaborador['nome'] = novo_nome
                                    colaborador['especialidade'] = nova_especialidade
                                    colaborador['telefone'] = novo_telefone
                                    colaborador['email'] = novo_email
                                    colaborador['observacoes'] = novas_observacoes
                                    st.session_state[f'editing_{colaborador["id"]}'] = False
                                    st.success("Colaborador atualizado!")
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f'editing_{colaborador["id"]}'] = False
                                    st.rerun()
        else:
            st.info("Nenhum colaborador cadastrado. Adicione colaboradores usando o formulário acima.")
    
    elif opcao == "Tarefas de Galpão":
        st.header("Tarefas de Galpão")
        
        # Criar nova tarefa
        st.subheader("Nova Tarefa")
        
        with st.form("nova_tarefa"):
            col1, col2 = st.columns(2)
            
            with col1:
                titulo = st.text_input("Título da Tarefa")
                tipo_tarefa = st.selectbox("Tipo de Tarefa", [
                    "Limpeza de Equipamentos",
                    "Organização do Estoque",
                    "Manutenção Preventiva",
                    "Inventário",
                    "Preparação de Material",
                    "Controle de Qualidade",
                    "Outros"
                ])
                prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])
            
            with col2:
                if st.session_state.equipes:
                    responsavel = st.selectbox("Responsável", 
                                             ["Não atribuído"] + [e['nome'] for e in st.session_state.equipes])
                else:
                    responsavel = st.selectbox("Responsável", ["Não atribuído"])
                    st.warning("⚠️ Nenhuma equipe cadastrada")
                
                prazo = st.date_input("Prazo")
                descricao = st.text_area("Descrição da Tarefa")
            
            submitted = st.form_submit_button("Criar Tarefa")
            
            if submitted and titulo:
                nova_tarefa = {
                    "id": len(st.session_state.tarefas_galpao) + 1,
                    "titulo": titulo,
                    "tipo": tipo_tarefa,
                    "descricao": descricao,
                    "responsavel": responsavel,
                    "prioridade": prioridade,
                    "prazo": str(prazo),
                    "status": "Pendente",
                    "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "data_conclusao": None
                }
                
                st.session_state.tarefas_galpao.append(nova_tarefa)
                st.success("Tarefa criada com sucesso!")
                st.rerun()
        
        # Lista de tarefas
        st.subheader("Tarefas Ativas")
        
        if st.session_state.tarefas_galpao:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_status = st.selectbox("Filtrar por Status", 
                                           ["Todos", "Pendente", "Em Andamento", "Concluída"])
            
            with col2:
                filtro_prioridade = st.selectbox("Filtrar por Prioridade", 
                                                ["Todas", "Baixa", "Média", "Alta", "Urgente"])
            
            with col3:
                filtro_tipo = st.selectbox("Filtrar por Tipo", 
                                         ["Todos"] + [
                                             "Limpeza de Equipamentos",
                                             "Organização do Estoque",
                                             "Manutenção Preventiva",
                                             "Inventário",
                                             "Preparação de Material",
                                             "Controle de Qualidade",
                                             "Outros"
                                         ])
            
            # Aplicar filtros
            tarefas_filtradas = st.session_state.tarefas_galpao
            
            if filtro_status != "Todos":
                tarefas_filtradas = [t for t in tarefas_filtradas if t['status'] == filtro_status]
            
            if filtro_prioridade != "Todas":
                tarefas_filtradas = [t for t in tarefas_filtradas if t['prioridade'] == filtro_prioridade]
            
            if filtro_tipo != "Todos":
                tarefas_filtradas = [t for t in tarefas_filtradas if t['tipo'] == filtro_tipo]
            
            # Exibir tarefas
            for tarefa in tarefas_filtradas:
                # Cor da prioridade
                cor_prioridade = {
                    "Baixa": "#22c55e",
                    "Média": "#f59e0b", 
                    "Alta": "#ef4444",
                    "Urgente": "#dc2626"
                }
                
                with st.expander(f"#{tarefa['id']} - {tarefa['titulo']} ({tarefa['status']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Tipo:** {tarefa['tipo']}")
                        st.write(f"**Responsável:** {tarefa['responsavel']}")
                        st.markdown(f"**Prioridade:** <span style='color: {cor_prioridade[tarefa['prioridade']]}'>{tarefa['prioridade']}</span>", 
                                  unsafe_allow_html=True)
                    
                    with col2:
                        st.write(f"**Prazo:** {tarefa['prazo']}")
                        st.write(f"**Criada em:** {tarefa['data_criacao']}")
                        st.write(f"**Status:** {tarefa['status']}")
                    
                    with col3:
                        # Alterar status
                        novo_status = st.selectbox(
                            "Alterar Status",
                            ["Pendente", "Em Andamento", "Concluída"],
                            index=["Pendente", "Em Andamento", "Concluída"].index(tarefa['status']),
                            key=f"status_tarefa_{tarefa['id']}"
                        )
                        
                        if st.button(f"Atualizar", key=f"update_tarefa_{tarefa['id']}"):
                            tarefa['status'] = novo_status
                            if novo_status == "Concluída":
                                tarefa['data_conclusao'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.success("Status atualizado!")
                            st.rerun()
                    
                    if tarefa['descricao']:
                        st.write(f"**Descrição:** {tarefa['descricao']}")
                    
                    if tarefa['data_conclusao']:
                        st.success(f"✅ Concluída em: {tarefa['data_conclusao']}")
        else:
            st.info("Nenhuma tarefa criada. Crie uma nova tarefa para começar.")
    
    elif opcao == "Documentos":
        st.header("Gestão de Documentos")
        
        # Documentos obrigatórios
        st.subheader("Documentos Obrigatórios")
        
        documentos_obrigatorios = [
            "Ordem de Separação",
            "Confirmação de Reserva", 
            "Romaneio de Entrega",
            "Termo de Recebimento",
            "Ordem de Recolhimento",
            "Relatório de Inspeção"
        ]
        
        for doc in documentos_obrigatorios:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"📄 **{doc}**")
            
            with col2:
                uploaded_file = st.file_uploader(
                    f"Upload {doc}",
                    type=['pdf', 'jpg', 'png', 'docx'],
                    key=f"upload_{doc.replace(' ', '_').lower()}"
                )
            
            with col3:
                if uploaded_file:
                    st.success("✅ Anexado")
                else:
                    st.warning("⚠️ Pendente")
        
        # Documentos do local
        st.subheader("Documentos do Local")
        
        documentos_local = [
            "Planta do Local",
            "Autorização de Uso",
            "Normas de Segurança",
            "Contato Responsável"
        ]
        
        for doc in documentos_local:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"🏢 **{doc}**")
            
            with col2:
                uploaded_file = st.file_uploader(
                    f"Upload {doc}",
                    type=['pdf', 'jpg', 'png', 'docx'],
                    key=f"upload_local_{doc.replace(' ', '_').lower()}"
                )
            
            with col3:
                if uploaded_file:
                    st.success("✅ Anexado")
                else:
                    st.info("📋 Opcional")
        
        # Documentos técnicos
        st.subheader("Documentos Técnicos")
        
        documentos_tecnicos = [
            "Manual de Equipamentos",
            "Certificados de Segurança",
            "Laudos Técnicos",
            "Especificações Técnicas"
        ]
        
        for doc in documentos_tecnicos:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"🔧 **{doc}**")
            
            with col2:
                uploaded_file = st.file_uploader(
                    f"Upload {doc}",
                    type=['pdf', 'jpg', 'png', 'docx'],
                    key=f"upload_tecnico_{doc.replace(' ', '_').lower()}"
                )
            
            with col3:
                if uploaded_file:
                    st.success("✅ Anexado")
                else:
                    st.info("📋 Opcional")
        
        # Geração automática de documentos
        st.subheader("Geração Automática")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Gerar Ordem de Separação"):
                st.success("Ordem de Separação gerada automaticamente!")
                st.info("Documento baseado nos pedidos ativos")
        
        with col2:
            if st.button("🚚 Gerar Romaneio de Entrega"):
                st.success("Romaneio de Entrega gerado automaticamente!")
                st.info("Documento baseado nas entregas do dia")
    
    if opcao == "Dashboard":
        st.header("Dashboard Logístico")
        
        # KPIs Logísticos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Entregas Hoje</h3>
                <h2 style="margin: 0.5rem 0;">5</h2>
                <p style="margin: 0; color: #22c55e;">3 concluídas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Equipes Ativas</h3>
                <h2 style="margin: 0.5rem 0;">4/5</h2>
                <p style="margin: 0; color: #f59e0b;">1 disponível</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Docs Pendentes</h3>
                <h2 style="margin: 0.5rem 0;">3</h2>
                <p style="margin: 0; color: #ef4444;">Requer atenção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Eficiência</h3>
                <h2 style="margin: 0.5rem 0;">94%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 2% vs semana anterior</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Próximas entregas
        st.subheader("Próximas Entregas (48h)")
        
        proximas_entregas = [
            {"cliente": "Hotel Ramada", "data": "Hoje 14:00", "equipe": "João + Carlos", "status": "Preparando"},
            {"cliente": "Clube Náutico", "data": "Amanhã 09:00", "equipe": "Pedro + Ana", "status": "Agendado"},
            {"cliente": "Residência Silva", "data": "Amanhã 16:00", "equipe": "A definir", "status": "Pendente"}
        ]
        
        for entrega in proximas_entregas:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{entrega['cliente']}**")
            
            with col2:
                st.write(entrega['data'])
            
            with col3:
                st.write(entrega['equipe'])
            
            with col4:
                if entrega['status'] == "Preparando":
                    st.markdown('<span class="status-badge status-andamento">Preparando</span>', unsafe_allow_html=True)
                elif entrega['status'] == "Agendado":
                    st.markdown('<span class="status-badge status-concluido">Agendado</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-badge status-pendente">Pendente</span>', unsafe_allow_html=True)
    
    elif opcao == "Gestão de Pedidos":
        st.header("Gestão de Pedidos")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            status_filtro = st.selectbox("Filtrar por Status", 
                                       ["Todos", "Na Logística", "Documentos Pendentes", "Pronto para Campo"])
        
        with col2:
            regime_filtro = st.selectbox("Filtrar por Regime", 
                                       ["Todos", "Padrão", "1%", "3%"])
        
        # Pedidos na logística
        pedidos_logistica = [p for p in st.session_state.pedidos if p['status'] in ['Na Logística', 'Documentos Pendentes']]
        
        if pedidos_logistica:
            for pedido in pedidos_logistica:
                with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} - Regime: {pedido['regime']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {pedido['cliente']}")
                        st.write(f"**Evento:** {pedido['evento']}")
                        st.write(f"**Data Evento:** {pedido['data_evento']}")
                        st.write(f"**Local:** {pedido['local']}")
                        
                        # Datas específicas de logística
                        st.subheader("Datas de Logística")
                        data_entrega = st.date_input(f"Data de Entrega", key=f"data_entrega_{pedido['id']}")
                        hora_entrega = st.time_input(f"Horário de Entrega", key=f"hora_entrega_{pedido['id']}")
                        
                        data_recolhimento = st.date_input(f"Data de Recolhimento", key=f"data_recolhimento_{pedido['id']}")
                        hora_recolhimento = st.time_input(f"Horário de Recolhimento", key=f"hora_recolhimento_{pedido['id']}")
                    
                    with col2:
                        st.write(f"**Regime:** {pedido['regime']}")
                        st.write(f"**Total:** R$ {pedido['total']:.2f}")
                        
                        # Alocação de equipe
                        st.subheader("Alocação de Equipe")
                        equipes_disponiveis = [e["nome"] for e in st.session_state.equipes if e["status"] == "Disponível"]
                        
                        equipe_entrega = st.multiselect(f"Equipe para Entrega", 
                                                      equipes_disponiveis, 
                                                      key=f"equipe_entrega_{pedido['id']}")
                        
                        equipe_recolhimento = st.multiselect(f"Equipe para Recolhimento", 
                                                           equipes_disponiveis, 
                                                           key=f"equipe_recolhimento_{pedido['id']}")
                        
                        # Responsáveis
                        responsavel_recepcao = st.text_input(f"Responsável pela Recepção", 
                                                           key=f"resp_recepcao_{pedido['id']}")
                        responsavel_liberacao = st.text_input(f"Responsável pela Liberação", 
                                                            key=f"resp_liberacao_{pedido['id']}")
                    
                    # Documentos obrigatórios
                    st.subheader("Documentos Obrigatórios")
                    
                    documentos = [
                        "Ordem de Separação",
                        "Confirmação de Reserva", 
                        "Romaneio de Entrega",
                        "Termo de Recebimento",
                        "Ordem de Recolhimento",
                        "Relatório de Inspeção"
                    ]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    for i, doc in enumerate(documentos):
                        with [col1, col2, col3][i % 3]:
                            uploaded_file = st.file_uploader(f"{doc}", 
                                                           type=['pdf', 'jpg', 'png'], 
                                                           key=f"doc_{doc}_{pedido['id']}")
                            
                            if uploaded_file:
                                st.success(f"✅ {doc} anexado")
                            else:
                                st.warning(f"⏳ {doc} pendente")
                    
                    # Observações
                    observacoes_logistica = st.text_area(f"Observações da Logística", 
                                                        key=f"obs_log_{pedido['id']}")
                    
                    # Botões de ação
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"Gerar Documentos Automáticos", key=f"gerar_docs_{pedido['id']}"):
                            st.success("Documentos gerados automaticamente!")
                    
                    with col2:
                        if st.button(f"Salvar Informações", key=f"salvar_{pedido['id']}"):
                            st.success("Informações salvas!")
                    
                    with col3:
                        if st.button(f"Enviar para Campo", key=f"enviar_campo_{pedido['id']}"):
                            pedido['status'] = "Pronto para Campo"
                            st.success("Pedido enviado para equipe de campo!")
                            st.rerun()
        else:
            st.info("Nenhum pedido na logística no momento.")
    
    elif opcao == "Gestão de Equipes":
        st.header("Gestão de Equipes")
        
        # Status das equipes
        st.subheader("Status da Equipe")
        
        for equipe in st.session_state.equipes:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{equipe['nome']}**")
            
            with col2:
                st.write(equipe['especialidade'])
            
            with col3:
                if equipe['status'] == "Disponível":
                    st.markdown('<span class="status-badge status-concluido">Disponível</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-badge status-urgente">Ocupado</span>', unsafe_allow_html=True)
            
            with col4:
                novo_status = st.selectbox("Alterar Status", 
                                         ["Disponível", "Ocupado"], 
                                         index=0 if equipe['status'] == "Disponível" else 1,
                                         key=f"status_{equipe['nome']}")
                
                if novo_status != equipe['status']:
                    equipe['status'] = novo_status
                    st.rerun()
        
        # Adicionar novo colaborador
        with st.expander("Adicionar Novo Colaborador"):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_nome = st.text_input("Nome do Colaborador")
                nova_especialidade = st.selectbox("Especialidade", 
                                                ["Montagem", "Elétrica", "Logística", "Decoração", "Supervisão"])
            
            with col2:
                novo_telefone = st.text_input("Telefone")
                nova_observacao = st.text_area("Observações")
            
            if st.button("Adicionar Colaborador"):
                if novo_nome and nova_especialidade:
                    novo_colaborador = {
                        "nome": novo_nome,
                        "especialidade": nova_especialidade,
                        "status": "Disponível",
                        "telefone": novo_telefone,
                        "observacao": nova_observacao
                    }
                    st.session_state.equipes.append(novo_colaborador)
                    st.success("Colaborador adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha pelo menos nome e especialidade!")
    
    elif opcao == "Tarefas de Galpão":
        st.header("Tarefas de Galpão")
        
        # Criar nova tarefa
        with st.expander("Nova Tarefa de Galpão"):
            col1, col2 = st.columns(2)
            
            with col1:
                tipo_tarefa = st.selectbox("Tipo de Tarefa", [
                    "Limpeza de Equipamentos",
                    "Organização do Estoque",
                    "Manutenção Preventiva",
                    "Inventário",
                    "Preparação de Material",
                    "Controle de Qualidade",
                    "Outros"
                ])
                
                responsavel = st.selectbox("Responsável", 
                                         [e["nome"] for e in st.session_state.equipes])
            
            with col2:
                prazo = st.date_input("Prazo")
                prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])
            
            descricao = st.text_area("Descrição da Tarefa")
            
            if st.button("Criar Tarefa"):
                if tipo_tarefa and responsavel and descricao:
                    nova_tarefa = {
                        "id": len(st.session_state.tarefas_galpao) + 1,
                        "tipo": tipo_tarefa,
                        "responsavel": responsavel,
                        "prazo": str(prazo),
                        "prioridade": prioridade,
                        "descricao": descricao,
                        "status": "Pendente",
                        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.tarefas_galpao.append(nova_tarefa)
                    st.success("Tarefa criada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios!")
        
        # Lista de tarefas
        st.subheader("Tarefas Ativas")
        
        if st.session_state.tarefas_galpao:
            for tarefa in st.session_state.tarefas_galpao:
                with st.expander(f"Tarefa #{tarefa['id']} - {tarefa['tipo']} - {tarefa['responsavel']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Tipo:** {tarefa['tipo']}")
                        st.write(f"**Responsável:** {tarefa['responsavel']}")
                        st.write(f"**Prazo:** {tarefa['prazo']}")
                        st.write(f"**Criada em:** {tarefa['data_criacao']}")
                    
                    with col2:
                        st.write(f"**Prioridade:** {tarefa['prioridade']}")
                        st.write(f"**Status:** {tarefa['status']}")
                        
                        novo_status = st.selectbox("Alterar Status", 
                                                 ["Pendente", "Em Andamento", "Concluída"], 
                                                 index=["Pendente", "Em Andamento", "Concluída"].index(tarefa['status']),
                                                 key=f"status_tarefa_{tarefa['id']}")
                        
                        if novo_status != tarefa['status']:
                            tarefa['status'] = novo_status
                            st.rerun()
                    
                    st.write(f"**Descrição:** {tarefa['descricao']}")
        else:
            st.info("Nenhuma tarefa de galpão criada ainda.")
    
    elif opcao == "Documentos":
        st.header("Gestão de Documentos")
        
        # Seleção de pedido
        pedidos_com_docs = [p for p in st.session_state.pedidos if p['status'] in ['Na Logística', 'Pronto para Campo']]
        
        if pedidos_com_docs:
            pedido_selecionado = st.selectbox("Selecionar Pedido", 
                                            [f"#{p['id']} - {p['cliente']} - {p['evento']}" for p in pedidos_com_docs])
            
            if pedido_selecionado:
                pedido_id = int(pedido_selecionado.split('#')[1].split(' -')[0])
                pedido = next((p for p in st.session_state.pedidos if p['id'] == pedido_id), None)
                
                if pedido:
                    st.subheader(f"Documentos do Pedido #{pedido['id']}")
                    
                    # Upload de documentos por categoria
                    categorias_docs = {
                        "Documentos Obrigatórios": [
                            "Ordem de Separação",
                            "Confirmação de Reserva",
                            "Romaneio de Entrega",
                            "Termo de Recebimento",
                            "Ordem de Recolhimento",
                            "Relatório de Inspeção"
                        ],
                        "Documentos do Local": [
                            "Autorização do Local",
                            "Planta/Layout",
                            "Fotos do Local",
                            "Contatos Importantes"
                        ],
                        "Documentos Técnicos": [
                            "Diagrama Elétrico",
                            "Certificados de Segurança",
                            "Especificações Técnicas"
                        ]
                    }
                    
                    for categoria, docs in categorias_docs.items():
                        with st.expander(categoria):
                            cols = st.columns(2)
                            
                            for i, doc in enumerate(docs):
                                with cols[i % 2]:
                                    uploaded_file = st.file_uploader(f"{doc}", 
                                                                   type=['pdf', 'jpg', 'png', 'docx'], 
                                                                   key=f"doc_{categoria}_{doc}_{pedido['id']}")
                                    
                                    if uploaded_file:
                                        st.success(f"✅ {doc} anexado")
                                        
                                        # Botão de download
                                        st.download_button(
                                            label=f"📥 Download {doc}",
                                            data=uploaded_file.getvalue(),
                                            file_name=uploaded_file.name,
                                            mime=uploaded_file.type
                                        )
                                    else:
                                        st.warning(f"⏳ {doc} pendente")
                    
                    # Geração automática de documentos
                    st.subheader("Geração Automática")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Gerar Ordem de Separação"):
                            st.success("Ordem de Separação gerada!")
                    
                    with col2:
                        if st.button("Gerar Romaneio de Entrega"):
                            st.success("Romaneio de Entrega gerado!")
                    
                    with col3:
                        if st.button("Gerar Todos os Documentos"):
                            st.success("Todos os documentos foram gerados!")
        else:
            st.info("Nenhum pedido disponível para gestão de documentos.")
    
    elif opcao == "Chat Integrado":
        st.header("Chat Integrado")
        
        # Seleção de destinatário
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_conversa = st.selectbox("Tipo de Conversa", ["Por Setor", "Por Colaborador"])
        
        with col2:
            if tipo_conversa == "Por Setor":
                destinatario = st.selectbox("Setor", ["Comercial", "Campo", "Boss", "Geral"])
            else:
                destinatario = st.selectbox("Colaborador", [e["nome"] for e in st.session_state.equipes])
        
        # Container do chat
        st.markdown(f"""
        <div class="chat-container">
            <h4 style="color: var(--nexo-orange); margin-bottom: 1rem;">Conversa com {destinatario}</h4>
            <div class="chat-message">
                <strong>Marcelão:</strong> Pessoal, material do evento de amanhã já está separado
            </div>
            <div class="chat-message">
                <strong>João:</strong> Perfeito! Que horas vamos carregar o caminhão?
            </div>
            <div class="chat-message">
                <strong>Marcelão:</strong> 7h da manhã. Chegada no local às 8h30
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Input de mensagem
        col1, col2 = st.columns([4, 1])
        
        with col1:
            nova_mensagem = st.text_input("Digite sua mensagem...", key="chat_logistica")
        
        with col2:
            if st.button("Enviar"):
                if nova_mensagem:
                    st.success("Mensagem enviada!")
                    st.rerun()

# Interface Equipe de Campo
def interface_campo():
    st.title("NEXO - Equipe de Campo")
    
    with st.sidebar:
        st.markdown(f"### Bem-vindo, {st.session_state.user_name}!")
        opcao = st.selectbox("Navegação", [
            "Pedidos Designados",
            "Trabalho Atual",
            "Histórico"
        ])
        
        if st.button("🚪 Sair do Sistema"):
            st.session_state.authenticated = False
            st.rerun()
    
    if opcao == "Pedidos Designados":
        st.header("Pedidos Designados")
        
        # Tabela de Entregas
        st.subheader("📦 ENTREGAS PENDENTES")
        
        # Pedidos para entrega vindos da logística
        pedidos_entrega = [p for p in st.session_state.pedidos if p['status'] == 'No Campo' and not p.get('entregue', False)]
        
        if pedidos_entrega:
            for pedido in pedidos_entrega:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid #22c55e;">
                        <h4 style="color: var(--nexo-orange); margin: 0;">ENTREGA - Pedido #{pedido['id']}</h4>
                        <p style="margin: 0.5rem 0;"><strong>Cliente:</strong> {pedido['cliente']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Evento:</strong> {pedido['evento']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Data:</strong> {pedido['data_evento']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Total:</strong> R$ {pedido['total']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🚚 INICIAR ENTREGA #{pedido['id']}", key=f"iniciar_entrega_{pedido['id']}", use_container_width=True):
                        st.session_state.trabalho_atual = {
                            "pedido": pedido,
                            "tipo": "entrega",
                            "etapa": 1,
                            "etapas_concluidas": [],
                            "dados_etapas": {}
                        }
                        st.success(f"Entrega do pedido #{pedido['id']} iniciada!")
                        st.rerun()
        else:
            st.info("Nenhuma entrega pendente no momento.")
        
        st.markdown("---")
        
        # Tabela de Recolhimentos
        st.subheader("📤 RECOLHIMENTOS PENDENTES")
        
        # Pedidos para recolhimento (já entregues)
        pedidos_recolhimento = [p for p in st.session_state.pedidos if p.get('entregue', False) and not p.get('recolhido', False)]
        
        if pedidos_recolhimento:
            for pedido in pedidos_recolhimento:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                        <h4 style="color: var(--nexo-orange); margin: 0;">RECOLHIMENTO - Pedido #{pedido['id']}</h4>
                        <p style="margin: 0.5rem 0;"><strong>Cliente:</strong> {pedido['cliente']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Evento:</strong> {pedido['evento']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Data:</strong> {pedido['data_evento']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
                        <p style="margin: 0.5rem 0;"><strong>Status:</strong> Entregue - Aguardando Recolhimento</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"📦 INICIAR RECOLHIMENTO #{pedido['id']}", key=f"iniciar_recolhimento_{pedido['id']}", use_container_width=True):
                        st.session_state.trabalho_atual = {
                            "pedido": pedido,
                            "tipo": "recolhimento",
                            "etapa": 1,
                            "etapas_concluidas": [],
                            "dados_etapas": {}
                        }
                        st.success(f"Recolhimento do pedido #{pedido['id']} iniciado!")
                        st.rerun()
        else:
            st.info("Nenhum recolhimento pendente no momento.")
    
    elif opcao == "Trabalho Atual":
        st.header("Trabalho Atual")
        
        if 'trabalho_atual' not in st.session_state or not st.session_state.trabalho_atual:
            st.info("Nenhum trabalho em andamento. Selecione um pedido na aba 'Pedidos Designados' para começar.")
            return
        
        trabalho = st.session_state.trabalho_atual
        pedido = trabalho['pedido']
        tipo_trabalho = trabalho['tipo']
        etapa_atual = trabalho['etapa']
        
        # Cabeçalho do trabalho
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: var(--nexo-orange); margin: 0;">{tipo_trabalho.upper()} - Pedido #{pedido['id']}</h3>
            <p style="margin: 0.5rem 0;"><strong>Cliente:</strong> {pedido['cliente']}</p>
            <p style="margin: 0.5rem 0;"><strong>Evento:</strong> {pedido['evento']}</p>
            <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progresso = (etapa_atual - 1) / 7 * 100
        st.progress(progresso / 100)
        st.write(f"Etapa {etapa_atual} de 7 - {progresso:.0f}% concluído")
        
        # Etapas do trabalho
        etapas = [
            "Check-in Chegada",
            "Conferência de Material", 
            "Início da Montagem",
            "Montagem Concluída",
            "Início da Desmontagem",
            "Material Recolhido",
            "Check-out Saída"
        ]
        
        # Mostrar etapas concluídas
        if trabalho['etapas_concluidas']:
            st.subheader("✅ Etapas Concluídas")
            for etapa_id in trabalho['etapas_concluidas']:
                st.success(f"✅ Etapa {etapa_id}: {etapas[etapa_id-1]}")
        
        # Etapa atual
        if etapa_atual <= 7:
            st.subheader(f"🔄 Etapa {etapa_atual}: {etapas[etapa_atual-1]}")
            
            # Formulário da etapa atual
            executar_etapa_trabalho(etapa_atual, trabalho)
        else:
            st.success("🎉 Trabalho Concluído!")
            
            if st.button("Finalizar Trabalho"):
                # Marcar como entregue ou recolhido
                if tipo_trabalho == "entrega":
                    pedido['entregue'] = True
                    pedido['status'] = "Entregue"
                else:
                    pedido['recolhido'] = True
                    pedido['status'] = "Concluído"
                
                # Limpar trabalho atual
                st.session_state.trabalho_atual = None
                st.success("Trabalho finalizado com sucesso!")
                st.rerun()
    
    elif opcao == "Histórico":
        st.header("Histórico de Trabalhos")
        
        # Trabalhos concluídos
        trabalhos_concluidos = [p for p in st.session_state.pedidos if p['status'] == 'Concluído']
        
        if trabalhos_concluidos:
            for trabalho in trabalhos_concluidos:
                with st.expander(f"Trabalho #{trabalho['id']} - {trabalho['cliente']} - {trabalho['evento']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Cliente:** {trabalho['cliente']}")
                        st.write(f"**Evento:** {trabalho['evento']}")
                        st.write(f"**Data:** {trabalho['data_evento']}")
                        st.write(f"**Local:** {trabalho['local']}")
                    
                    with col2:
                        st.write(f"**Status:** {trabalho['status']}")
                        st.write(f"**Total:** R$ {trabalho['total']:.2f}")
                        st.write(f"**Regime:** {trabalho['regime']}")
                    
                    # Produtos do trabalho
                    if trabalho['produtos']:
                        st.subheader("Produtos:")
                        df_produtos = pd.DataFrame(trabalho['produtos'])
                        st.dataframe(df_produtos, use_container_width=True)
        else:
            st.info("Nenhum trabalho concluído ainda.")

# Função para executar etapas do trabalho
def executar_etapa_trabalho(etapa, trabalho):
    pedido = trabalho['pedido']
    
    if etapa == 1:  # Check-in Chegada
        st.write("📍 **Check-in no local de trabalho**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📍 Usar Minha Localização", use_container_width=True):
                st.success("Localização capturada!")
                st.info("Latitude: -23.5505, Longitude: -46.6333")
        
        with col2:
            foto_chegada = st.file_uploader("📸 Foto do Local de Chegada", type=['jpg', 'png'])
        
        observacoes_chegada = st.text_area("Observações da Chegada")
        
        if st.button("✅ Concluir Check-in", use_container_width=True):
            if foto_chegada and observacoes_chegada:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_chegada.name,
                    'observacoes': observacoes_chegada,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Check-in concluído!")
                st.rerun()
            else:
                st.error("Preencha todos os campos obrigatórios!")
    
    elif etapa == 2:  # Conferência de Material
        st.write("📋 **Conferência de Material**")
        
        # Lista de produtos do pedido
        if pedido['produtos']:
            st.subheader("Produtos para Conferir:")
            
            for i, produto in enumerate(pedido['produtos']):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"• {produto['produto']} - Qtd: {produto['quantidade']} - Diárias: {produto['diarias']}")
                
                with col2:
                    conferido = st.checkbox("Conferido", key=f"conf_{i}")
        
        foto_material = st.file_uploader("📸 Foto do Material Conferido", type=['jpg', 'png'])
        observacoes_material = st.text_area("Observações da Conferência")
        
        if st.button("✅ Concluir Conferência", use_container_width=True):
            if foto_material:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_material.name,
                    'observacoes': observacoes_material,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Conferência concluída!")
                st.rerun()
            else:
                st.error("Foto do material é obrigatória!")
    
    elif etapa == 3:  # Início da Montagem
        st.write("🔧 **Início da Montagem**")
        
        foto_inicio = st.file_uploader("📸 Foto do Início da Montagem", type=['jpg', 'png'])
        observacoes_inicio = st.text_area("Observações do Início")
        
        if st.button("✅ Confirmar Início da Montagem", use_container_width=True):
            if foto_inicio:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_inicio.name,
                    'observacoes': observacoes_inicio,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Início da montagem registrado!")
                st.rerun()
            else:
                st.error("Foto é obrigatória!")
    
    elif etapa == 4:  # Montagem Concluída
        st.write("✅ **Montagem Concluída - Assinatura do Cliente**")
        
        foto_conclusao = st.file_uploader("📸 Foto da Montagem Finalizada", type=['jpg', 'png'])
        
        # Dados do cliente para assinatura
        st.subheader("📝 Dados do Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("Nome Completo do Cliente", value=pedido['cliente'])
            cpf_cliente = st.text_input("CPF do Cliente")
        
        with col2:
            st.write("**Assinatura Digital:**")
            # Simulação de campo de assinatura
            assinatura_texto = st.text_area("Assinatura (Digite seu nome)", height=100, 
                                           help="Em um sistema real, aqui seria um campo de desenho para assinatura digital")
        
        observacoes_conclusao = st.text_area("Observações da Conclusão")
        
        if st.button("✅ Concluir Montagem com Assinatura", use_container_width=True):
            if foto_conclusao and nome_cliente and cpf_cliente and assinatura_texto:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_conclusao.name,
                    'nome_cliente': nome_cliente,
                    'cpf_cliente': cpf_cliente,
                    'assinatura': assinatura_texto,
                    'observacoes': observacoes_conclusao,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Montagem concluída e assinada!")
                st.rerun()
            else:
                st.error("Todos os campos são obrigatórios!")
    
    elif etapa == 5:  # Início da Desmontagem
        st.write("🔧 **Início da Desmontagem**")
        
        foto_desmontagem = st.file_uploader("📸 Foto do Início da Desmontagem", type=['jpg', 'png'])
        observacoes_desmontagem = st.text_area("Observações da Desmontagem")
        
        if st.button("✅ Confirmar Início da Desmontagem", use_container_width=True):
            if foto_desmontagem:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_desmontagem.name,
                    'observacoes': observacoes_desmontagem,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Início da desmontagem registrado!")
                st.rerun()
            else:
                st.error("Foto é obrigatória!")
    
    elif etapa == 6:  # Material Recolhido
        st.write("📦 **Material Recolhido**")
        
        # Checklist de recolhimento
        if pedido['produtos']:
            st.subheader("Checklist de Recolhimento:")
            
            for i, produto in enumerate(pedido['produtos']):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"• {produto['produto']} - Qtd: {produto['quantidade']}")
                
                with col2:
                    recolhido = st.checkbox("Recolhido", key=f"recol_{i}")
        
        foto_recolhimento = st.file_uploader("📸 Foto do Material Recolhido", type=['jpg', 'png'])
        observacoes_recolhimento = st.text_area("Observações do Recolhimento")
        
        if st.button("✅ Confirmar Material Recolhido", use_container_width=True):
            if foto_recolhimento:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_recolhimento.name,
                    'observacoes': observacoes_recolhimento,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Material recolhido!")
                st.rerun()
            else:
                st.error("Foto é obrigatória!")
    
    elif etapa == 7:  # Check-out Saída
        st.write("🚪 **Check-out de Saída**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📍 Usar Minha Localização", use_container_width=True):
                st.success("Localização de saída capturada!")
                st.info("Latitude: -23.5505, Longitude: -46.6333")
        
        with col2:
            foto_saida = st.file_uploader("📸 Foto Final do Local", type=['jpg', 'png'])
        
        relatorio_final = st.text_area("Relatório Final do Trabalho")
        observacoes_saida = st.text_area("Observações de Saída")
        
        if st.button("✅ Finalizar Check-out", use_container_width=True):
            if foto_saida and relatorio_final:
                trabalho['etapas_concluidas'].append(etapa)
                trabalho['etapa'] = etapa + 1
                trabalho['dados_etapas'][f'etapa_{etapa}'] = {
                    'foto': foto_saida.name,
                    'relatorio': relatorio_final,
                    'observacoes': observacoes_saida,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("Check-out concluído!")
                st.rerun()
            else:
                st.error("Foto e relatório final são obrigatórios!")
    st.title("NEXO - Equipe de Campo")
    
    with st.sidebar:
        st.markdown(f"### Bem-vindo, {st.session_state.user_name}!")
        opcao = st.selectbox("Navegação", [
            "Pedidos Designados",
            "Trabalho Atual",
            "Histórico",
            "Chat"
        ])
    
    if opcao == "Pedidos Designados":
        st.header("Pedidos Designados")
        
        # Pedidos para entrega
        st.subheader("📦 Pedidos para Entrega")
        
        pedidos_entrega = [
            {
                "id": 1,
                "cliente": "Hotel Ramada",
                "evento": "Casamento",
                "data": "Hoje",
                "horario": "14:00",
                "local": "Salão Principal",
                "status": "Pronto para Entrega"
            },
            {
                "id": 2,
                "cliente": "Clube Náutico",
                "evento": "Festa Corporativa",
                "data": "Amanhã",
                "horario": "09:00",
                "local": "Área da Piscina",
                "status": "Agendado"
            }
        ]
        
        for pedido in pedidos_entrega:
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: var(--nexo-orange); margin: 0;">Pedido #{pedido['id']} - {pedido['cliente']}</h4>
                    <p style="margin: 0.5rem 0;"><strong>Evento:</strong> {pedido['evento']}</p>
                    <p style="margin: 0.5rem 0;"><strong>Data/Hora:</strong> {pedido['data']} às {pedido['horario']}</p>
                    <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🚚 Iniciar Entrega #{pedido['id']}", key=f"iniciar_entrega_{pedido['id']}"):
                    st.session_state.trabalho_atual = {
                        "pedido": pedido,
                        "tipo": "entrega",
                        "etapa": 1,
                        "etapas_concluidas": []
                    }
                    st.success(f"Entrega do pedido #{pedido['id']} iniciada!")
                    st.rerun()
        
        # Pedidos para recolhimento
        st.subheader("📤 Pedidos para Recolhimento")
        
        pedidos_recolhimento = [
            {
                "id": 3,
                "cliente": "Residência Silva",
                "evento": "Aniversário",
                "data": "Hoje",
                "horario": "18:00",
                "local": "Quintal",
                "status": "Pronto para Recolhimento"
            }
        ]
        
        for pedido in pedidos_recolhimento:
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: var(--nexo-orange); margin: 0;">Pedido #{pedido['id']} - {pedido['cliente']}</h4>
                    <p style="margin: 0.5rem 0;"><strong>Evento:</strong> {pedido['evento']}</p>
                    <p style="margin: 0.5rem 0;"><strong>Data/Hora:</strong> {pedido['data']} às {pedido['horario']}</p>
                    <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📦 Iniciar Recolhimento #{pedido['id']}", key=f"iniciar_recolhimento_{pedido['id']}"):
                    st.session_state.trabalho_atual = {
                        "pedido": pedido,
                        "tipo": "recolhimento",
                        "etapa": 1,
                        "etapas_concluidas": []
                    }
                    st.success(f"Recolhimento do pedido #{pedido['id']} iniciado!")
                    st.rerun()
    
    elif opcao == "Trabalho Atual":
        if 'trabalho_atual' not in st.session_state:
            st.info("Nenhum trabalho em andamento. Selecione um pedido para iniciar.")
            return
        
        trabalho = st.session_state.trabalho_atual
        pedido = trabalho['pedido']
        tipo = trabalho['tipo']
        etapa_atual = trabalho['etapa']
        
        st.header(f"Trabalho Atual - {tipo.title()} #{pedido['id']}")
        
        # Informações do pedido
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: var(--nexo-orange); margin: 0;">{pedido['cliente']} - {pedido['evento']}</h4>
            <p style="margin: 0.5rem 0;"><strong>Local:</strong> {pedido['local']}</p>
            <p style="margin: 0.5rem 0;"><strong>Data/Hora:</strong> {pedido['data']} às {pedido['horario']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Etapas do trabalho
        if tipo == "entrega":
            etapas = [
                "Check-in Chegada",
                "Conferência de Material",
                "Início da Montagem",
                "Montagem Concluída",
                "Início da Desmontagem",
                "Material Recolhido",
                "Check-out Saída"
            ]
        else:  # recolhimento
            etapas = [
                "Check-in Chegada",
                "Início da Desmontagem",
                "Desmontagem Concluída",
                "Conferência de Material",
                "Material Carregado",
                "Check-out Saída"
            ]
        
        # Progress bar
        progresso = (etapa_atual - 1) / len(etapas) * 100
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progresso}%;"></div>
        </div>
        <p style="text-align: center; color: var(--nexo-orange); font-weight: 600;">
            Etapa {etapa_atual} de {len(etapas)} - {progresso:.0f}% Concluído
        </p>
        """, unsafe_allow_html=True)
        
        # Etapa atual
        etapa_nome = etapas[etapa_atual - 1]
        st.subheader(f"Etapa {etapa_atual}: {etapa_nome}")
        
        # Campos obrigatórios por etapa
        if etapa_atual == 1:  # Check-in Chegada
            st.write("📍 **Confirme sua localização e registre a chegada**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📍 Usar Minha Localização"):
                    st.success("✅ Localização registrada: Lat: -8.0476, Lng: -34.8770")
                    st.session_state.localizacao_registrada = True
            
            with col2:
                foto_chegada = st.camera_input("📸 Foto do Local de Chegada")
                if foto_chegada:
                    st.success("✅ Foto de chegada registrada")
                    st.session_state.foto_chegada = True
            
            observacoes = st.text_area("Observações da Chegada")
            
            if st.button("✅ Concluir Check-in"):
                if 'localizacao_registrada' in st.session_state and 'foto_chegada' in st.session_state:
                    trabalho['etapas_concluidas'].append({
                        "etapa": etapa_atual,
                        "nome": etapa_nome,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "observacoes": observacoes
                    })
                    trabalho['etapa'] = etapa_atual + 1
                    st.success("Check-in concluído!")
                    st.rerun()
                else:
                    st.error("Complete todos os campos obrigatórios!")
        
        elif etapa_atual == 2:  # Conferência de Material
            st.write("📋 **Confira todos os itens do pedido**")
            
            # Lista de itens para conferência
            itens_conferencia = [
                {"item": "Tenda 6x6", "quantidade": 2, "conferido": False},
                {"item": "Mesa Redonda", "quantidade": 8, "conferido": False},
                {"item": "Cadeira Plástica", "quantidade": 32, "conferido": False},
                {"item": "Som Ambiente", "quantidade": 1, "conferido": False}
            ]
            
            todos_conferidos = True
            
            for i, item in enumerate(itens_conferencia):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{item['item']}**")
                
                with col2:
                    st.write(f"Qtd: {item['quantidade']}")
                
                with col3:
                    conferido = st.checkbox("✅", key=f"item_{i}")
                    if not conferido:
                        todos_conferidos = False
            
            foto_material = st.camera_input("📸 Foto do Material Conferido")
            observacoes = st.text_area("Observações da Conferência")
            
            if st.button("✅ Concluir Conferência"):
                if todos_conferidos and foto_material:
                    trabalho['etapas_concluidas'].append({
                        "etapa": etapa_atual,
                        "nome": etapa_nome,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "observacoes": observacoes
                    })
                    trabalho['etapa'] = etapa_atual + 1
                    st.success("Conferência concluída!")
                    st.rerun()
                else:
                    st.error("Confira todos os itens e tire a foto!")
        
        elif etapa_atual == 3:  # Início da Montagem
            st.write("🔧 **Registre o início da montagem**")
            
            foto_inicio = st.camera_input("📸 Foto do Início da Montagem")
            horario_inicio = st.time_input("⏰ Horário de Início")
            observacoes = st.text_area("Observações do Início")
            
            if st.button("✅ Registrar Início da Montagem"):
                if foto_inicio:
                    trabalho['etapas_concluidas'].append({
                        "etapa": etapa_atual,
                        "nome": etapa_nome,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "horario_inicio": str(horario_inicio),
                        "observacoes": observacoes
                    })
                    trabalho['etapa'] = etapa_atual + 1
                    st.success("Início da montagem registrado!")
                    st.rerun()
                else:
                    st.error("Tire a foto obrigatória!")
        
        elif etapa_atual == 4:  # Montagem Concluída
            st.write("✅ **Finalize a montagem e obtenha assinatura**")
            
            foto_final = st.camera_input("📸 Foto da Montagem Finalizada")
            horario_conclusao = st.time_input("⏰ Horário de Conclusão")
            
            # Assinatura digital (simulada)
            st.subheader("✍️ Assinatura do Cliente")
            nome_cliente = st.text_input("Nome do Cliente")
            assinatura_cliente = st.text_input("Assinatura Digital (digite o nome)")
            
            observacoes = st.text_area("Observações da Conclusão")
            
            if st.button("✅ Concluir Montagem"):
                if foto_final and nome_cliente and assinatura_cliente:
                    trabalho['etapas_concluidas'].append({
                        "etapa": etapa_atual,
                        "nome": etapa_nome,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "horario_conclusao": str(horario_conclusao),
                        "cliente": nome_cliente,
                        "assinatura": assinatura_cliente,
                        "observacoes": observacoes
                    })
                    trabalho['etapa'] = etapa_atual + 1
                    st.success("Montagem concluída!")
                    st.rerun()
                else:
                    st.error("Complete todos os campos obrigatórios!")
        
        # Continuar com as outras etapas...
        elif etapa_atual >= len(etapas):
            st.success("🎉 Trabalho Concluído!")
            
            if st.button("🏁 Finalizar e Voltar aos Pedidos"):
                # Salvar dados do trabalho concluído
                del st.session_state.trabalho_atual
                st.success("Trabalho finalizado com sucesso!")
                st.rerun()
        
        else:
            # Etapas restantes (simplificadas)
            st.write(f"🔄 **{etapa_nome}**")
            
            foto_etapa = st.camera_input(f"📸 Foto da {etapa_nome}")
            observacoes = st.text_area(f"Observações da {etapa_nome}")
            
            if st.button(f"✅ Concluir {etapa_nome}"):
                if foto_etapa:
                    trabalho['etapas_concluidas'].append({
                        "etapa": etapa_atual,
                        "nome": etapa_nome,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "observacoes": observacoes
                    })
                    trabalho['etapa'] = etapa_atual + 1
                    st.success(f"{etapa_nome} concluída!")
                    st.rerun()
                else:
                    st.error("Tire a foto obrigatória!")
        
        # Histórico de etapas concluídas
        if trabalho['etapas_concluidas']:
            st.subheader("📋 Etapas Concluídas")
            
            for etapa_concluida in trabalho['etapas_concluidas']:
                st.markdown(f"""
                <div style="background: var(--nexo-gray); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #22c55e;">
                    <strong>✅ Etapa {etapa_concluida['etapa']}: {etapa_concluida['nome']}</strong><br>
                    <small>Concluída em: {etapa_concluida['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    elif opcao == "Histórico":
        st.header("Histórico de Trabalhos")
        
        # Trabalhos concluídos (dados de exemplo)
        trabalhos_concluidos = [
            {
                "id": 1,
                "cliente": "Empresa ABC",
                "evento": "Confraternização",
                "data": "2024-01-15",
                "tipo": "Entrega + Recolhimento",
                "status": "Concluído"
            },
            {
                "id": 2,
                "cliente": "Família Santos",
                "evento": "Aniversário",
                "data": "2024-01-12",
                "tipo": "Entrega + Recolhimento",
                "status": "Concluído"
            }
        ]
        
        for trabalho in trabalhos_concluidos:
            with st.expander(f"Trabalho #{trabalho['id']} - {trabalho['cliente']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cliente:** {trabalho['cliente']}")
                    st.write(f"**Evento:** {trabalho['evento']}")
                    st.write(f"**Data:** {trabalho['data']}")
                
                with col2:
                    st.write(f"**Tipo:** {trabalho['tipo']}")
                    st.write(f"**Status:** {trabalho['status']}")
                
                if st.button(f"Ver Detalhes #{trabalho['id']}", key=f"detalhes_{trabalho['id']}"):
                    st.info("Detalhes do trabalho em desenvolvimento")
    
    elif opcao == "Chat":
        st.header("Chat da Equipe")
        
        # Chat específico por trabalho
        if 'trabalho_atual' in st.session_state:
            trabalho = st.session_state.trabalho_atual
            st.subheader(f"Chat - Trabalho #{trabalho['pedido']['id']}")
        else:
            st.subheader("Chat Geral da Equipe")
        
        # Container do chat
        st.markdown("""
        <div class="chat-container">
            <div class="chat-message">
                <strong>Marcelão:</strong> João, como está o andamento no Hotel Ramada?
            </div>
            <div class="chat-message">
                <strong>João:</strong> Montagem 70% concluída. Previsão de término às 16h
            </div>
            <div class="chat-message">
                <strong>Comercial:</strong> Perfeito! Cliente está satisfeito com o andamento
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Input de mensagem
        col1, col2 = st.columns([4, 1])
        
        with col1:
            nova_mensagem = st.text_input("Digite sua mensagem...", key="chat_campo")
        
        with col2:
            if st.button("Enviar"):
                if nova_mensagem:
                    st.success("Mensagem enviada!")
                    st.rerun()

# Interface Boss
def interface_boss():
    st.title("NEXO - Dashboard Executivo")
    
    with st.sidebar:
        st.markdown(f"### Bem-vindo, {st.session_state.user_name}!")
        opcao = st.selectbox("Navegação", [
            "Dashboard Executivo",
            "Análise Financeira",
            "Performance da Equipe",
            "Relatórios Gerenciais",
            "Alertas Executivos",
            "Visão Consolidada"
        ])
    
    if opcao == "Dashboard Executivo":
        st.header("Dashboard Executivo")
        
        # KPIs Estratégicos
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Receita Mensal</h3>
                <h2 style="margin: 0.5rem 0;">R$ 45.200</h2>
                <p style="margin: 0; color: #22c55e;">↑ 8.2%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Margem Bruta</h3>
                <h2 style="margin: 0.5rem 0;">68%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 2.1%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Pedidos Ativos</h3>
                <h2 style="margin: 0.5rem 0;">27</h2>
                <p style="margin: 0; color: #f59e0b;">↓ 3.2%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Eficiência Op.</h3>
                <h2 style="margin: 0.5rem 0;">94%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 1.8%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">NPS Cliente</h3>
                <h2 style="margin: 0.5rem 0;">87</h2>
                <p style="margin: 0; color: #22c55e;">↑ 5.3%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">ROI Mensal</h3>
                <h2 style="margin: 0.5rem 0;">23%</h2>
                <p style="margin: 0; color: #22c55e;">↑ 4.1%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos Executivos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Receita vs Meta (6 meses)")
            dados_receita = pd.DataFrame({
                'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                'Receita Real': [35000, 42000, 38000, 45000, 41000, 45200],
                'Meta': [40000, 40000, 40000, 42000, 42000, 44000]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dados_receita['Mês'], y=dados_receita['Receita Real'], 
                                   mode='lines+markers', name='Receita Real', 
                                   line=dict(color='#FF6B00', width=3)))
            fig.add_trace(go.Scatter(x=dados_receita['Mês'], y=dados_receita['Meta'], 
                                   mode='lines+markers', name='Meta', 
                                   line=dict(color='#22c55e', width=2, dash='dash')))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Distribuição de Custos")
            dados_custos = pd.DataFrame({
                'Categoria': ['Pessoal', 'Material', 'Logística', 'Overhead'],
                'Valor': [15000, 8000, 3000, 2000]
            })
            
            fig = px.pie(dados_custos, values='Valor', names='Categoria',
                        color_discrete_sequence=['#FF6B00', '#ff8533', '#ffb366', '#ffd1a3'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Fluxo de Pedidos
        st.subheader("Fluxo de Pedidos em Tempo Real")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="background: var(--nexo-gray); padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: var(--nexo-orange); margin: 0;">Comercial</h4>
                <h2 style="margin: 0.5rem 0; color: white;">8</h2>
                <p style="margin: 0; color: #888;">Novos pedidos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: var(--nexo-gray); padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: var(--nexo-orange); margin: 0;">Logística</h4>
                <h2 style="margin: 0.5rem 0; color: white;">5</h2>
                <p style="margin: 0; color: #888;">Em preparação</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: var(--nexo-gray); padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: var(--nexo-orange); margin: 0;">Campo</h4>
                <h2 style="margin: 0.5rem 0; color: white;">7</h2>
                <p style="margin: 0; color: #888;">Em execução</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: var(--nexo-gray); padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: var(--nexo-orange); margin: 0;">Concluídos</h4>
                <h2 style="margin: 0.5rem 0; color: white;">15</h2>
                <p style="margin: 0; color: #888;">Este mês</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif opcao == "Análise Financeira":
        st.header("Análise Financeira Detalhada")
        
        # Resumo Financeiro
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Receita Bruta</h3>
                <h2 style="margin: 0.5rem 0;">R$ 45.200</h2>
                <p style="margin: 0; color: #888;">Junho 2024</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Custos Totais</h3>
                <h2 style="margin: 0.5rem 0;">R$ 28.000</h2>
                <p style="margin: 0; color: #888;">62% da receita</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: var(--nexo-orange); margin: 0;">Lucro Líquido</h3>
                <h2 style="margin: 0.5rem 0;">R$ 17.200</h2>
                <p style="margin: 0; color: #22c55e;">38% margem</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Análise por Regime de Pagamento
        st.subheader("Receita por Regime de Pagamento")
        
        dados_regime = pd.DataFrame({
            'Regime': ['Padrão', '1% (Urgente)', '3% (Weekend)'],
            'Receita': [32000, 8200, 5000],
            'Quantidade': [18, 6, 3]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(dados_regime, x='Regime', y='Receita', 
                        color_discrete_sequence=['#FF6B00'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(dados_regime, values='Quantidade', names='Regime',
                        color_discrete_sequence=['#FF6B00', '#ff8533', '#ffb366'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Projeções
        st.subheader("Projeções Financeiras")
        
        dados_projecao = pd.DataFrame({
            'Mês': ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'Projeção Conservadora': [46000, 48000, 50000, 52000, 55000, 60000],
            'Projeção Otimista': [50000, 55000, 58000, 62000, 68000, 75000]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dados_projecao['Mês'], y=dados_projecao['Projeção Conservadora'], 
                               mode='lines+markers', name='Conservadora', 
                               line=dict(color='#ff8533', width=2)))
        fig.add_trace(go.Scatter(x=dados_projecao['Mês'], y=dados_projecao['Projeção Otimista'], 
                               mode='lines+markers', name='Otimista', 
                               line=dict(color='#22c55e', width=2)))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title="Projeções de Receita (6 meses)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif opcao == "Performance da Equipe":
        st.header("Performance da Equipe")
        
        # Métricas por colaborador
        dados_performance = pd.DataFrame({
            'Colaborador': ['João Silva', 'Carlos Santos', 'Pedro Lima', 'Ana Costa', 'Marcelão'],
            'Trabalhos Concluídos': [15, 12, 18, 10, 20],
            'Avaliação Média': [4.8, 4.6, 4.9, 4.7, 4.9],
            'Eficiência (%)': [95, 88, 97, 92, 98]
        })
        
        st.subheader("Ranking de Performance")
        st.dataframe(dados_performance.sort_values('Eficiência (%)', ascending=False), 
                    use_container_width=True)
        
        # Gráficos de performance
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(dados_performance, x='Colaborador', y='Trabalhos Concluídos',
                        color='Eficiência (%)', color_continuous_scale='Oranges')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title="Trabalhos Concluídos vs Eficiência"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(dados_performance, x='Avaliação Média', y='Eficiência (%)',
                           size='Trabalhos Concluídos', hover_name='Colaborador',
                           color_discrete_sequence=['#FF6B00'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title="Avaliação vs Eficiência"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Alertas de performance
        st.subheader("Alertas de Performance")
        
        st.markdown("""
        <div class="alert alert-success">
            ✅ <strong>João Silva</strong> mantém 97% de eficiência há 3 meses consecutivos
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert alert-warning">
            ⚠️ <strong>Carlos Santos</strong> com eficiência abaixo da meta (88% vs 90%)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert alert-info">
            ℹ️ <strong>Ana Costa</strong> disponível para mais trabalhos (apenas 10 concluídos)
        </div>
        """, unsafe_allow_html=True)
    
    elif opcao == "Relatórios Gerenciais":
        st.header("Relatórios Gerenciais")
        
        # Seleção de período
        col1, col2 = st.columns(2)
        
        with col1:
            periodo = st.selectbox("Período do Relatório", 
                                 ["Última Semana", "Último Mês", "Últimos 3 Meses", "Último Ano"])
        
        with col2:
            tipo_relatorio = st.selectbox("Tipo de Relatório", 
                                        ["Operacional", "Financeiro", "Comercial", "Completo"])
        
        # Relatório Operacional
        if tipo_relatorio in ["Operacional", "Completo"]:
            st.subheader("📊 Relatório Operacional")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pedidos Processados", "47", "↑ 12%")
                st.metric("Taxa de Conclusão", "96%", "↑ 2%")
            
            with col2:
                st.metric("Tempo Médio de Entrega", "2.3h", "↓ 0.2h")
                st.metric("Retrabalhos", "2", "↓ 50%")
            
            with col3:
                st.metric("Satisfação Cliente", "4.7/5", "↑ 0.1")
                st.metric("Incidentes", "0", "→ 0")
        
        # Relatório Financeiro
        if tipo_relatorio in ["Financeiro", "Completo"]:
            st.subheader("💰 Relatório Financeiro")
            
            dados_financeiro = pd.DataFrame({
                'Categoria': ['Receita', 'Custos Pessoal', 'Custos Material', 'Custos Logística', 'Lucro'],
                'Valor Atual': [45200, 15000, 8000, 3000, 19200],
                'Valor Anterior': [41800, 14500, 7500, 2800, 17000],
                'Variação (%)': [8.1, 3.4, 6.7, 7.1, 12.9]
            })
            
            st.dataframe(dados_financeiro, use_container_width=True)
        
        # Relatório Comercial
        if tipo_relatorio in ["Comercial", "Completo"]:
            st.subheader("🎯 Relatório Comercial")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Novos Clientes", "8", "↑ 60%")
                st.metric("Taxa de Conversão", "42.8%", "↑ 5.2%")
                st.metric("Ticket Médio", "R$ 1.674", "↑ 8%")
            
            with col2:
                st.metric("Orçamentos Enviados", "28", "↓ 3%")
                st.metric("Follow-up Realizados", "25", "↑ 25%")
                st.metric("Clientes Recorrentes", "15", "↑ 20%")
        
        # Botão de download
        if st.button("📥 Gerar Relatório PDF"):
            st.success("Relatório PDF gerado com sucesso!")
            st.info("Funcionalidade de download em desenvolvimento")
    
    elif opcao == "Alertas Executivos":
        st.header("Alertas Executivos")
        
        # Alertas críticos
        st.subheader("🚨 Alertas Críticos")
        
        st.markdown("""
        <div class="alert alert-error">
            🚨 <strong>URGENTE:</strong> 3 pedidos com documentação pendente há mais de 24h
        </div>
        """, unsafe_allow_html=True)
        
        # Alertas importantes
        st.subheader("⚠️ Alertas Importantes")
        
        st.markdown("""
        <div class="alert alert-warning">
            ⚠️ <strong>Capacidade:</strong> Equipe com 90% de ocupação na próxima semana
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert alert-warning">
            ⚠️ <strong>Financeiro:</strong> Margem do mês abaixo da meta (38% vs 40%)
        </div>
        """, unsafe_allow_html=True)
        
        # Alertas informativos
        st.subheader("ℹ️ Alertas Informativos")
        
        st.markdown("""
        <div class="alert alert-info">
            ℹ️ <strong>Oportunidade:</strong> 5 clientes sem pedidos há mais de 30 dias
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert alert-info">
            ℹ️ <strong>Performance:</strong> João Silva elegível para promoção (97% eficiência)
        </div>
        """, unsafe_allow_html=True)
        
        # Alertas positivos
        st.subheader("✅ Alertas Positivos")
        
        st.markdown("""
        <div class="alert alert-success">
            ✅ <strong>Meta Atingida:</strong> Receita mensal superou meta em 8.2%
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="alert alert-success">
            ✅ <strong>Qualidade:</strong> NPS de 87 - maior índice do ano
        </div>
        """, unsafe_allow_html=True)
    
    elif opcao == "Visão Consolidada":
        st.header("Visão Consolidada do Negócio")
        
        # Mapa de calor de atividades
        st.subheader("Mapa de Atividades por Setor")
        
        dados_atividades = pd.DataFrame({
            'Setor': ['Comercial', 'Logística', 'Campo', 'Galpão'],
            'Segunda': [8, 5, 7, 3],
            'Terça': [6, 8, 9, 4],
            'Quarta': [9, 6, 8, 2],
            'Quinta': [7, 7, 6, 5],
            'Sexta': [10, 9, 10, 6],
            'Sábado': [4, 3, 8, 1],
            'Domingo': [2, 1, 5, 0]
        })
        
        # Transformar para formato de heatmap
        dados_heatmap = dados_atividades.set_index('Setor')
        
        fig = px.imshow(dados_heatmap.values, 
                       x=dados_heatmap.columns, 
                       y=dados_heatmap.index,
                       color_continuous_scale='Oranges',
                       aspect="auto")
        
        fig.update_layout(
            title="Intensidade de Atividades por Setor/Dia",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Resumo executivo
        st.subheader("Resumo Executivo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 Principais Conquistas:**
            - Receita mensal recorde: R$ 45.200
            - NPS cliente em 87 pontos
            - Eficiência operacional de 94%
            - Zero incidentes de segurança
            
            **📈 Oportunidades:**
            - Expansão da equipe de campo
            - Automatização de processos
            - Novos produtos/serviços
            """)
        
        with col2:
            st.markdown("""
            **⚠️ Pontos de Atenção:**
            - Documentação pendente em 3 pedidos
            - Capacidade próxima do limite
            - Margem abaixo da meta mensal
            
            **🚀 Próximos Passos:**
            - Contratar 2 novos colaboradores
            - Implementar sistema de docs automático
            - Revisar precificação de serviços
            """)

# Função principal
def main():
    init_session_state()
    
    # Verificar autenticação
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Loading após login
    if 'loading_shown' not in st.session_state:
        show_loading()
        st.session_state.loading_shown = True
        st.rerun()
    
    # Roteamento por tipo de usuário
    if st.session_state.user_type == "comercial":
        interface_comercial()
    elif st.session_state.user_type == "logistica":
        interface_logistica()
    elif st.session_state.user_type == "campo":
        interface_campo()
    elif st.session_state.user_type == "boss":
        interface_boss()
    
    # Botão de logout na sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Sair do Sistema"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()

