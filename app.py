"""
Dashboard Primeira Linha Eventos - Sistema Integrado Completo
Versão 5.3 - CORRIGIDO (download_button fora do formulário)
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
    
    .item-row {
        background: #374151;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #D4AF37;
    }
    
    .total-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 1rem;
        border: 2px solid #D4AF37;
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
    produtos_df = carregar_produtos_sheets()
    
    if produtos_df.empty:
        return pd.DataFrame()
    
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
    
    return pd.DataFrame(pedidos_reais)

# Função para calcular diferença de dias entre datas
def calcular_dias_evento(data_inicio, data_fim):
    """Calcula a diferença em dias entre duas datas"""
    try:
        if data_inicio and data_fim:
            delta = data_fim - data_inicio
            return delta.days + 1  # +1 para incluir o dia inicial
        return 0
    except:
        return 0

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
    c.drawString(50, y_position, f"Data do Evento: {dados_orcamento.get('data_evento_inicio', 'A definir')} até {dados_orcamento.get('data_evento_fim', 'A definir')}")
    y_position -= 20
    c.drawString(50, y_position, f"Quantidade de Diárias: {dados_orcamento.get('quantidade_diarias', 1)}")
    
    y_position -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "ITENS DO ORÇAMENTO:")
    
    y_position -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "Item")
    c.drawString(250, y_position, "Qtd")
    c.drawString(300, y_position, "Diárias")
    c.drawString(350, y_position, "Valor Unit.")
    c.drawString(450, y_position, "Valor Total")
    
    y_position -= 20
    c.setFont("Helvetica", 10)
    
    for item in itens_orcamento:
        c.drawString(50, y_position, item['produto'][:30])  # Limita o nome do produto
        c.drawString(250, y_position, str(item['quantidade']))
        c.drawString(300, y_position, str(item['diarias']))
        c.drawString(350, y_position, f"R$ {item['preco_unitario']:.2f}")
        c.drawString(450, y_position, f"R$ {item['preco_total']:.2f}")
        y_position -= 15
    
    # Valor total
    y_position -= 20
    c.setFont("Helvetica-Bold", 14)
    valor_total = sum(item['preco_total'] for item in itens_orcamento)
    c.drawString(350, y_position, f"VALOR TOTAL: R$ {valor_total:.2f}")
    
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
    
    # Botão Novo Pedido na sidebar
    if st.sidebar.button("📝 NOVO PEDIDO", use_container_width=True):
        st.session_state.show_novo_pedido = True
    
    # Botão para atualizar dados
    if st.sidebar.button("🔄 Atualizar Dados da Planilha"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    df_produtos = carregar_produtos_sheets()
    df_pedidos = gerar_dados_pedidos()
    
    # Verificar se os dados foram carregados
    if df_produtos.empty:
        st.error("❌ Erro ao carregar dados da planilha. Verifique a conexão.")
        return
    
    # Mostrar formulário de novo pedido se solicitado
    if st.session_state.get('show_novo_pedido', False):
        st.markdown("### ➕ Novo Pedido")
        
        with st.form("novo_pedido"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Cliente/Projeto*")
                categoria = st.selectbox("Categoria*", [
                    "Público Extra", "Público Geral", "Corporativo", 
                    "Casamento", "Aniversário", "Particular", "Outro"
                ])
                
                # Seleção múltipla de produtos
                produtos_disponiveis = df_produtos['produto'].tolist()
                produtos_selecionados = st.multiselect(
                    "Produtos/Serviços*", 
                    produtos_disponiveis
                )
                
                # Campo para produtos extras
                produtos_extras = st.text_area("Produtos/Serviços Extras (não listados)")
                
                valor = st.number_input("Valor Total (R$)*", min_value=0.0, format="%.2f")
            
            with col2:
                custos = st.number_input("Custos do Pedido (R$)", min_value=0.0, format="%.2f")
                diarias_equipe = st.number_input("Diárias de Equipe", min_value=0, format="%d")
                local = st.text_input("Local do Evento")
                data_entrega = st.date_input("Data de Entrega")
                data_recolhimento = st.date_input("Data de Recolhimento")
                status = st.selectbox("Status", [
                    "Em Negociação", "Confirmado", "Em Andamento", 
                    "Finalizado", "Cancelado", "Pendente"
                ])
                observacoes = st.text_area("Observações")
            
            submitted = st.form_submit_button("💾 Salvar Pedido", use_container_width=True)
            
            if submitted:
                if cliente and categoria and (produtos_selecionados or produtos_extras) and valor > 0:
                    # Combinar produtos selecionados e extras
                    todos_produtos = produtos_selecionados.copy()
                    if produtos_extras:
                        todos_produtos.extend([p.strip() for p in produtos_extras.split(',') if p.strip()])
                    
                    # Criar novo pedido
                    novo_numero = f"PED{len(df_pedidos) + 1:03d}"
                    
                    novo_pedido = {
                        'numero_pedido': novo_numero,
                        'cliente': cliente,
                        'categoria': categoria,
                        'produto_servico': ', '.join(todos_produtos),
                        'valor': valor,
                        'custos': custos,
                        'diarias_equipe': diarias_equipe,
                        'local': local,
                        'data_entrega': data_entrega.strftime('%Y-%m-%d') if data_entrega else '',
                        'data_recolhimento': data_recolhimento.strftime('%Y-%m-%d') if data_recolhimento else '',
                        'status': status,
                        'observacoes': observacoes
                    }
                    
                    # Salvar em session_state
                    if 'novos_pedidos' not in st.session_state:
                        st.session_state.novos_pedidos = []
                    
                    st.session_state.novos_pedidos.append(novo_pedido)
                    
                    st.success(f"✅ Pedido {novo_numero} salvo com sucesso!")
                    st.balloons()
                    
                    # Limpar formulário
                    st.session_state.show_novo_pedido = False
                    st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios (*)")
        
        if st.button("❌ Fechar Formulário"):
            st.session_state.show_novo_pedido = False
            st.rerun()
        
        st.divider()
    
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
        
        # Combinar pedidos existentes com novos pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        # KPIs principais
        if not todos_pedidos.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            receita_total = todos_pedidos['valor'].sum()
            custos_totais = todos_pedidos['custos'].sum()
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
                    <h2>{len(todos_pedidos)}</h2>
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
                status_count = todos_pedidos['status'].value_counts().reset_index()
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
        
        # Combinar pedidos para análise temporal
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            # Converter datas
            todos_pedidos['data_entrega'] = pd.to_datetime(todos_pedidos['data_entrega'], errors='coerce')
            
            # Gráfico de receita mensal
            todos_pedidos['mes_ano'] = todos_pedidos['data_entrega'].dt.to_period('M').astype(str)
            receita_mensal = todos_pedidos.groupby('mes_ano')['valor'].sum().reset_index()
            
            fig_receita = px.bar(
                receita_mensal,
                x='mes_ano',
                y='valor',
                title="💰 Receita Mensal",
                color='valor',
                color_continuous_scale=['#1E3A8A', '#D4AF37']
            )
            fig_receita.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_receita, use_container_width=True)
            
            # Gráfico de lucro mensal
            lucro_mensal = todos_pedidos.groupby('mes_ano').agg({
                'valor': 'sum',
                'custos': 'sum'
            }).reset_index()
            lucro_mensal['lucro'] = lucro_mensal['valor'] - lucro_mensal['custos']
            
            fig_lucro = px.bar(
                lucro_mensal,
                x='mes_ano',
                y='lucro',
                title="📈 Lucro Mensal",
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
        
        # Combinar pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_categoria = st.selectbox("Filtrar por Categoria", 
                                              ["Todas"] + list(todos_pedidos['categoria'].unique()))
            
            with col2:
                filtro_status = st.selectbox("Filtrar por Status", 
                                           ["Todos"] + list(todos_pedidos['status'].unique()))
            
            with col3:
                busca_cliente = st.text_input("Buscar Cliente")
            
            # Aplicar filtros
            df_filtrado = todos_pedidos.copy()
            
            if filtro_categoria != "Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == filtro_categoria]
            
            if filtro_status != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
            
            if busca_cliente:
                df_filtrado = df_filtrado[df_filtrado['cliente'].str.contains(busca_cliente, case=False, na=False)]
            
            # Mostrar resultados
            st.markdown(f"**📊 Resultados:** {len(df_filtrado)} pedidos | Receita: R$ {df_filtrado['valor'].sum():,.2f}")
            
            # Tabela de pedidos
            if not df_filtrado.empty:
                st.dataframe(df_filtrado, use_container_width=True, height=400)
            else:
                st.info("🔍 Nenhum pedido encontrado com os filtros aplicados")
        else:
            st.info("📦 Nenhum pedido encontrado")
    
    with tab4:
        st.markdown("### 🎯 Gerador de Orçamentos")
        
        # Inicializar session state para itens do orçamento
        if 'itens_orcamento' not in st.session_state:
            st.session_state.itens_orcamento = []
        
        # Container para o orçamento
        st.markdown('<div class="orcamento-container">', unsafe_allow_html=True)
        
        # Seção para adicionar itens
        st.markdown("#### ➕ Adicionar Item ao Orçamento")
        
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            produto_selecionado = st.selectbox(
                "Selecione o Produto",
                df_produtos['produto'].tolist(),
                key="produto_select"
            )
        
        with col2:
            quantidade = st.number_input("Qtd", min_value=1, value=1, key="quantidade")
        
        with col3:
            diarias = st.number_input("Diárias", min_value=1, value=1, key="diarias")
        
        with col4:
            # Buscar preço padrão do produto
            preco_padrao = df_produtos[df_produtos['produto'] == produto_selecionado]['valor_diaria'].iloc[0] if not df_produtos.empty else 0
            preco_unitario = st.number_input("Preço Unit.", min_value=0.0, value=float(preco_padrao), format="%.2f", key="preco")
        
        with col5:
            if st.button("➕ Adicionar", key="add_item"):
                preco_total = quantidade * diarias * preco_unitario
                
                item = {
                    'produto': produto_selecionado,
                    'quantidade': quantidade,
                    'diarias': diarias,
                    'preco_unitario': preco_unitario,
                    'preco_total': preco_total
                }
                
                st.session_state.itens_orcamento.append(item)
                st.rerun()
        
        # Mostrar itens adicionados
        if st.session_state.itens_orcamento:
            st.markdown("#### 📋 Itens do Orçamento")
            
            # Cabeçalho da tabela
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
            with col1:
                st.markdown("**Produto**")
            with col2:
                st.markdown("**Qtd**")
            with col3:
                st.markdown("**Diárias**")
            with col4:
                st.markdown("**Preço Unit.**")
            with col5:
                st.markdown("**Total**")
            with col6:
                st.markdown("**Ação**")
            
            # Itens
            for i, item in enumerate(st.session_state.itens_orcamento):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f'<div class="item-row">{item["produto"]}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="item-row">{item["quantidade"]}</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="item-row">{item["diarias"]}</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="item-row">R$ {item["preco_unitario"]:.2f}</div>', unsafe_allow_html=True)
                with col5:
                    st.markdown(f'<div class="item-row">R$ {item["preco_total"]:.2f}</div>', unsafe_allow_html=True)
                with col6:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.itens_orcamento.pop(i)
                        st.rerun()
            
            # Total geral
            valor_total = sum(item['preco_total'] for item in st.session_state.itens_orcamento)
            st.markdown(f"""
            <div class="total-section">
                <h3>💰 VALOR TOTAL: R$ {valor_total:,.2f}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Formulário de dados do cliente (FORA do form para evitar conflito)
        if st.session_state.itens_orcamento:
            st.markdown("#### 👤 Dados do Cliente e Evento")
            
            # Dados do cliente em session_state
            if 'dados_cliente' not in st.session_state:
                st.session_state.dados_cliente = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                nome_cliente = st.text_input("Nome do Cliente*", key="nome_cliente")
                telefone = st.text_input("Telefone", key="telefone")
                email = st.text_input("E-mail", key="email")
                evento_descricao = st.text_input("Descrição do Evento*", key="evento_descricao")
            
            with col2:
                local_evento = st.text_input("Local do Evento", key="local_evento")
                data_evento_inicio = st.date_input("Data de Início do Evento", key="data_inicio")
                data_evento_fim = st.date_input("Data de Fim do Evento", key="data_fim")
                
                # Calcular dias do evento
                dias_evento = calcular_dias_evento(data_evento_inicio, data_evento_fim)
                
                # Campo para quantidade de diárias
                quantidade_diarias = st.number_input("Quantidade de Diárias", min_value=1, value=dias_evento if dias_evento > 0 else 1, key="qtd_diarias")
                
                # Aviso se as diárias não batem com as datas
                if dias_evento > 0 and quantidade_diarias != dias_evento:
                    st.markdown(f"""
                    <div class="warning-box">
                        ⚠️ ATENÇÃO: As datas do evento indicam {dias_evento} dia(s), mas você definiu {quantidade_diarias} diária(s).
                    </div>
                    """, unsafe_allow_html=True)
            
            observacoes = st.text_area("Observações", key="observacoes")
            
            # Botão para gerar orçamento (FORA do form)
            if st.button("📄 Gerar Orçamento PDF", use_container_width=True, key="gerar_orcamento"):
                if nome_cliente and evento_descricao:
                    # Gerar número do orçamento
                    numero_orcamento = f"ORC{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Dados do orçamento
                    dados_orcamento = {
                        'numero_orcamento': numero_orcamento,
                        'nome_cliente': nome_cliente,
                        'telefone': telefone,
                        'email': email,
                        'evento_descricao': evento_descricao,
                        'local_evento': local_evento,
                        'data_evento_inicio': data_evento_inicio.strftime('%d/%m/%Y') if data_evento_inicio else '',
                        'data_evento_fim': data_evento_fim.strftime('%d/%m/%Y') if data_evento_fim else '',
                        'quantidade_diarias': quantidade_diarias,
                        'observacoes': observacoes
                    }
                    
                    # Gerar PDF
                    pdf_buffer = gerar_pdf_orcamento(dados_orcamento, st.session_state.itens_orcamento)
                    
                    # Salvar PDF em session_state para download
                    st.session_state.pdf_gerado = {
                        'buffer': pdf_buffer.getvalue(),
                        'filename': f"Orcamento_{numero_orcamento}_{nome_cliente.replace(' ', '_')}.pdf",
                        'numero': numero_orcamento
                    }
                    
                    st.success(f"✅ Orçamento {numero_orcamento} gerado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Preencha pelo menos o nome do cliente e descrição do evento")
        
        # Mostrar botão de download se PDF foi gerado
        if 'pdf_gerado' in st.session_state:
            st.markdown(f"""
            <div class="success-box">
                ✅ Orçamento {st.session_state.pdf_gerado['numero']} pronto para download!
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de download (FORA do form)
            st.download_button(
                label="📥 Download do Orçamento PDF",
                data=st.session_state.pdf_gerado['buffer'],
                file_name=st.session_state.pdf_gerado['filename'],
                mime="application/pdf",
                use_container_width=True
            )
            
            # Botão para limpar orçamento
            if st.button("🗑️ Limpar Orçamento e Criar Novo", use_container_width=True):
                st.session_state.itens_orcamento = []
                if 'pdf_gerado' in st.session_state:
                    del st.session_state.pdf_gerado
                st.rerun()
    
    with tab5:
        st.markdown("### 🛠️ Catálogo de Produtos")
        
        if not df_produtos.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_categoria_cat = st.selectbox("Filtrar por Categoria", 
                                                  ["Todas"] + list(df_produtos['categoria'].unique()),
                                                  key="filtro_cat_catalogo")
            
            with col2:
                busca_produto = st.text_input("Buscar Produto", key="busca_produto")
            
            with col3:
                ordenar_por = st.selectbox("Ordenar por", 
                                         ["Nome", "Preço (Menor)", "Preço (Maior)", "Categoria"],
                                         key="ordenar_catalogo")
            
            # Aplicar filtros
            df_catalogo = df_produtos.copy()
            
            if filtro_categoria_cat != "Todas":
                df_catalogo = df_catalogo[df_catalogo['categoria'] == filtro_categoria_cat]
            
            if busca_produto:
                df_catalogo = df_catalogo[df_catalogo['produto'].str.contains(busca_produto, case=False, na=False)]
            
            # Ordenar
            if ordenar_por == "Nome":
                df_catalogo = df_catalogo.sort_values('produto')
            elif ordenar_por == "Preço (Menor)":
                df_catalogo = df_catalogo.sort_values('valor_diaria')
            elif ordenar_por == "Preço (Maior)":
                df_catalogo = df_catalogo.sort_values('valor_diaria', ascending=False)
            elif ordenar_por == "Categoria":
                df_catalogo = df_catalogo.sort_values('categoria')
            
            # Mostrar produtos
            st.markdown(f"**📊 Produtos encontrados:** {len(df_catalogo)}")
            
            # Exibir em cards
            for i in range(0, len(df_catalogo), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(df_catalogo):
                        produto = df_catalogo.iloc[i + j]
                        with col:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{produto['produto']}</h4>
                                <p><strong>Categoria:</strong> {produto['categoria']}</p>
                                <p><strong>Unidades:</strong> {produto['unidades']}</p>
                                <h3>R$ {produto['valor_diaria']:.2f}/dia</h3>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("📦 Nenhum produto encontrado no catálogo")
    
    with tab6:
        st.markdown("### ⚠️ Alertas e Insights")
        
        # Combinar pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            # Alertas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚨 Alertas Críticos")
                
                # Pedidos pendentes
                pedidos_pendentes = len(todos_pedidos[todos_pedidos['status'] == 'Pendente'])
                if pedidos_pendentes > 0:
                    st.error(f"⚠️ {pedidos_pendentes} pedido(s) pendente(s) de confirmação")
                
                # Pedidos sem valor
                pedidos_sem_valor = len(todos_pedidos[todos_pedidos['valor'] == 0])
                if pedidos_sem_valor > 0:
                    st.warning(f"💰 {pedidos_sem_valor} pedido(s) sem valor definido")
                
                # Margem baixa
                receita_total = todos_pedidos['valor'].sum()
                custos_totais = todos_pedidos['custos'].sum()
                margem = ((receita_total - custos_totais) / receita_total * 100) if receita_total > 0 else 0
                
                if margem < 30:
                    st.warning(f"📉 Margem de lucro baixa: {margem:.1f}% (Meta: >30%)")
                else:
                    st.success(f"📈 Margem de lucro saudável: {margem:.1f}%")
            
            with col2:
                st.markdown("#### 💡 Insights")
                
                # Categoria mais lucrativa
                receita_categoria = todos_pedidos.groupby('categoria')['valor'].sum()
                categoria_top = receita_categoria.idxmax()
                st.info(f"🏆 Categoria mais lucrativa: {categoria_top}")
                
                # Cliente com mais pedidos
                cliente_top = todos_pedidos['cliente'].value_counts().idxmax()
                st.info(f"👥 Cliente com mais pedidos: {cliente_top}")
                
                # Próximos eventos
                hoje = datetime.now().date()
                proximos_30_dias = 0
                
                for _, pedido in todos_pedidos.iterrows():
                    try:
                        data_entrega = pd.to_datetime(pedido['data_entrega']).date()
                        if hoje <= data_entrega <= hoje + timedelta(days=30):
                            proximos_30_dias += 1
                    except:
                        continue
                
                if proximos_30_dias > 0:
                    st.info(f"📅 {proximos_30_dias} evento(s) nos próximos 30 dias")
                else:
                    st.info("📅 Nenhum evento programado para os próximos 30 dias")
        else:
            st.info("📊 Nenhum dado disponível para gerar alertas")

if __name__ == "__main__":
    main()
