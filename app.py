import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import calendar

# Configuração da página
st.set_page_config(
    page_title="Dashboard Primeira Linha Eventos",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores premium - Fundo azul escuro conforme solicitado
CORES_PREMIUM = {
    'azul_escuro_fundo': '#0B1426',      # Fundo azul escuro principal
    'azul_medio': '#1E3A5F',             # Azul médio para cards
    'azul_claro': '#2E5984',             # Azul claro para destaques
    'dourado_premium': '#FFD700',        # Dourado premium
    'dourado_suave': '#F4D03F',          # Dourado mais suave
    'branco_puro': '#FFFFFF',            # Branco puro para textos
    'cinza_claro': '#E8F4FD',            # Cinza claro para backgrounds
    'verde_sucesso': '#00D4AA',          # Verde moderno para sucessos
    'laranja_alerta': '#FF6B35',         # Laranja para alertas
    'vermelho_erro': '#FF4757',          # Vermelho para erros
    'roxo_premium': '#6C5CE7',           # Roxo premium para destaques
    'azul_info': '#74B9FF'               # Azul para informações
}

# CSS customizado premium com fundo azul escuro
st.markdown(f"""
<style>
    /* Importar fontes premium */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Reset e configurações globais */
    .stApp {{
        background: linear-gradient(135deg, {CORES_PREMIUM['azul_escuro_fundo']} 0%, #0F1B2E 100%);
        font-family: 'Inter', sans-serif;
    }}
    
    /* Sidebar premium */
    .css-1d391kg {{
        background: linear-gradient(180deg, {CORES_PREMIUM['azul_medio']} 0%, {CORES_PREMIUM['azul_escuro_fundo']} 100%);
        border-right: 1px solid {CORES_PREMIUM['azul_claro']};
    }}
    
    /* Cabeçalho premium */
    .header-premium {{
        background: linear-gradient(135deg, {CORES_PREMIUM['azul_medio']} 0%, {CORES_PREMIUM['azul_claro']} 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid {CORES_PREMIUM['dourado_premium']};
    }}
    
    .header-title {{
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: {CORES_PREMIUM['branco_puro']};
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        letter-spacing: -1px;
    }}
    
    .header-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 400;
        color: {CORES_PREMIUM['cinza_claro']};
        opacity: 0.9;
    }}
    
    /* Cards de métricas premium */
    .metric-card-premium {{
        background: linear-gradient(135deg, {CORES_PREMIUM['azul_medio']} 0%, {CORES_PREMIUM['azul_claro']} 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 1px solid {CORES_PREMIUM['dourado_suave']};
        margin-bottom: 1.5rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {CORES_PREMIUM['dourado_premium']} 0%, {CORES_PREMIUM['dourado_suave']} 100%);
    }}
    
    .metric-card-premium:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }}
    
    .metric-value-premium {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: {CORES_PREMIUM['branco_puro']};
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }}
    
    .metric-label-premium {{
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        color: {CORES_PREMIUM['cinza_claro']};
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}
    
    /* Seções de gráficos premium */
    .chart-section-premium {{
        background: linear-gradient(135deg, {CORES_PREMIUM['azul_medio']} 0%, {CORES_PREMIUM['azul_escuro_fundo']} 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 1px solid {CORES_PREMIUM['azul_claro']};
        margin-bottom: 2rem;
    }}
    
    .chart-title-premium {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: {CORES_PREMIUM['branco_puro']};
        margin-bottom: 1.5rem;
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }}
    
    /* Velocímetros premium */
    .velocimetro-premium {{
        background: linear-gradient(135deg, {CORES_PREMIUM['azul_medio']} 0%, {CORES_PREMIUM['azul_claro']} 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid {CORES_PREMIUM['dourado_suave']};
    }}
    
    .velocimetro-title-premium {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: {CORES_PREMIUM['branco_puro']};
        margin-bottom: 1rem;
    }}
    
    /* Abas premium */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: {CORES_PREMIUM['azul_escuro_fundo']};
        border-radius: 12px;
        padding: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {CORES_PREMIUM['azul_medio']};
        color: {CORES_PREMIUM['cinza_claro']};
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid {CORES_PREMIUM['azul_claro']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {CORES_PREMIUM['dourado_premium']} 0%, {CORES_PREMIUM['dourado_suave']} 100%);
        color: {CORES_PREMIUM['azul_escuro_fundo']};
        font-weight: 600;
    }}
    
    /* Textos gerais */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {CORES_PREMIUM['branco_puro']};
        font-family: 'Poppins', sans-serif;
    }}
    
    .stMarkdown p {{
        color: {CORES_PREMIUM['cinza_claro']};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Sidebar styling */
    .css-1d391kg .stMarkdown {{
        color: {CORES_PREMIUM['cinza_claro']};
    }}
    
    .css-1d391kg .stSelectbox label {{
        color: {CORES_PREMIUM['branco_puro']};
        font-weight: 500;
    }}
</style>
""", unsafe_allow_html=True)

# Função para carregar e limpar dados (mantida igual)
@st.cache_data
def load_and_clean_data(file_path):
    """Carrega e limpa os dados da planilha de pedidos"""
    try:
        df = pd.read_csv(file_path)
        
        # Renomear colunas para padronização
        df.columns = [
            'ID do Pedido', 'Cliente/Projeto', 'Categoria', 'Produto/Serviço', 
            'Valor Total', 'Custo do Pedido', 'Diárias Equipe', 'Local', 
            'Data Entrega', 'Data Recolhimento', 'Data Pagamento'
        ]

        # Tratar dados conforme implementado anteriormente
        df['Categoria'] = df['Categoria'].replace({
            'particular': 'Privado', 
            'Público Extra': 'Público EXTRA',
            'público': 'Público',
            'público extra': 'Público EXTRA',
            'privado': 'Privado'
        })

        # Padronizar valores pendentes
        df['Valor Total'] = df['Valor Total'].replace({'a definir': 'A DEFINIR'})
        df['Valor_Pendente'] = df['Valor Total'].apply(lambda x: True if str(x).upper() in ['A DEFINIR', 'NAN'] else False)
        df['Valor_Numerico'] = pd.to_numeric(df['Valor Total'], errors='coerce')

        # Limpar custos e diárias
        df['Custo_Original'] = df['Custo do Pedido'].copy()
        df['Custo_Pendente'] = df['Custo do Pedido'].apply(lambda x: True if str(x).lower() in ['x', 'nan'] else False)
        df['Custo_Numerico'] = df['Custo do Pedido'].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        df['Diarias_Original'] = df['Diárias Equipe'].copy()
        df['Diarias_Pendente'] = df['Diárias Equipe'].apply(lambda x: True if str(x).lower() in ['x', 'nan'] else False)
        df['Diarias_Numerico'] = df['Diárias Equipe'].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # Converter datas
        date_columns = ['Data Entrega', 'Data Recolhimento', 'Data Pagamento']
        for col in date_columns:
            df[f'{col}_Pendente'] = df[col].apply(lambda x: True if str(x).lower() in ['indefinido', 'nan'] else False)
            df[col] = df[col].replace({'indefinido': np.nan})
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        
        # Adicionar data do pedido
        df['Data do Pedido'] = df['Data Entrega'].fillna(pd.to_datetime(datetime.now().date())) - pd.Timedelta(days=1)

        # Status de pagamento
        df['Status Pagamento'] = df['Data Pagamento'].apply(
            lambda x: 'Pago' if pd.notna(x) and x <= datetime.now() 
            else ('Pendente' if pd.notna(x) and x > datetime.now() else 'Indefinido')
        )
        
        df.loc[(df['Status Pagamento'] == 'Pendente') & (df['Data Entrega'] < datetime.now()), 'Status Pagamento'] = 'Atrasado'

        # Calcular lucro bruto
        custo_diaria_padrao = 150.00
        df['Custo_Diarias'] = df['Diarias_Numerico'] * custo_diaria_padrao
        df['Custo_Total'] = df['Custo_Numerico'] + df['Custo_Diarias']
        
        df['Lucro Bruto'] = np.where(
            df['Valor_Pendente'] | df['Custo_Pendente'] | df['Diarias_Pendente'],
            np.nan,
            df['Valor_Numerico'] - df['Custo_Total']
        )
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Função para criar gráficos mensais completos (12 meses)
def criar_grafico_mensal_completo(df_dados, coluna_valor, titulo, cor, ano_atual=2025):
    """Cria gráfico com todos os 12 meses do ano"""
    
    # Criar DataFrame com todos os meses
    meses_completos = pd.DataFrame({
        'Mes': range(1, 13),
        'Nome_Mes': [calendar.month_abbr[i] for i in range(1, 13)],
        'Valor': [0] * 12
    })
    
    if not df_dados.empty:
        # Agrupar dados por mês
        df_dados['Mes'] = df_dados['Data do Pedido'].dt.month
        dados_agrupados = df_dados.groupby('Mes')[coluna_valor].sum().reset_index()
        
        # Mesclar com meses completos
        for _, row in dados_agrupados.iterrows():
            meses_completos.loc[meses_completos['Mes'] == row['Mes'], 'Valor'] = row[coluna_valor]
    
    # Criar gráfico
    fig = px.bar(
        meses_completos,
        x='Nome_Mes',
        y='Valor',
        title=titulo,
        color_discrete_sequence=[cor]
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=12, color=CORES_PREMIUM['branco_puro']),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        showlegend=False,
        xaxis=dict(
            gridcolor=CORES_PREMIUM['azul_claro'],
            tickfont=dict(color=CORES_PREMIUM['cinza_claro'])
        ),
        yaxis=dict(
            gridcolor=CORES_PREMIUM['azul_claro'],
            tickfont=dict(color=CORES_PREMIUM['cinza_claro'])
        ),
        title=dict(
            font=dict(color=CORES_PREMIUM['branco_puro'], size=16),
            x=0.5
        )
    )
    
    return fig

# Função para criar velocímetro premium
def criar_velocimetro_premium(valor, titulo, subtitulo=""):
    """Cria um gráfico de velocímetro premium"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': titulo, 'font': {'size': 14, 'color': CORES_PREMIUM['branco_puro']}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': CORES_PREMIUM['cinza_claro']},
            'bar': {'color': CORES_PREMIUM['dourado_premium']},
            'bgcolor': CORES_PREMIUM['azul_medio'],
            'borderwidth': 2,
            'bordercolor': CORES_PREMIUM['azul_claro'],
            'steps': [
                {'range': [0, 50], 'color': CORES_PREMIUM['vermelho_erro']},
                {'range': [50, 80], 'color': CORES_PREMIUM['laranja_alerta']},
                {'range': [80, 100], 'color': CORES_PREMIUM['verde_sucesso']}
            ],
            'threshold': {
                'line': {'color': CORES_PREMIUM['dourado_premium'], 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        font={'color': CORES_PREMIUM['branco_puro'], 'family': "Inter"},
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Cabeçalho premium
st.markdown(f"""
<div class="header-premium">
    <div class="header-title">
        🎪 PRIMEIRA LINHA EVENTOS
    </div>
    <div class="header-subtitle">
        Dashboard de Gestão de Pedidos e Performance
    </div>
</div>
""", unsafe_allow_html=True)

# Carregar dados
df = load_and_clean_data('Planilhasemtítulo-Página1.csv')

if not df.empty:
    # Sidebar premium com filtros
    with st.sidebar:
        st.markdown("### 🔍 Filtros de Análise")
        
        categorias = ["Todos"] + sorted(df["Categoria"].dropna().unique().tolist())
        categoria_selecionada = st.selectbox("📋 Categoria", categorias)
        
        status_pagamento = ["Todos"] + sorted(df["Status Pagamento"].unique().tolist())
        status_selecionado = st.selectbox("💰 Status Pagamento", status_pagamento)
        
        st.markdown("### 📅 Período")
        min_date = df["Data do Pedido"].min().date() if pd.notna(df["Data do Pedido"].min()) else datetime.now().date() - timedelta(days=30)
        max_date = df["Data do Pedido"].max().date() if pd.notna(df["Data do Pedido"].max()) else datetime.now().date()

        data_inicio = st.date_input("Data Início", min_date)
        data_fim = st.date_input("Data Fim", max_date)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if categoria_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_selecionada]
    
    if status_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status Pagamento"] == status_selecionado]
    
    df_filtrado = df_filtrado[
        (df_filtrado["Data do Pedido"] >= pd.to_datetime(data_inicio)) &
        (df_filtrado["Data do Pedido"] <= pd.to_datetime(data_fim))
    ]
    
    # Criar abas premium
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Evolução Temporal"])
    
    with tab1:
        # PRIMEIRA PARTE: MÉTRICAS PREMIUM
        st.markdown("## 📈 Métricas Operacionais")
        
        # Calcular métricas principais
        df_com_valores = df_filtrado[~df_filtrado['Valor_Pendente']]
        
        receita_total = df_com_valores["Valor_Numerico"].sum()
        custo_total = df_com_valores["Custo_Total"].sum()
        lucro_total = df_com_valores["Lucro Bruto"].sum()
        margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
        margem_contribuicao = ((receita_total - custo_total) / receita_total * 100) if receita_total > 0 else 0
        
        # Métricas no topo premium
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['laranja_alerta']};">R$ {custo_total:,.0f}</div>
                <div class="metric-label-premium">Despesa</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['verde_sucesso']};">R$ {receita_total:,.0f}</div>
                <div class="metric-label-premium">Receita</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['dourado_premium']};">{margem_lucro:.1f}%</div>
                <div class="metric-label-premium">% Lucro</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            custo_operacional = df_com_valores["Custo_Numerico"].sum()
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['azul_info']};">R$ {custo_operacional:,.0f}</div>
                <div class="metric-label-premium">Custo</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['roxo_premium']};">{margem_contribuicao:.1f}%</div>
                <div class="metric-label-premium">% M. Contrib.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            meta_categoria = receita_total / len(df_com_valores["Categoria"].unique()) if len(df_com_valores["Categoria"].unique()) > 0 else 0
            st.markdown(f"""
            <div class="metric-card-premium">
                <div class="metric-value-premium" style="color: {CORES_PREMIUM['verde_sucesso']};">R$ {meta_categoria:,.0f}</div>
                <div class="metric-label-premium">Meta Por Categoria</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos principais premium com 12 meses
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-section-premium">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title-premium">🔥 Despesa Operacional Mensal</div>', unsafe_allow_html=True)
            
            fig_despesa = criar_grafico_mensal_completo(
                df_com_valores, 'Custo_Total', 
                "Despesas por Mês", CORES_PREMIUM['laranja_alerta']
            )
            st.plotly_chart(fig_despesa, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-section-premium">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title-premium">📈 Receita Operacional Mensal</div>', unsafe_allow_html=True)
            
            fig_receita = criar_grafico_mensal_completo(
                df_com_valores, 'Valor_Numerico', 
                "Receitas por Mês", CORES_PREMIUM['verde_sucesso']
            )
            st.plotly_chart(fig_receita, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # SEGUNDA PARTE: VELOCÍMETROS PREMIUM
        st.markdown("## ⚡ Indicadores de Conclusão")
        
        # Calcular porcentagens de preenchimento
        total_pedidos = len(df_filtrado)
        
        if total_pedidos > 0:
            perc_ids = ((total_pedidos - df_filtrado['ID do Pedido'].isna().sum()) / total_pedidos) * 100
            perc_valores = ((total_pedidos - df_filtrado['Valor_Pendente'].sum()) / total_pedidos) * 100
            perc_custos = ((total_pedidos - df_filtrado['Custo_Pendente'].sum()) / total_pedidos) * 100
            perc_diarias = ((total_pedidos - df_filtrado['Diarias_Pendente'].sum()) / total_pedidos) * 100
            perc_pagamentos = ((total_pedidos - df_filtrado['Data Pagamento_Pendente'].sum()) / total_pedidos) * 100
        else:
            perc_ids = perc_valores = perc_custos = perc_diarias = perc_pagamentos = 0
        
        # Velocímetros em colunas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown('<div class="velocimetro-premium">', unsafe_allow_html=True)
            st.markdown('<div class="velocimetro-title-premium">🆔 IDs dos Pedidos</div>', unsafe_allow_html=True)
            fig_ids = criar_velocimetro_premium(perc_ids, "")
            st.plotly_chart(fig_ids, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="velocimetro-premium">', unsafe_allow_html=True)
            st.markdown('<div class="velocimetro-title-premium">💰 Valores Definidos</div>', unsafe_allow_html=True)
            fig_valores = criar_velocimetro_premium(perc_valores, "")
            st.plotly_chart(fig_valores, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="velocimetro-premium">', unsafe_allow_html=True)
            st.markdown('<div class="velocimetro-title-premium">💸 Custos Informados</div>', unsafe_allow_html=True)
            fig_custos = criar_velocimetro_premium(perc_custos, "")
            st.plotly_chart(fig_custos, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="velocimetro-premium">', unsafe_allow_html=True)
            st.markdown('<div class="velocimetro-title-premium">👥 Diárias Registradas</div>', unsafe_allow_html=True)
            fig_diarias = criar_velocimetro_premium(perc_diarias, "")
            st.plotly_chart(fig_diarias, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col5:
            st.markdown('<div class="velocimetro-premium">', unsafe_allow_html=True)
            st.markdown('<div class="velocimetro-title-premium">📅 Datas de Pagamento</div>', unsafe_allow_html=True)
            fig_pagamentos = criar_velocimetro_premium(perc_pagamentos, "")
            st.plotly_chart(fig_pagamentos, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 📈 Evolução Temporal")
        
        # Análise temporal premium
        if not df_com_valores.empty:
            # Gráfico de evolução anual
            df_temporal = df_com_valores.copy()
            df_temporal['Mes_Ano'] = df_temporal['Data do Pedido'].dt.to_period('M')
            
            evolucao_mensal = df_temporal.groupby('Mes_Ano').agg({
                'Valor_Numerico': 'sum',
                'Custo_Total': 'sum',
                'Lucro Bruto': 'sum'
            }).reset_index()
            
            evolucao_mensal['Mes_Ano_Str'] = evolucao_mensal['Mes_Ano'].astype(str)
            
            # Gráfico de linhas para evolução
            fig_evolucao = go.Figure()
            
            fig_evolucao.add_trace(go.Scatter(
                x=evolucao_mensal['Mes_Ano_Str'],
                y=evolucao_mensal['Valor_Numerico'],
                mode='lines+markers',
                name='Receita',
                line=dict(color=CORES_PREMIUM['verde_sucesso'], width=3),
                marker=dict(size=8)
            ))
            
            fig_evolucao.add_trace(go.Scatter(
                x=evolucao_mensal['Mes_Ano_Str'],
                y=evolucao_mensal['Custo_Total'],
                mode='lines+markers',
                name='Custos',
                line=dict(color=CORES_PREMIUM['laranja_alerta'], width=3),
                marker=dict(size=8)
            ))
            
            fig_evolucao.add_trace(go.Scatter(
                x=evolucao_mensal['Mes_Ano_Str'],
                y=evolucao_mensal['Lucro Bruto'],
                mode='lines+markers',
                name='Lucro',
                line=dict(color=CORES_PREMIUM['dourado_premium'], width=3),
                marker=dict(size=8)
            ))
            
            fig_evolucao.update_layout(
                title="Evolução Temporal das Métricas",
                font=dict(family="Inter", size=12, color=CORES_PREMIUM['branco_puro']),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Período",
                yaxis_title="Valor (R$)",
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color=CORES_PREMIUM['branco_puro'])
                ),
                xaxis=dict(
                    gridcolor=CORES_PREMIUM['azul_claro'],
                    tickfont=dict(color=CORES_PREMIUM['cinza_claro'])
                ),
                yaxis=dict(
                    gridcolor=CORES_PREMIUM['azul_claro'],
                    tickfont=dict(color=CORES_PREMIUM['cinza_claro'])
                )
            )
            
            st.plotly_chart(fig_evolucao, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para análise temporal.")

else:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo está disponível.")

# Rodapé premium
st.markdown(f"""
<div style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid {CORES_PREMIUM['azul_claro']};">
    <p style="color: {CORES_PREMIUM['cinza_claro']}; font-family: 'Inter', sans-serif; font-size: 0.9rem;">
        <strong>PRIMEIRA LINHA EVENTOS</strong> - Dashboard de Gestão de Pedidos<br>
        Sistema desenvolvido para otimização da gestão empresarial
    </p>
</div>
""", unsafe_allow_html=True)




