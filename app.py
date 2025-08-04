"""
Dashboard Primeira Linha Eventos - VERSÃO COM LOGÍSTICA
Sistema completo: Comercial + Logística (Marcelão)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import io
import os
import base64

# Configuração da página
st.set_page_config(
    page_title="Primeira Linha Eventos - Sistema Completo",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
    
    .metric-card.green { border-left-color: #10b981; }
    .metric-card.blue { border-left-color: #3b82f6; }
    .metric-card.purple { border-left-color: #8b5cf6; }
    .metric-card.orange { border-left-color: #f59e0b; }
    
    .logistica-container {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #D4AF37;
        margin: 1rem 0;
    }
    
    .documento-card {
        background: #374151;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #D4AF37;
    }
    
    .status-pendente { border-left-color: #f59e0b; }
    .status-completo { border-left-color: #10b981; }
    .status-enviado { border-left-color: #3b82f6; }
    
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
</style>
""", unsafe_allow_html=True)

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

# Dados de pedidos
@st.cache_data(ttl=600)
def gerar_dados_pedidos():
    """Dados de pedidos existentes"""
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
            'status': 'Finalizado',
            'status_logistica': 'Pendente Docs'
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
            'status': 'Finalizado',
            'status_logistica': 'Docs Completos'
        },
        {
            'numero_pedido': 'PED003',
            'cliente': 'Programa Sempre por Elas',
            'categoria': 'Público Extra',
            'produto_servico': 'Carrinho de Pipoca, Monitor/TV',
            'valor': 9080.0,
            'custos': 5500.0,
            'local': 'Curralinho',
            'data_entrega': '2025-01-10',
            'status': 'Confirmado',
            'status_logistica': 'Enviado Campo'
        }
    ]
    return pd.DataFrame(pedidos)

# Lista de documentos da logística
DOCUMENTOS_LOGISTICA = [
    "Ordem de Separação",
    "Confirmação de Reserva", 
    "Romaneio de Entrega",
    "Termo de Recebimento",
    "Ordem de Recolhimento",
    "Relatório de Inspeção"
]

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
    
    # Conteúdo específico por tipo de documento
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
        c.drawString(50, y_position, f"Data do Evento: {dados_pedido['data_entrega']}")
        y_position -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "EQUIPAMENTOS A SEPARAR:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        produtos = dados_pedido['produto_servico'].split(', ')
        for produto in produtos:
            c.drawString(70, y_position, f"• {produto}")
            y_position -= 15
    
    elif tipo_documento == "Romaneio de Entrega":
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, f"ROMANEIO DE ENTREGA - {dados_pedido['numero_pedido']}")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Cliente: {dados_pedido['cliente']}")
        y_position -= 20
        c.drawString(50, y_position, f"Local de Entrega: {dados_pedido['local']}")
        y_position -= 20
        
        if 'data_entrega_logistica' in dados_logistica:
            c.drawString(50, y_position, f"Data/Hora Entrega: {dados_logistica['data_entrega_logistica']} às {dados_logistica.get('hora_entrega_logistica', 'A definir')}")
            y_position -= 20
        
        if 'data_recolhimento_logistica' in dados_logistica:
            c.drawString(50, y_position, f"Data/Hora Recolhimento: {dados_logistica['data_recolhimento_logistica']} às {dados_logistica.get('hora_recolhimento_logistica', 'A definir')}")
            y_position -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "ITENS PARA ENTREGA:")
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
    c.drawString(50, 35, "Primeira Linha Eventos - Sistema de Logística")
    c.drawString(50, 25, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    c.drawString(50, 15, "primeiralinhaeventos@gmail.com | (61) 991334258")
    
    c.save()
    buffer.seek(0)
    return buffer

# Função principal
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎪 PRIMEIRA LINHA EVENTOS</h1>
        <h3>Sistema Completo: Comercial + Logística v6.0</h3>
        <p>Dashboard + Orçamentos + Gestão de Documentos Logísticos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("### 🎯 Navegação")
    
    if st.sidebar.button("📝 NOVO PEDIDO", use_container_width=True):
        st.session_state.show_novo_pedido = True
    
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    df_produtos = carregar_produtos_sheets()
    df_pedidos = gerar_dados_pedidos()
    
    if df_produtos.empty:
        st.error("❌ Erro ao carregar planilha")
        return
    
    # Formulário novo pedido
    if st.session_state.get('show_novo_pedido', False):
        st.markdown("### ➕ Novo Pedido")
        
        with st.form("novo_pedido"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Cliente*")
                categoria = st.selectbox("Categoria*", [
                    "Público Extra", "Corporativo", "Particular"
                ])
                produtos_selecionados = st.multiselect(
                    "Produtos*", df_produtos['produto'].tolist()
                )
                valor = st.number_input("Valor (R$)*", min_value=0.0)
            
            with col2:
                custos = st.number_input("Custos (R$)", min_value=0.0)
                local = st.text_input("Local")
                data_entrega = st.date_input("Data Entrega")
                status = st.selectbox("Status", [
                    "Em Negociação", "Confirmado", "Finalizado"
                ])
            
            if st.form_submit_button("💾 Salvar"):
                if cliente and categoria and produtos_selecionados and valor > 0:
                    novo_numero = f"PED{len(df_pedidos) + 1:03d}"
                    
                    novo_pedido = {
                        'numero_pedido': novo_numero,
                        'cliente': cliente,
                        'categoria': categoria,
                        'produto_servico': ', '.join(produtos_selecionados),
                        'valor': valor,
                        'custos': custos,
                        'local': local,
                        'data_entrega': data_entrega.strftime('%Y-%m-%d'),
                        'status': status,
                        'status_logistica': 'Pendente Docs'
                    }
                    
                    if 'novos_pedidos' not in st.session_state:
                        st.session_state.novos_pedidos = []
                    
                    st.session_state.novos_pedidos.append(novo_pedido)
                    st.success(f"✅ Pedido {novo_numero} salvo!")
                    st.session_state.show_novo_pedido = False
                    st.rerun()
                else:
                    st.error("❌ Preencha campos obrigatórios")
        
        if st.button("❌ Fechar"):
            st.session_state.show_novo_pedido = False
            st.rerun()
        
        st.divider()
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "📦 Pedidos", 
        "🚚 Logística",  # NOVA ABA
        "🎯 Orçamentos",
        "🛠️ Catálogo"
    ])
    
    with tab1:
        st.markdown("### 📊 Dashboard Principal")
        
        # Combinar pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            receita_total = todos_pedidos['valor'].sum()
            custos_totais = todos_pedidos['custos'].sum()
            lucro_total = receita_total - custos_totais
            
            # KPIs Logísticos
            pendentes_docs = len(todos_pedidos[todos_pedidos['status_logistica'] == 'Pendente Docs'])
            
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
                    <h4>📦 Total Pedidos</h4>
                    <h2>{len(todos_pedidos)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card orange">
                    <h4>🚚 Pendentes Docs</h4>
                    <h2>{pendentes_docs}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                receita_categoria = todos_pedidos.groupby('categoria')['valor'].sum().reset_index()
                fig = px.pie(receita_categoria, values='valor', names='categoria',
                            title="💼 Receita por Categoria")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                status_logistica = todos_pedidos['status_logistica'].value_counts().reset_index()
                fig2 = px.bar(status_logistica, x='status_logistica', y='count',
                             title="🚚 Status Logística")
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("### 📦 Gestão de Pedidos")
        
        # Combinar pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            st.markdown(f"**📊 Total:** {len(todos_pedidos)} pedidos")
            
            # Lista de pedidos
            for i, (idx, pedido) in enumerate(todos_pedidos.iterrows()):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{pedido['numero_pedido']}** - {pedido['cliente']}")
                
                with col2:
                    st.markdown(f"R$ {pedido['valor']:,.2f} - {pedido['status']}")
                
                with col3:
                    st.markdown(f"{pedido['data_entrega']}")
                
                with col4:
                    status_logistica = pedido.get('status_logistica', 'Pendente Docs')
                    if status_logistica == 'Pendente Docs':
                        st.markdown("🟡 Pendente")
                    elif status_logistica == 'Docs Completos':
                        st.markdown("🟢 Completo")
                    else:
                        st.markdown("🔵 Enviado")
                
                with col5:
                    # Botão excluir apenas para novos pedidos
                    if 'novos_pedidos' in st.session_state:
                        pedidos_novos = [p['numero_pedido'] for p in st.session_state.novos_pedidos]
                        if pedido['numero_pedido'] in pedidos_novos:
                            if st.button("🗑️", key=f"del_{pedido['numero_pedido']}"):
                                st.session_state.novos_pedidos = [
                                    p for p in st.session_state.novos_pedidos 
                                    if p['numero_pedido'] != pedido['numero_pedido']
                                ]
                                st.success("✅ Excluído!")
                                st.rerun()
                        else:
                            st.markdown("*Fixo*")
                
                st.divider()
    
    with tab3:  # NOVA ABA LOGÍSTICA
        st.markdown("### 🚚 Logística - Gestão de Documentos")
        st.markdown("**👨‍💼 Área do Marcelão - Gerente de Logística**")
        
        # Combinar pedidos
        todos_pedidos = df_pedidos.copy()
        if 'novos_pedidos' in st.session_state:
            novos_df = pd.DataFrame(st.session_state.novos_pedidos)
            if not novos_df.empty:
                todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
        
        if not todos_pedidos.empty:
            # Seletor de pedido
            st.markdown("#### 📋 Selecionar Pedido para Gestão")
            
            pedidos_opcoes = [f"{row['numero_pedido']} - {row['cliente']}" for _, row in todos_pedidos.iterrows()]
            pedido_selecionado = st.selectbox("Escolha o pedido:", pedidos_opcoes)
            
            if pedido_selecionado:
                # Extrair dados do pedido selecionado
                numero_pedido = pedido_selecionado.split(' - ')[0]
                dados_pedido = todos_pedidos[todos_pedidos['numero_pedido'] == numero_pedido].iloc[0]
                
                st.markdown(f"""
                <div class="logistica-container">
                    <h4>📦 {dados_pedido['numero_pedido']} - {dados_pedido['cliente']}</h4>
                    <p><strong>Local:</strong> {dados_pedido['local']}</p>
                    <p><strong>Produtos:</strong> {dados_pedido['produto_servico']}</p>
                    <p><strong>Data do Evento:</strong> {dados_pedido['data_entrega']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Seção de Datas e Horários Logísticos
                st.markdown("#### 📅 Datas e Horários de Entrega/Recolhimento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🚚 ENTREGA**")
                    data_entrega_log = st.date_input("Data de Entrega", key=f"data_ent_{numero_pedido}")
                    hora_entrega_log = st.time_input("Horário de Entrega", key=f"hora_ent_{numero_pedido}")
                    responsavel_entrega = st.text_input("Responsável pela Recepção", key=f"resp_ent_{numero_pedido}")
                    obs_entrega = st.text_area("Observações da Entrega", key=f"obs_ent_{numero_pedido}")
                
                with col2:
                    st.markdown("**📦 RECOLHIMENTO**")
                    data_recolhimento_log = st.date_input("Data de Recolhimento", key=f"data_rec_{numero_pedido}")
                    hora_recolhimento_log = st.time_input("Horário de Recolhimento", key=f"hora_rec_{numero_pedido}")
                    responsavel_recolhimento = st.text_input("Responsável pela Liberação", key=f"resp_rec_{numero_pedido}")
                    obs_recolhimento = st.text_area("Observações do Recolhimento", key=f"obs_rec_{numero_pedido}")
                
                # Seção de Documentos
                st.markdown("#### 📄 Gestão de Documentos")
                
                # Inicializar documentos no session_state
                if f'docs_{numero_pedido}' not in st.session_state:
                    st.session_state[f'docs_{numero_pedido}'] = {doc: None for doc in DOCUMENTOS_LOGISTICA}
                
                # Mostrar documentos em cards
                for i, documento in enumerate(DOCUMENTOS_LOGISTICA):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        status_doc = "✅ Anexado" if st.session_state[f'docs_{numero_pedido}'][documento] else "⏳ Pendente"
                        status_class = "status-completo" if status_doc == "✅ Anexado" else "status-pendente"
                        
                        st.markdown(f"""
                        <div class="documento-card {status_class}">
                            <h5>{documento}</h5>
                            <p>{status_doc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Upload de arquivo
                        uploaded_file = st.file_uploader(
                            f"Upload {documento}", 
                            type=['pdf', 'jpg', 'jpeg', 'png'],
                            key=f"upload_{documento}_{numero_pedido}"
                        )
                        
                        if uploaded_file:
                            st.session_state[f'docs_{numero_pedido}'][documento] = uploaded_file
                            st.success("✅ Anexado!")
                    
                    with col3:
                        # Botão para gerar documento automaticamente
                        if documento in ["Ordem de Separação", "Romaneio de Entrega"]:
                            if st.button(f"📄 Gerar", key=f"gerar_{documento}_{numero_pedido}"):
                                dados_logistica = {
                                    'data_entrega_logistica': data_entrega_log.strftime('%d/%m/%Y') if data_entrega_log else '',
                                    'hora_entrega_logistica': hora_entrega_log.strftime('%H:%M') if hora_entrega_log else '',
                                    'data_recolhimento_logistica': data_recolhimento_log.strftime('%d/%m/%Y') if data_recolhimento_log else '',
                                    'hora_recolhimento_logistica': hora_recolhimento_log.strftime('%H:%M') if hora_recolhimento_log else ''
                                }
                                
                                pdf_buffer = gerar_documento_logistica(documento, dados_pedido, dados_logistica)
                                
                                st.download_button(
                                    label=f"📥 Download {documento}",
                                    data=pdf_buffer.getvalue(),
                                    file_name=f"{documento}_{numero_pedido}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{documento}_{numero_pedido}"
                                )
                
                # Botão para salvar informações logísticas
                if st.button("💾 Salvar Informações Logísticas", use_container_width=True):
                    # Aqui você salvaria as informações no banco de dados
                    st.success("✅ Informações logísticas salvas com sucesso!")
                    
                    # Atualizar status do pedido
                    docs_completos = all(st.session_state[f'docs_{numero_pedido}'][doc] is not None for doc in DOCUMENTOS_LOGISTICA)
                    if docs_completos:
                        st.balloons()
                        st.success("🎉 Todos os documentos foram anexados! Pedido pronto para envio ao campo.")
        else:
            st.info("📦 Nenhum pedido encontrado para gestão logística")
    
    with tab4:
        st.markdown("### 🎯 Gerador de Orçamentos")
        
        # Inicializar itens
        if 'itens_orcamento' not in st.session_state:
            st.session_state.itens_orcamento = []
        
        # Adicionar item
        st.markdown("#### ➕ Adicionar Item")
        
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            produto = st.selectbox("Produto", df_produtos['produto'].tolist())
        
        with col2:
            quantidade = st.number_input("Qtd", min_value=1, value=1)
        
        with col3:
            diarias = st.number_input("Diárias", min_value=1, value=1)
        
        with col4:
            preco_padrao = df_produtos[df_produtos['produto'] == produto]['valor_diaria'].iloc[0] if not df_produtos.empty else 0
            preco = st.number_input("Preço", min_value=0.0, value=float(preco_padrao))
        
        with col5:
            if st.button("➕ Add"):
                total = quantidade * diarias * preco
                item = {
                    'produto': produto,
                    'quantidade': quantidade,
                    'diarias': diarias,
                    'preco_unitario': preco,
                    'preco_total': total
                }
                st.session_state.itens_orcamento.append(item)
                st.rerun()
        
        # Mostrar itens e resto da funcionalidade de orçamentos...
        if st.session_state.itens_orcamento:
            st.markdown("#### 📋 Itens do Orçamento")
            
            for i, item in enumerate(st.session_state.itens_orcamento):
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(item['produto'])
                with col2:
                    st.markdown(str(item['quantidade']))
                with col3:
                    st.markdown(str(item['diarias']))
                with col4:
                    st.markdown(f"R$ {item['preco_total']:.2f}")
                with col5:
                    if st.button("🗑️", key=f"rem_{i}"):
                        st.session_state.itens_orcamento.pop(i)
                        st.rerun()
            
            # Total
            valor_total = sum(item['preco_total'] for item in st.session_state.itens_orcamento)
            st.markdown(f"""
            <div class="success-box">
                <h3>💰 TOTAL: R$ {valor_total:,.2f}</h3>
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 🛠️ Catálogo")
        
        if not df_produtos.empty:
            st.markdown(f"**📊 Produtos:** {len(df_produtos)}")
            
            # Mostrar produtos em cards
            for i in range(0, len(df_produtos), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(df_produtos):
                        produto = df_produtos.iloc[i + j]
                        with col:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{produto['produto']}</h4>
                                <p><strong>Categoria:</strong> {produto['categoria']}</p>
                                <h3>R$ {produto['valor_diaria']:.2f}/dia</h3>
                            </div>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
