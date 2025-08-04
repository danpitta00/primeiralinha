"""
Dashboard Primeira Linha Eventos - Sistema Integrado Completo
Versão 5.3 - CORRIGIDO + Gerador de Orçamentos Completo
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import quote
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Primeira Linha Eventos - Sistema Completo",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Identidade Visual da Empresa
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
    
    .metric-card.green {
        border-left-color: #10b981;
    }
    
    .metric-card.blue {
        border-left-color: #3b82f6;
    }
    
    .metric-card.purple {
        border-left-color: #8b5cf6;
    }
    
    .metric-card.orange {
        border-left-color: #f59e0b;
    }
    
    .orcamento-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #D4AF37;
        margin: 1rem 0;
    }
    
    .pedido-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #10b981;
        margin: 1rem 0;
    }
    
    .item-row {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #D4AF37;
        border: 1px solid #4b5563;
    }
    
    .item-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 2px solid #D4AF37;
        font-weight: bold;
        text-align: center;
    }
    
    .total-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 1rem;
        border: 2px solid #D4AF37;
    }
    
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid #374151;
    }
    
    .stSelectbox > div > div {
        background-color: #374151;
        color: white;
    }
    
    .stTextInput > div > div > input {
        background-color: #374151;
        color: white;
        border: 2px solid #4b5563;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #D4AF37;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%);
        color: #1f2937;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #B8941F 0%, #9A7B1A 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
    }
    
    .sidebar-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        width: 100%;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .sidebar-button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados da planilha Google Sheets
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_produtos_sheets():
    """Carrega produtos diretamente da planilha Google Sheets"""
    try:
        # URL da planilha em formato CSV
        sheet_id = "1pxBGsaeCuWR_4bdD2_mWBLyxRUqGSJlztH0wnFAtNaw"
        gid = "1527827989"  # ID da aba
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        # Carregar dados
        df = pd.read_csv(url)
        
        # Limpar e padronizar dados
        df.columns = ['produto', 'unidades', 'valor_diaria', 'categoria']
        df = df.dropna(subset=['produto'])
        df['valor_diaria'] = pd.to_numeric(df['valor_diaria'], errors='coerce').fillna(0)
        df['unidades'] = pd.to_numeric(df['unidades'], errors='coerce').fillna(0)
        df['categoria'] = df['categoria'].fillna('outros')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return pd.DataFrame()

# Função para gerar dados de pedidos (simulados baseados na planilha real)
@st.cache_data(ttl=600)
def gerar_dados_pedidos():
    """Gera dados de pedidos baseados nos produtos reais da planilha"""
    
    # Verificar se há pedidos salvos no session_state
    if 'pedidos_salvos' in st.session_state:
        pedidos_existentes = st.session_state.pedidos_salvos
    else:
        pedidos_existentes = []
    
    # Dados reais dos pedidos existentes
    pedidos_reais = [
        {
            'numero_pedido': 'PED001',
            'cliente': 'Caixa Econômica Federal',
            'categoria': 'Público Extra',
            'produto_servico': 'Stand Octanorme, Banqueta, Púlpito',
            'valor': 1850.0,
            'custos': 1200.0,
            'diarias_equipe': 2,
            'local': 'Hotel Ramada',
            'data_entrega': '2024-12-15',
            'data_recolhimento': '2024-12-16',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED002',
            'cliente': 'Sec. da Mulher',
            'categoria': 'Público Extra',
            'produto_servico': 'Palco Tablado 6x3, Brinquedo Inflável, Cama Elástica',
            'valor': 4560.0,
            'custos': 2800.0,
            'diarias_equipe': 3,
            'local': 'Torre de TV',
            'data_entrega': '2024-12-20',
            'data_recolhimento': '2024-12-22',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED003',
            'cliente': 'Programa "Sempre por Elas"',
            'categoria': 'Público Extra',
            'produto_servico': 'Carrinho de Pipoca, Carrinho de Algodão Doce, Monitor/TV',
            'valor': 9080.0,
            'custos': 5500.0,
            'diarias_equipe': 4,
            'local': 'Curralinho',
            'data_entrega': '2025-01-10',
            'data_recolhimento': '2025-01-12',
            'status': 'Confirmado'
        },
        {
            'numero_pedido': 'PED004',
            'cliente': 'Divino Festival',
            'categoria': 'Particular',
            'produto_servico': 'Bebedouro, Filtro de Água, Suporte para TV',
            'valor': 980.0,
            'custos': 600.0,
            'diarias_equipe': 1,
            'local': 'Planaltina',
            'data_entrega': '2025-01-15',
            'data_recolhimento': '2025-01-16',
            'status': 'Em Andamento'
        },
        {
            'numero_pedido': 'PED005',
            'cliente': 'Instituto Maktub',
            'categoria': 'Corporativo',
            'produto_servico': 'Cadeira Estofada, Piscina de Bolinha, Escorregador Inflável',
            'valor': 1310.0,
            'custos': 800.0,
            'diarias_equipe': 2,
            'local': 'Asa Norte',
            'data_entrega': '2025-01-20',
            'data_recolhimento': '2025-01-21',
            'status': 'Pendente'
        },
        {
            'numero_pedido': 'PED006',
            'cliente': 'SERPRO (evento BRICS)',
            'categoria': 'Corporativo',
            'produto_servico': 'Extintor de Incêndio, Notebook, Impressora',
            'valor': 4000.0,
            'custos': 2400.0,
            'diarias_equipe': 3,
            'local': 'Setor Bancário Sul',
            'data_entrega': '2025-02-01',
            'data_recolhimento': '2025-02-03',
            'status': 'Confirmado'
        },
        {
            'numero_pedido': 'PED007',
            'cliente': 'Campeonato de Pesca do DF',
            'categoria': 'Público Extra',
            'produto_servico': 'Banner, Cone de Sinalização, Mesa Dobrável',
            'valor': 0.0,  # A definir
            'custos': 0.0,
            'diarias_equipe': 2,
            'local': 'Lago Paranoá',
            'data_entrega': '2025-02-15',
            'data_recolhimento': '2025-02-16',
            'status': 'Em Negociação'
        }
    ]
    
    # Combinar pedidos reais com pedidos salvos
    todos_pedidos = pedidos_reais + pedidos_existentes
    
    return pd.DataFrame(todos_pedidos)

# Função para gerar PDF do orçamento
def gerar_pdf_orcamento(dados_orcamento, itens_orcamento):
    """Gera PDF do orçamento com timbrado da empresa"""
    
    # Criar PDF em memória
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Cores da empresa
    cor_dourado = HexColor('#D4AF37')
    cor_azul = HexColor('#1E3A8A')
    
    # Cabeçalho com timbrado
    c.setFillColor(cor_azul)
    c.rect(0, height - 80, width, 80, fill=1)
    
    c.setFillColor(cor_dourado)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "PRIMEIRA LINHA EVENTOS")
    
    c.setFillColor('white')
    c.setFont("Helvetica", 10)
    c.drawString(width - 200, height - 30, "CNPJ: 31.912.825/0001-06")
    c.drawString(width - 200, height - 45, "Inscrição Estadual: 07.885.269/001-70")
    
    # Conteúdo do orçamento
    y_position = height - 120
    
    c.setFillColor('black')
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, f"ORÇAMENTO Nº {dados_orcamento['numero_orcamento']}")
    
    y_position -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, f"Cliente: {dados_orcamento['nome_cliente']}")
    y_position -= 20
    c.drawString(50, y_position, f"Evento: {dados_orcamento.get('evento_descricao', 'A definir')}")
    y_position -= 20
    c.drawString(50, y_position, f"Local: {dados_orcamento.get('local_evento', 'A definir')}")
    y_position -= 20
    c.drawString(50, y_position, f"Data do Evento: {dados_orcamento.get('data_evento', 'A definir')}")
    
    y_position -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "ITENS DO ORÇAMENTO:")
    
    y_position -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "Item")
    c.drawString(250, y_position, "Qtd")
    c.drawString(300, y_position, "Valor Unit.")
    c.drawString(400, y_position, "Valor Total")
    
    y_position -= 20
    c.setFont("Helvetica", 10)
    
    for item in itens_orcamento:
        c.drawString(50, y_position, item['produto'])
        c.drawString(250, y_position, str(item['quantidade']))
        c.drawString(300, y_position, f"R$ {item['preco_unitario']:.2f}")
        c.drawString(400, y_position, f"R$ {item['preco_total']:.2f}")
        y_position -= 15
    
    # Valor total
    y_position -= 20
    c.setFont("Helvetica-Bold", 14)
    valor_total = sum(item['preco_total'] for item in itens_orcamento)
    c.drawString(300, y_position, f"VALOR TOTAL: R$ {valor_total:.2f}")
    
    # Informações de pagamento
    y_position -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "FORMA DE PAGAMENTO:")
    y_position -= 20
    c.drawString(50, y_position, "PIX: primeiralinhaeventos@gmail.com")
    
    y_position -= 30
    valido_ate = (datetime.now() + timedelta(days=10)).strftime('%d/%m/%Y')
    c.drawString(50, y_position, f"Proposta válida até: {valido_ate}")
    
    # Rodapé
    c.setFillColor(cor_azul)
    c.rect(0, 0, width, 60, fill=1)
    
    c.setFillColor('white')
    c.setFont("Helvetica", 9)
    c.drawString(50, 35, "Endereço: Saan quadra 02 nº 275/265 - Brasília/DF - CEP 70632240")
    c.drawString(50, 25, "Telefone: (61) 991334258 | E-mail: primeiralinhaeventos@gmail.com")
    c.drawString(50, 15, "Site: www.primeiralinha.com.br | Instagram: @eventosprimeiralinha1")
    
    c.save()
    buffer.seek(0)
    return buffer

# Função principal
def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🎪 PRIMEIRA LINHA EVENTOS</h1>
        <h3>Sistema Integrado Completo v5.3</h3>
        <p>Dashboard + Gerador de Orçamentos + Gestão de Pedidos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com navegação
    st.sidebar.markdown("### 🎯 Navegação")
    
    # Botão para criar novo pedido na sidebar
    if st.sidebar.button("📝 Novo Pedido", use_container_width=True):
        st.session_state.show_novo_pedido = True
    
    # Botão para atualizar dados
    if st.sidebar.button("🔄 Atualizar Dados da Planilha", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    df_produtos = carregar_produtos_sheets()
    df_pedidos = gerar_dados_pedidos()
    
    # Verificar se os dados foram carregados
    if df_produtos.empty:
        st.error("❌ Erro ao carregar dados da planilha. Verifique a conexão.")
        return
    
    # Modal para novo pedido
    if st.session_state.get('show_novo_pedido', False):
        st.markdown("""
        <div class="pedido-container">
            <h2 style="color: #10b981; text-align: center;">📝 Criar Novo Pedido</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_novo_pedido"):
            # Dados básicos do pedido
            col1, col2 = st.columns(2)
            
            with col1:
                cliente_pedido = st.text_input("Cliente *", placeholder="Nome do cliente ou empresa")
                categoria_pedido = st.selectbox("Categoria *", ["Particular", "Corporativo", "Público Extra"])
                valor_pedido = st.number_input("Valor do Pedido (R$) *", min_value=0.0, step=0.01)
                local_pedido = st.text_input("Local do Evento *", placeholder="Endereço completo")
            
            with col2:
                custos_pedido = st.number_input("Custos (R$)", min_value=0.0, step=0.01)
                diarias_equipe = st.number_input("Diárias de Equipe", min_value=0, value=1)
                data_entrega_pedido = st.date_input("Data de Entrega *")
                data_recolhimento_pedido = st.date_input("Data de Recolhimento *")
            
            # Produtos/Serviços
            st.markdown("#### 🛠️ Produtos/Serviços")
            
            # Seleção múltipla de produtos
            produtos_selecionados = st.multiselect(
                "Selecionar Produtos:",
                options=df_produtos['produto'].tolist(),
                help="Selecione um ou mais produtos da lista"
            )
            
            # Campo adicional para produtos não listados
            produtos_extras = st.text_area(
                "Produtos Adicionais:",
                placeholder="Digite produtos que não estão na lista, separados por vírgula"
            )
            
            # Status do pedido
            status_pedido = st.selectbox(
                "Status do Pedido:",
                ["Em Negociação", "Confirmado", "Em Andamento", "Finalizado", "Cancelado", "Pendente"]
            )
            
            # Observações
            observacoes_pedido = st.text_area("Observações", placeholder="Informações adicionais sobre o pedido")
            
            # Botões do formulário
            col1, col2 = st.columns(2)
            
            with col1:
                submitted_pedido = st.form_submit_button("✅ Salvar Pedido", use_container_width=True)
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_novo_pedido = False
                    st.rerun()
            
            # Processar envio do formulário
            if submitted_pedido:
                if cliente_pedido and valor_pedido > 0 and local_pedido and data_entrega_pedido and data_recolhimento_pedido:
                    # Gerar número do pedido
                    numero_pedido = f"PED{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:3].upper()}"
                    
                    # Combinar produtos selecionados com produtos extras
                    produtos_finais = produtos_selecionados.copy()
                    if produtos_extras:
                        produtos_extras_lista = [p.strip() for p in produtos_extras.split(',') if p.strip()]
                        produtos_finais.extend(produtos_extras_lista)
                    
                    produto_servico_str = ', '.join(produtos_finais) if produtos_finais else 'A definir'
                    
                    # Criar novo pedido
                    novo_pedido = {
                        'numero_pedido': numero_pedido,
                        'cliente': cliente_pedido,
                        'categoria': categoria_pedido,
                        'produto_servico': produto_servico_str,
                        'valor': valor_pedido,
                        'custos': custos_pedido,
                        'diarias_equipe': diarias_equipe,
                        'local': local_pedido,
                        'data_entrega': data_entrega_pedido.strftime('%Y-%m-%d'),
                        'data_recolhimento': data_recolhimento_pedido.strftime('%Y-%m-%d'),
                        'status': status_pedido
                    }
                    
                    # Salvar no session_state
                    if 'pedidos_salvos' not in st.session_state:
                        st.session_state.pedidos_salvos = []
                    
                    st.session_state.pedidos_salvos.append(novo_pedido)
                    
                    # Limpar cache para atualizar dados
                    st.cache_data.clear()
                    
                    st.success(f"✅ Pedido {numero_pedido} criado com sucesso!")
                    st.session_state.show_novo_pedido = False
                    st.rerun()
                
                else:
                    st.error("❌ Preencha todos os campos obrigatórios marcados com *")
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "📈 Evolução", 
        "📦 Pedidos", 
        "🎯 Gerador de Orçamentos",
        "🛠️ Catálogo", 
        "⚠️ Alertas"
    ])
    
    with tab1:
        st.markdown("### 📊 Dashboard Principal")
        
        # KPIs principais
        if not df_pedidos.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            receita_total = df_pedidos['valor'].sum()
            custos_totais = df_pedidos['custos'].sum()
            lucro_total = receita_total - custos_totais
            margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>💰 Receita Total</h4>
                    <h2>R$ {receita_total:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card green">
                    <h4>📈 Lucro Total</h4>
                    <h2>R$ {lucro_total:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card blue">
                    <h4>📊 Margem de Lucro</h4>
                    <h2>{margem_lucro:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card purple">
                    <h4>📦 Total de Pedidos</h4>
                    <h2>{len(df_pedidos)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Receita por categoria
                receita_categoria = df_pedidos.groupby('categoria')['valor'].sum().reset_index()
                fig_categoria = px.pie(
                    receita_categoria, 
                    values='valor', 
                    names='categoria',
                    title="💼 Receita por Categoria",
                    color_discrete_sequence=['#D4AF37', '#1E3A8A', '#3730A3', '#1E1B4B']
                )
                fig_categoria.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_categoria, use_container_width=True)
            
            with col2:
                # Status dos pedidos
                status_count = df_pedidos['status'].value_counts().reset_index()
                fig_status = px.bar(
                    status_count,
                    x='status',
                    y='count',
                    title="📋 Status dos Pedidos",
                    color='count',
                    color_continuous_scale=['#1E3A8A', '#D4AF37']
                )
                fig_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_status, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Evolução Temporal")
        
        if not df_pedidos.empty:
            # Gráfico de receita mensal
            df_pedidos['data_entrega'] = pd.to_datetime(df_pedidos['data_entrega'])
            df_pedidos['mes'] = df_pedidos['data_entrega'].dt.to_period('M')
            
            receita_mensal = df_pedidos.groupby('mes')['valor'].sum().reset_index()
            receita_mensal['mes_str'] = receita_mensal['mes'].astype(str)
            
            fig_evolucao = px.line(
                receita_mensal,
                x='mes_str',
                y='valor',
                title="📈 Evolução da Receita Mensal",
                markers=True
            )
            fig_evolucao.update_traces(line_color='#D4AF37', marker_color='#D4AF37')
            fig_evolucao.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
            # Lucro mensal
            lucro_mensal = df_pedidos.groupby('mes').apply(lambda x: x['valor'].sum() - x['custos'].sum()).reset_index()
            lucro_mensal.columns = ['mes', 'lucro']
            lucro_mensal['mes_str'] = lucro_mensal['mes'].astype(str)
            
            fig_lucro = px.bar(
                lucro_mensal,
                x='mes_str',
                y='lucro',
                title="💰 Lucro Mensal",
                color='lucro',
                color_continuous_scale=['#1E3A8A', '#D4AF37']
            )
            fig_lucro.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_lucro, use_container_width=True)
    
    with tab3:
        st.markdown("### 📦 Gestão de Pedidos")
        
        if not df_pedidos.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Filtrar por Status:",
                    ["Todos"] + list(df_pedidos['status'].unique())
                )
            
            with col2:
                categoria_filter = st.selectbox(
                    "Filtrar por Categoria:",
                    ["Todas"] + list(df_pedidos['categoria'].unique())
                )
            
            with col3:
                cliente_filter = st.selectbox(
                    "Filtrar por Cliente:",
                    ["Todos"] + list(df_pedidos['cliente'].unique())
                )
            
            # Aplicar filtros
            df_filtrado = df_pedidos.copy()
            
            if status_filter != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status'] == status_filter]
            
            if categoria_filter != "Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filter]
            
            if cliente_filter != "Todos":
                df_filtrado = df_filtrado[df_filtrado['cliente'] == cliente_filter]
            
            # Tabela de pedidos
            st.dataframe(
                df_filtrado[['numero_pedido', 'cliente', 'categoria', 'valor', 'status', 'data_entrega']],
                use_container_width=True
            )
            
            # Métricas filtradas
            if not df_filtrado.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Pedidos Filtrados</h4>
                        <h2>{len(df_filtrado)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    valor_filtrado = df_filtrado['valor'].sum()
                    st.markdown(f"""
                    <div class="metric-card green">
                        <h4>Valor Total</h4>
                        <h2>R$ {valor_filtrado:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    ticket_medio = valor_filtrado / len(df_filtrado) if len(df_filtrado) > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card blue">
                        <h4>Ticket Médio</h4>
                        <h2>R$ {ticket_medio:,.0f}</h2>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🎯 Gerador de Orçamentos")
        
        st.markdown("""
        <div class="orcamento-container">
            <h2 style="color: #D4AF37; text-align: center;">📋 Criar Novo Orçamento</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializar session state para itens
        if 'itens_orcamento' not in st.session_state:
            st.session_state.itens_orcamento = []
        
        # Seção para adicionar itens (FORA do formulário)
        st.markdown("#### 🛠️ Adicionar Produtos ao Orçamento")
        
        if not df_produtos.empty:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                produto_selecionado = st.selectbox(
                    "Selecionar Produto:",
                    options=df_produtos['produto'].tolist(),
                    key="produto_select"
                )
            
            with col2:
                quantidade = st.number_input("Quantidade:", min_value=1, value=1, key="quantidade_input")
            
            with col3:
                # Buscar preço do produto selecionado
                preco_sugerido = df_produtos[df_produtos['produto'] == produto_selecionado]['valor_diaria'].iloc[0] if not df_produtos.empty else 0
                preco_unitario = st.number_input("Preço Unit.:", min_value=0.0, value=float(preco_sugerido), step=0.01, key="preco_input")
            
            with col4:
                if st.button("➕ Adicionar Item", use_container_width=True):
                    if produto_selecionado and quantidade > 0 and preco_unitario > 0:
                        item = {
                            'produto': produto_selecionado,
                            'quantidade': quantidade,
                            'preco_unitario': preco_unitario,
                            'preco_total': quantidade * preco_unitario
                        }
                        st.session_state.itens_orcamento.append(item)
                        st.success(f"✅ {produto_selecionado} adicionado!")
                        st.rerun()
        
        # Exibir itens adicionados com visual melhorado
        if st.session_state.itens_orcamento:
            st.markdown("#### 📋 Itens do Orçamento")
            
            # Cabeçalho da lista
            st.markdown("""
            <div class="item-header">
                <div style="display: flex; justify-content: space-between;">
                    <span style="flex: 3;">PRODUTO</span>
                    <span style="flex: 1; text-align: center;">QTD</span>
                    <span style="flex: 1; text-align: center;">PREÇO UNIT.</span>
                    <span style="flex: 1; text-align: center;">TOTAL</span>
                    <span style="flex: 0.5; text-align: center;">AÇÃO</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Lista de itens
            for i, item in enumerate(st.session_state.itens_orcamento):
                st.markdown(f"""
                <div class="item-row">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="flex: 3; font-weight: bold;">{item['produto']}</span>
                        <span style="flex: 1; text-align: center;">{item['quantidade']}</span>
                        <span style="flex: 1; text-align: center;">R$ {item['preco_unitario']:.2f}</span>
                        <span style="flex: 1; text-align: center; font-weight: bold; color: #D4AF37;">R$ {item['preco_total']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de remover (fora do HTML)
                if st.button("🗑️ Remover", key=f"remove_{i}", help=f"Remover {item['produto']}"):
                    st.session_state.itens_orcamento.pop(i)
                    st.rerun()
            
            # Total
            valor_total = sum(item['preco_total'] for item in st.session_state.itens_orcamento)
            st.markdown(f"""
            <div class="total-section">
                <h2>💰 VALOR TOTAL: R$ {valor_total:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Formulário de orçamento (SEM botões internos)
        with st.form("form_orcamento"):
            # Dados do cliente
            st.markdown("#### 👤 Dados do Cliente")
            col1, col2 = st.columns(2)
            
            with col1:
                nome_cliente = st.text_input("Nome do Cliente *", placeholder="Nome completo ou empresa")
                telefone_cliente = st.text_input("Telefone", placeholder="(61) 99999-9999")
                data_evento = st.date_input("Data do Evento")
            
            with col2:
                email_cliente = st.text_input("Email", placeholder="email@exemplo.com")
                evento_descricao = st.text_input("Descrição do Evento", placeholder="Ex: Festa de aniversário")
                local_evento = st.text_input("Local do Evento", placeholder="Endereço completo")
            
            # Datas
            st.markdown("#### 📅 Datas")
            col1, col2 = st.columns(2)
            
            with col1:
                data_entrega = st.date_input("Data de Entrega")
            
            with col2:
                data_recolhimento = st.date_input("Data de Recolhimento")
            
            # Observações
            observacoes = st.text_area("Observações", placeholder="Informações adicionais sobre o orçamento")
            
            # Botão para gerar orçamento
            submitted = st.form_submit_button("🎯 Gerar Orçamento PDF", use_container_width=True)
            
            if submitted:
                if nome_cliente and st.session_state.itens_orcamento:
                    # Gerar número do orçamento
                    numero_orcamento = f"ORC{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
                    
                    # Dados do orçamento
                    dados_orcamento = {
                        'numero_orcamento': numero_orcamento,
                        'nome_cliente': nome_cliente,
                        'email_cliente': email_cliente,
                        'telefone_cliente': telefone_cliente,
                        'evento_descricao': evento_descricao,
                        'local_evento': local_evento,
                        'data_evento': data_evento.strftime('%d/%m/%Y') if data_evento else '',
                        'data_entrega': data_entrega.strftime('%d/%m/%Y') if data_entrega else '',
                        'data_recolhimento': data_recolhimento.strftime('%d/%m/%Y') if data_recolhimento else '',
                        'observacoes': observacoes
                    }
                    
                    # Gerar PDF
                    try:
                        pdf_buffer = gerar_pdf_orcamento(dados_orcamento, st.session_state.itens_orcamento)
                        
                        # Disponibilizar para download
                        st.success(f"✅ Orçamento {numero_orcamento} gerado com sucesso!")
                        
                        st.download_button(
                            label="📥 Baixar Orçamento PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"orcamento_{numero_orcamento}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {e}")
                
                else:
                    st.error("❌ Preencha pelo menos o nome do cliente e adicione itens ao orçamento!")
        
        # Botão para limpar orçamento (FORA do formulário)
        if st.session_state.itens_orcamento:
            if st.button("🔄 Limpar Orçamento", use_container_width=True):
                st.session_state.itens_orcamento = []
                st.rerun()
    
    with tab5:
        st.markdown("### 🛠️ Catálogo de Produtos")
        
        if not df_produtos.empty:
            # Estatísticas do catálogo
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📦 Total de Produtos</h4>
                    <h2>{len(df_produtos)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                categorias_unicas = df_produtos['categoria'].nunique()
                st.markdown(f"""
                <div class="metric-card green">
                    <h4>🏷️ Categorias</h4>
                    <h2>{categorias_unicas}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                preco_medio = df_produtos['valor_diaria'].mean()
                st.markdown(f"""
                <div class="metric-card blue">
                    <h4>💰 Preço Médio</h4>
                    <h2>R$ {preco_medio:.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                estoque_total = df_produtos['unidades'].sum()
                st.markdown(f"""
                <div class="metric-card purple">
                    <h4>📊 Estoque Total</h4>
                    <h2>{estoque_total:.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                categoria_filtro = st.selectbox(
                    "Filtrar por Categoria:",
                    ["Todas"] + sorted(df_produtos['categoria'].unique().tolist())
                )
            
            with col2:
                busca_produto = st.text_input("Buscar Produto:", placeholder="Digite o nome do produto")
            
            # Aplicar filtros
            df_produtos_filtrado = df_produtos.copy()
            
            if categoria_filtro != "Todas":
                df_produtos_filtrado = df_produtos_filtrado[df_produtos_filtrado['categoria'] == categoria_filtro]
            
            if busca_produto:
                df_produtos_filtrado = df_produtos_filtrado[
                    df_produtos_filtrado['produto'].str.contains(busca_produto, case=False, na=False)
                ]
            
            # Tabela de produtos
            st.dataframe(
                df_produtos_filtrado[['produto', 'categoria', 'valor_diaria', 'unidades']],
                use_container_width=True
            )
            
            # Gráfico de distribuição por categoria
            if not df_produtos_filtrado.empty:
                categoria_count = df_produtos_filtrado['categoria'].value_counts().reset_index()
                
                fig_cat_dist = px.bar(
                    categoria_count,
                    x='categoria',
                    y='count',
                    title="📊 Distribuição de Produtos por Categoria",
                    color='count',
                    color_continuous_scale=['#1E3A8A', '#D4AF37']
                )
                fig_cat_dist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_cat_dist, use_container_width=True)
        
        else:
            st.warning("⚠️ Nenhum produto encontrado na planilha.")
    
    with tab6:
        st.markdown("### ⚠️ Sistema de Alertas")
        
        if not df_pedidos.empty:
            # Calcular KPIs para alertas
            receita_total = df_pedidos['valor'].sum()
            custos_totais = df_pedidos['custos'].sum()
            lucro_total = receita_total - custos_totais
            margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
            
            # Calcular alertas
            alertas_criticos = 0
            alertas_atencao = 0
            alertas_positivos = 0
            
            # Verificar margem de lucro baixa
            if margem_lucro < 20:
                alertas_criticos += 1
                st.error(f"🚨 **MARGEM DE LUCRO BAIXA**: {margem_lucro:.1f}% (Recomendado: >20%)")
            
            # Verificar pedidos pendentes
            pedidos_pendentes = len(df_pedidos[df_pedidos['status'].isin(['Pendente', 'Em Negociação'])])
            if pedidos_pendentes > 3:
                alertas_atencao += 1
                st.warning(f"⚠️ **MUITOS PEDIDOS PENDENTES**: {pedidos_pendentes} pedidos aguardando definição")
            
            # Verificar crescimento
            if receita_total > 20000:
                alertas_positivos += 1
                st.success(f"✅ **META DE RECEITA ATINGIDA**: R$ {receita_total:,.0f} (Meta: R$ 20.000)")
            
            # Verificar diversificação de clientes
            clientes_unicos = df_pedidos['cliente'].nunique()
            if clientes_unicos < 5:
                alertas_atencao += 1
                st.warning(f"⚠️ **POUCOS CLIENTES ATIVOS**: {clientes_unicos} clientes (Recomendado: >5)")
            
            # Resumo de alertas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🚨 Críticos</h4>
                    <h2>{alertas_criticos}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card orange">
                    <h4>⚠️ Atenção</h4>
                    <h2>{alertas_atencao}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card green">
                    <h4>✅ Positivos</h4>
                    <h2>{alertas_positivos}</h2>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        🎪 Dashboard Primeira Linha Eventos v5.3 | 
        Sistema Integrado Completo - CORRIGIDO | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df_produtos)} produtos no catálogo | 
        {len(df_pedidos)} pedidos registrados
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
