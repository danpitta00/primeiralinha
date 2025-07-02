import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard Primeira Linha Eventos",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de cores baseada na identidade visual da Primeira Linha Eventos
CORES_PRIMEIRA_LINHA = {
    'azul_escuro': '#2B3A67',      # Azul escuro do logo
    'dourado': '#D4AF37',          # Dourado do logo
    'azul_claro': '#4A6FA5',       # Azul mais claro para variações
    'laranja': '#FF6B35',          # Laranja para destaques (inspirado na referência)
    'verde': '#28A745',            # Verde para valores positivos
    'vermelho': '#DC3545',         # Vermelho para alertas
    'cinza_claro': '#F8F9FA',      # Fundo claro
    'cinza_escuro': '#6C757D',     # Texto secundário
    'branco': '#FFFFFF'
}

# CSS customizado para aplicar a identidade visual
st.markdown(f"""
<style>
    /* Importar fonte similar à usada no logo */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Aplicar fonte personalizada */
    html, body, [class*="st-"] {{
        font-family: 'Roboto', sans-serif;
    }}
    
    /* Estilizar o cabeçalho principal */
    .header-container {{
        background: linear-gradient(135deg, {CORES_PRIMEIRA_LINHA['azul_escuro']} 0%, {CORES_PRIMEIRA_LINHA['azul_claro']} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    .header-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .header-subtitle {{
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }}
    
    /* Estilizar métricas principais */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid {CORES_PRIMEIRA_LINHA['dourado']};
        margin-bottom: 1rem;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {CORES_PRIMEIRA_LINHA['azul_escuro']};
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {CORES_PRIMEIRA_LINHA['cinza_escuro']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }}
    
    /* Estilizar seções de gráficos */
    .chart-section {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }}
    
    .chart-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: {CORES_PRIMEIRA_LINHA['azul_escuro']};
        margin-bottom: 1rem;
        text-align: center;
    }}
    
    /* Estilizar velocímetros */
    .velocimetro-container {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
    }}
    
    .velocimetro-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {CORES_PRIMEIRA_LINHA['azul_escuro']};
        margin-bottom: 0.5rem;
    }}
    
    .velocimetro-value {{
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .velocimetro-subtitle {{
        font-size: 0.8rem;
        color: {CORES_PRIMEIRA_LINHA['cinza_escuro']};
    }}
</style>
""", unsafe_allow_html=True)

# Função para carregar e limpar dados
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

# Função para criar velocímetro
def criar_velocimetro(valor, titulo, subtitulo=""):
    """Cria um gráfico de velocímetro para indicar porcentagem de conclusão"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': titulo, 'font': {'size': 14}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': CORES_PRIMEIRA_LINHA['azul_escuro']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': CORES_PRIMEIRA_LINHA['vermelho']},
                {'range': [50, 80], 'color': CORES_PRIMEIRA_LINHA['dourado']},
                {'range': [80, 100], 'color': CORES_PRIMEIRA_LINHA['verde']}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        font={'color': CORES_PRIMEIRA_LINHA['azul_escuro'], 'family': "Roboto"},
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# Cabeçalho com identidade visual
st.markdown(f"""
<div class="header-container">
    <div class="header-title">
        📊 PRIMEIRA LINHA EVENTOS
    </div>
    <div class="header-subtitle">
        Dashboard de Gestão de Pedidos e Performance
    </div>
</div>
""", unsafe_allow_html=True)

# Carregar dados
df = load_and_clean_data('Planilhasemtítulo-Página1.csv')

if not df.empty:
    # Sidebar com filtros
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
    
    # Criar abas
    tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Evolução Temporal"])
    
    with tab1:
        # PRIMEIRA PARTE: MÉTRICAS E GRÁFICOS (baseados na referência)
        st.markdown("## 📈 Métricas Operacionais")
        
        # Calcular métricas principais
        df_com_valores = df_filtrado[~df_filtrado['Valor_Pendente']]
        
        receita_total = df_com_valores["Valor_Numerico"].sum()
        custo_total = df_com_valores["Custo_Total"].sum()
        lucro_total = df_com_valores["Lucro Bruto"].sum()
        margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
        margem_contribuicao = ((receita_total - custo_total) / receita_total * 100) if receita_total > 0 else 0
        
        # Métricas no topo (inspiradas na referência)
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['laranja']};">R$ {custo_total:,.0f}</div>
                <div class="metric-label">Despesa</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['azul_escuro']};">R$ {receita_total:,.0f}</div>
                <div class="metric-label">Receita</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['verde']};">{margem_lucro:.1f}%</div>
                <div class="metric-label">% Lucro</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            custo_operacional = df_com_valores["Custo_Numerico"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['cinza_escuro']};">R$ {custo_operacional:,.0f}</div>
                <div class="metric-label">Custo</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['azul_claro']};">{margem_contribuicao:.1f}%</div>
                <div class="metric-label">% M. Contrib.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            meta_categoria = receita_total / len(df_com_valores["Categoria"].unique()) if len(df_com_valores["Categoria"].unique()) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {CORES_PRIMEIRA_LINHA['verde']};">R$ {meta_categoria:,.0f}</div>
                <div class="metric-label">Meta Por Categoria</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos principais (inspirados na referência)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🔥 Despesa Operacional Mensal</div>', unsafe_allow_html=True)
            
            # Gráfico de despesas mensais
            df_temporal = df_com_valores.copy()
            df_temporal['Mes_Ano'] = df_temporal['Data do Pedido'].dt.to_period('M')
            despesa_mensal = df_temporal.groupby('Mes_Ano')['Custo_Total'].sum().reset_index()
            despesa_mensal['Mes_Ano_Str'] = despesa_mensal['Mes_Ano'].astype(str)
            
            fig_despesa = px.bar(
                despesa_mensal, 
                x='Mes_Ano_Str', 
                y='Custo_Total',
                color_discrete_sequence=[CORES_PRIMEIRA_LINHA['laranja']]
            )
            fig_despesa.update_layout(
                font=dict(family="Roboto", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Despesa (R$)",
                showlegend=False
            )
            st.plotly_chart(fig_despesa, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 Receita Operacional Mensal</div>', unsafe_allow_html=True)
            
            # Gráfico de receita mensal
            receita_mensal = df_temporal.groupby('Mes_Ano')['Valor_Numerico'].sum().reset_index()
            receita_mensal['Mes_Ano_Str'] = receita_mensal['Mes_Ano'].astype(str)
            
            fig_receita = px.bar(
                receita_mensal, 
                x='Mes_Ano_Str', 
                y='Valor_Numerico',
                color_discrete_sequence=[CORES_PRIMEIRA_LINHA['azul_escuro']]
            )
            fig_receita.update_layout(
                font=dict(family="Roboto", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="",
                yaxis_title="Receita (R$)",
                showlegend=False
            )
            st.plotly_chart(fig_receita, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Segunda linha de gráficos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">⚖️ Margem Por Cliente</div>', unsafe_allow_html=True)
            
            # Top 5 clientes por margem
            margem_cliente = df_com_valores.groupby("Cliente/Projeto").agg({
                "Valor_Numerico": "sum",
                "Lucro Bruto": "sum"
            }).reset_index()
            margem_cliente['Margem'] = (margem_cliente['Lucro Bruto'] / margem_cliente['Valor_Numerico'] * 100).round(1)
            margem_cliente = margem_cliente.sort_values('Margem', ascending=True).tail(5)
            
            fig_margem = px.bar(
                margem_cliente, 
                x="Margem", 
                y="Cliente/Projeto",
                orientation="h",
                color_discrete_sequence=[CORES_PRIMEIRA_LINHA['azul_escuro']]
            )
            fig_margem.update_layout(
                font=dict(family="Roboto", size=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Margem (%)",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig_margem, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📊 Análise Por Categoria</div>', unsafe_allow_html=True)
            
            # Tabela de análise por categoria
            analise_categoria = df_com_valores.groupby("Categoria").agg({
                "Valor_Numerico": "sum",
                "Lucro Bruto": "sum",
                "ID do Pedido": "count"
            }).reset_index()
            analise_categoria.columns = ["Categoria", "Receita", "Margem Bruta", "Qtd Pedidos"]
            analise_categoria['% M. Contrib'] = (analise_categoria['Margem Bruta'] / analise_categoria['Receita'] * 100).round(1)
            
            st.dataframe(
                analise_categoria[["Categoria", "Receita", "Margem Bruta", "% M. Contrib"]],
                use_container_width=True,
                height=200
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">🎯 Receita Por Tipo de Serviço</div>', unsafe_allow_html=True)
            
            # Gráfico de rosca por categoria
            receita_categoria = df_com_valores.groupby("Categoria")["Valor_Numerico"].sum().reset_index()
            
            fig_rosca = px.pie(
                receita_categoria, 
                values="Valor_Numerico", 
                names="Categoria",
                color_discrete_sequence=[CORES_PRIMEIRA_LINHA['azul_escuro'], 
                                       CORES_PRIMEIRA_LINHA['dourado'], 
                                       CORES_PRIMEIRA_LINHA['azul_claro']],
                hole=0.4
            )
            fig_rosca.update_layout(
                font=dict(family="Roboto", size=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True
            )
            st.plotly_chart(fig_rosca, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # SEGUNDA PARTE: VELOCÍMETROS DE CONCLUSÃO
        st.markdown("## 🎯 Indicadores de Preenchimento")
        
        # Calcular porcentagens de preenchimento
        total_pedidos = len(df_filtrado)
        
        perc_ids = ((total_pedidos - df_filtrado['ID do Pedido'].isna().sum()) / total_pedidos * 100) if total_pedidos > 0 else 0
        perc_valores = ((total_pedidos - df_filtrado['Valor_Pendente'].sum()) / total_pedidos * 100) if total_pedidos > 0 else 0
        perc_custos = ((total_pedidos - df_filtrado['Custo_Pendente'].sum()) / total_pedidos * 100) if total_pedidos > 0 else 0
        perc_diarias = ((total_pedidos - df_filtrado['Diarias_Pendente'].sum()) / total_pedidos * 100) if total_pedidos > 0 else 0
        perc_pagamentos = ((total_pedidos - df_filtrado['Data Pagamento_Pendente'].sum()) / total_pedidos * 100) if total_pedidos > 0 else 0
        
        # Exibir velocímetros
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            fig_vel1 = criar_velocimetro(perc_ids, "IDs dos Pedidos")
            st.plotly_chart(fig_vel1, use_container_width=True)
            st.markdown(f"""
            <div class="velocimetro-container">
                <div class="velocimetro-subtitle">{df_filtrado['ID do Pedido'].isna().sum()} pendentes de {total_pedidos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            fig_vel2 = criar_velocimetro(perc_valores, "Valores Definidos")
            st.plotly_chart(fig_vel2, use_container_width=True)
            st.markdown(f"""
            <div class="velocimetro-container">
                <div class="velocimetro-subtitle">{df_filtrado['Valor_Pendente'].sum()} pendentes de {total_pedidos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            fig_vel3 = criar_velocimetro(perc_custos, "Custos Informados")
            st.plotly_chart(fig_vel3, use_container_width=True)
            st.markdown(f"""
            <div class="velocimetro-container">
                <div class="velocimetro-subtitle">{df_filtrado['Custo_Pendente'].sum()} pendentes de {total_pedidos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            fig_vel4 = criar_velocimetro(perc_diarias, "Diárias Registradas")
            st.plotly_chart(fig_vel4, use_container_width=True)
            st.markdown(f"""
            <div class="velocimetro-container">
                <div class="velocimetro-subtitle">{df_filtrado['Diarias_Pendente'].sum()} pendentes de {total_pedidos}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            fig_vel5 = criar_velocimetro(perc_pagamentos, "Datas de Pagamento")
            st.plotly_chart(fig_vel5, use_container_width=True)
            st.markdown(f"""
            <div class="velocimetro-container">
                <div class="velocimetro-subtitle">{df_filtrado['Data Pagamento_Pendente'].sum()} pendentes de {total_pedidos}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # ABA DE EVOLUÇÃO TEMPORAL
        st.markdown("## 📈 Evolução Temporal dos Pedidos")
        
        # Preparar dados temporais
        df_temporal_completo = df_com_valores.copy()
        df_temporal_completo['Ano'] = df_temporal_completo['Data do Pedido'].dt.year
        df_temporal_completo['Mes'] = df_temporal_completo['Data do Pedido'].dt.month
        df_temporal_completo['Mes_Ano'] = df_temporal_completo['Data do Pedido'].dt.to_period('M')
        
        # Filtros específicos para a aba temporal
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            anos_disponiveis = sorted(df_temporal_completo['Ano'].unique())
            ano_selecionado = st.selectbox("📅 Selecionar Ano", ["Todos"] + anos_disponiveis)
        
        with col_filtro2:
            metrica_temporal = st.selectbox("📊 Métrica para Análise", 
                                          ["Receita", "Lucro Bruto", "Número de Pedidos", "Custo Total"])
        
        # Aplicar filtro de ano
        if ano_selecionado != "Todos":
            df_temporal_filtrado = df_temporal_completo[df_temporal_completo['Ano'] == ano_selecionado]
        else:
            df_temporal_filtrado = df_temporal_completo
        
        # Gráfico principal de evolução
        if metrica_temporal == "Receita":
            dados_temporais = df_temporal_filtrado.groupby('Mes_Ano')['Valor_Numerico'].sum().reset_index()
            coluna_y = 'Valor_Numerico'
            titulo_y = "Receita (R$)"
        elif metrica_temporal == "Lucro Bruto":
            dados_temporais = df_temporal_filtrado.groupby('Mes_Ano')['Lucro Bruto'].sum().reset_index()
            coluna_y = 'Lucro Bruto'
            titulo_y = "Lucro Bruto (R$)"
        elif metrica_temporal == "Número de Pedidos":
            dados_temporais = df_temporal_filtrado.groupby('Mes_Ano').size().reset_index(name='Quantidade')
            coluna_y = 'Quantidade'
            titulo_y = "Número de Pedidos"
        else:  # Custo Total
            dados_temporais = df_temporal_filtrado.groupby('Mes_Ano')['Custo_Total'].sum().reset_index()
            coluna_y = 'Custo_Total'
            titulo_y = "Custo Total (R$)"
        
        dados_temporais['Mes_Ano_Str'] = dados_temporais['Mes_Ano'].astype(str)
        
        # Gráfico de linha para evolução temporal
        fig_evolucao = px.line(
            dados_temporais, 
            x='Mes_Ano_Str', 
            y=coluna_y,
            title=f"Evolução de {metrica_temporal} ao Longo do Tempo",
            color_discrete_sequence=[CORES_PRIMEIRA_LINHA['azul_escuro']]
        )
        fig_evolucao.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_evolucao.update_layout(
            font=dict(family="Roboto", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Período",
            yaxis_title=titulo_y,
            title_x=0.5
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Análises complementares
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribuição por Ano")
            dados_anuais = df_temporal_completo.groupby('Ano').agg({
                'Valor_Numerico': 'sum',
                'Lucro Bruto': 'sum',
                'ID do Pedido': 'count'
            }).reset_index()
            dados_anuais.columns = ['Ano', 'Receita Total', 'Lucro Total', 'Qtd Pedidos']
            
            st.dataframe(dados_anuais, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Sazonalidade por Mês")
            sazonalidade = df_temporal_completo.groupby('Mes')['Valor_Numerico'].mean().reset_index()
            sazonalidade['Mes_Nome'] = sazonalidade['Mes'].map({
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            })
            
            fig_sazonalidade = px.bar(
                sazonalidade, 
                x='Mes_Nome', 
                y='Valor_Numerico',
                color_discrete_sequence=[CORES_PRIMEIRA_LINHA['dourado']]
            )
            fig_sazonalidade.update_layout(
                font=dict(family="Roboto", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Mês",
                yaxis_title="Receita Média (R$)",
                showlegend=False
            )
            st.plotly_chart(fig_sazonalidade, use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo está disponível.")

# Rodapé com identidade visual
st.markdown(f"""
<div style="margin-top: 3rem; padding: 2rem; background: {CORES_PRIMEIRA_LINHA['cinza_claro']}; border-radius: 10px; text-align: center;">
    <strong>PRIMEIRA LINHA EVENTOS</strong> - Dashboard de Gestão de Pedidos<br>
    <small style="color: {CORES_PRIMEIRA_LINHA['cinza_escuro']};">Sistema desenvolvido para otimização da gestão empresarial</small>
</div>
""", unsafe_allow_html=True)


