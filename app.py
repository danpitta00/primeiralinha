"""
Dashboard Primeira Linha Eventos - Versão 4.0 Dark Theme
Sistema Streamlit com visual profissional escuro + funcionalidades avançadas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from urllib.parse import quote

# Configuração da página
st.set_page_config(
    page_title="Dashboard Primeira Linha Eventos v4.0",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Tema Escuro Profissional
st.markdown("""
<style>
    /* Tema escuro global */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        color: #ffffff;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #1e1b4b 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Cards de métricas com bordas coloridas */
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    
    .metric-card.green {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
    }
    
    .metric-card.blue {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    .metric-card.purple {
        border-left-color: #8b5cf6;
        background: linear-gradient(135deg, #581c87 0%, #6b21a8 100%);
    }
    
    .metric-card.orange {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #92400e 0%, #b45309 100%);
    }
    
    .metric-card.cyan {
        border-left-color: #06b6d4;
        background: linear-gradient(135deg, #0e7490 0%, #0891b2 100%);
    }
    
    /* Alertas com visual aprimorado */
    .alert-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 4px solid #fca5a5;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 4px solid #fbbf24;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3);
    }
    
    .alert-success {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 4px solid #34d399;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
    }
    
    /* Sidebar escura */
    .css-1d391kg {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Tabelas com tema escuro */
    .stDataFrame {
        background: #1f2937;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Métricas com ícones */
    .metric-with-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .metric-icon {
        font-size: 2rem;
        opacity: 0.8;
    }
    
    /* Gráficos com fundo escuro */
    .plotly-graph-div {
        background: transparent !important;
    }
    
    /* Inputs escuros */
    .stSelectbox > div > div {
        background: #374151;
        color: white;
        border: 1px solid #4b5563;
    }
    
    .stTextInput > div > div > input {
        background: #374151;
        color: white;
        border: 1px solid #4b5563;
    }
    
    /* Tabs escuras */
    .stTabs [data-baseweb="tab-list"] {
        background: #1f2937;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #9ca3af;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0 0.25rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
    }
    
    /* Footer escuro */
    .footer {
        background: #111827;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #6b7280;
        margin-top: 2rem;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

def criar_dados_mock():
    """Cria dados mock para demonstração"""
    np.random.seed(42)
    
    # Dados de pedidos
    clientes = ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D', 'Empresa E', 'Empresa F']
    status_list = ['Confirmado', 'Pendente', 'Cancelado', 'Em Andamento', 'Finalizado']
    vendedores = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira']
    categorias = ['Corporativo', 'Casamento', 'Festa', 'Formatura', 'Aniversário']
    
    # Produtos individuais para segmentação
    produtos = [
        'Tenda 6x6m', 'Tenda 10x10m', 'Mesa Redonda', 'Cadeira Tiffany',
        'Som Profissional', 'Iluminação LED', 'Palco 4x3m', 'Gerador 15kva',
        'Toalha Mesa', 'Arranjo Floral', 'Buffet Completo', 'Garçom',
        'Segurança', 'Limpeza', 'Decoração', 'Fotografia'
    ]
    
    data = []
    for i in range(150):
        # Data aleatória nos últimos 12 meses
        data_evento = datetime.now() - timedelta(days=np.random.randint(0, 365))
        
        # Produtos do pedido (1 a 5 produtos por pedido)
        num_produtos = np.random.randint(1, 6)
        produtos_pedido = np.random.choice(produtos, num_produtos, replace=False)
        
        for produto in produtos_pedido:
            valor_produto = np.random.uniform(500, 5000)
            custo_produto = valor_produto * np.random.uniform(0.4, 0.7)
            
            data.append({
                'id': f'PED{i:03d}',
                'cliente': np.random.choice(clientes),
                'data_evento': data_evento.strftime('%Y-%m-%d'),
                'categoria': np.random.choice(categorias),
                'produto': produto,
                'quantidade': np.random.randint(1, 10),
                'valor_unitario': valor_produto,
                'valor_total': valor_produto * np.random.randint(1, 10),
                'custo_total': custo_produto * np.random.randint(1, 10),
                'vendedor': np.random.choice(vendedores),
                'status': np.random.choice(status_list),
                'observacoes': f'Observações do produto {produto}'
            })
    
    return pd.DataFrame(data)

def calcular_kpis(df):
    """Calcula KPIs principais"""
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Filtrar dados do mês atual
    df['data_evento'] = pd.to_datetime(df['data_evento'])
    df_mes_atual = df[(df['data_evento'].dt.month == mes_atual) & 
                      (df['data_evento'].dt.year == ano_atual)]
    
    # KPIs básicos
    receita_total = df_mes_atual['valor_total'].sum()
    custo_total = df_mes_atual['custo_total'].sum()
    lucro_total = receita_total - custo_total
    margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
    
    # Pedidos
    total_pedidos = df_mes_atual['id'].nunique()
    pedidos_confirmados = df_mes_atual[df_mes_atual['status'] == 'Confirmado']['id'].nunique()
    pedidos_pendentes = df_mes_atual[df_mes_atual['status'] == 'Pendente']['id'].nunique()
    pedidos_cancelados = df_mes_atual[df_mes_atual['status'] == 'Cancelado']['id'].nunique()
    
    # Taxas
    taxa_conversao = (pedidos_confirmados / total_pedidos * 100) if total_pedidos > 0 else 0
    taxa_cancelamento = (pedidos_cancelados / total_pedidos * 100) if total_pedidos > 0 else 0
    
    # Ticket médio
    ticket_medio = receita_total / total_pedidos if total_pedidos > 0 else 0
    
    # Comparação com mês anterior
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    
    df_mes_anterior = df[(df['data_evento'].dt.month == mes_anterior) & 
                         (df['data_evento'].dt.year == ano_anterior)]
    receita_mes_anterior = df_mes_anterior['valor_total'].sum()
    crescimento_receita = ((receita_total - receita_mes_anterior) / receita_mes_anterior * 100) if receita_mes_anterior > 0 else 0
    
    return {
        'receita_total': receita_total,
        'custo_total': custo_total,
        'lucro_total': lucro_total,
        'margem_lucro': margem_lucro,
        'total_pedidos': total_pedidos,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_cancelados': pedidos_cancelados,
        'taxa_conversao': taxa_conversao,
        'taxa_cancelamento': taxa_cancelamento,
        'ticket_medio': ticket_medio,
        'crescimento_receita': crescimento_receita
    }

def criar_grafico_receita_mensal(df):
    """Cria gráfico de receita mensal"""
    df['data_evento'] = pd.to_datetime(df['data_evento'])
    df['mes_ano'] = df['data_evento'].dt.to_period('M')
    
    receita_mensal = df.groupby('mes_ano')['valor_total'].sum().reset_index()
    receita_mensal['mes_ano_str'] = receita_mensal['mes_ano'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=receita_mensal['mes_ano_str'],
        y=receita_mensal['valor_total'],
        name='Receita Mensal',
        marker_color='#3b82f6',
        text=receita_mensal['valor_total'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Evolução da Receita Mensal',
        xaxis_title='Mês',
        yaxis_title='Receita (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=16,
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def criar_grafico_lucro_mensal(df):
    """Cria gráfico de lucro mensal"""
    df['data_evento'] = pd.to_datetime(df['data_evento'])
    df['mes_ano'] = df['data_evento'].dt.to_period('M')
    
    dados_mensais = df.groupby('mes_ano').agg({
        'valor_total': 'sum',
        'custo_total': 'sum'
    }).reset_index()
    
    dados_mensais['lucro'] = dados_mensais['valor_total'] - dados_mensais['custo_total']
    dados_mensais['mes_ano_str'] = dados_mensais['mes_ano'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dados_mensais['mes_ano_str'],
        y=dados_mensais['lucro'],
        name='Lucro Mensal',
        marker_color='#10b981',
        text=dados_mensais['lucro'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Evolução do Lucro Mensal',
        xaxis_title='Mês',
        yaxis_title='Lucro (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=16,
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🎪 Dashboard Primeira Linha Eventos</h1>
        <h3>Versão 4.0 - Tema Profissional Escuro</h3>
        <p>Gestão Completa de Eventos e Equipamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controles")
        
        # Botão Novo Pedido
        if st.button("➕ Novo Pedido", use_container_width=True):
            st.success("Funcionalidade de novo pedido será implementada!")
        
        st.markdown("---")
        
        # Filtros
        st.markdown("### 📊 Filtros")
        periodo = st.selectbox("Período", ["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"])
        categoria = st.selectbox("Categoria", ["Todas", "Corporativo", "Casamento", "Festa", "Formatura"])
        vendedor = st.selectbox("Vendedor", ["Todos", "João Silva", "Maria Santos", "Pedro Costa", "Ana Oliveira"])
    
    # Carregar dados
    df = criar_dados_mock()
    kpis = calcular_kpis(df)
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Evolução", "📋 Pedidos", "⚠️ Alertas"])
    
    with tab1:
        # KPIs principais em cards coloridos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card blue">
                <div class="metric-with-icon">
                    <span class="metric-icon">💰</span>
                    <div>
                        <h3>R$ {kpis['receita_total']:,.0f}</h3>
                        <p>Receita Total</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card green">
                <div class="metric-with-icon">
                    <span class="metric-icon">📈</span>
                    <div>
                        <h3>R$ {kpis['lucro_total']:,.0f}</h3>
                        <p>Lucro Total</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card purple">
                <div class="metric-with-icon">
                    <span class="metric-icon">📊</span>
                    <div>
                        <h3>{kpis['margem_lucro']:.1f}%</h3>
                        <p>Margem de Lucro</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card orange">
                <div class="metric-with-icon">
                    <span class="metric-icon">🎯</span>
                    <div>
                        <h3>{kpis['total_pedidos']}</h3>
                        <p>Total de Pedidos</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Segunda linha de KPIs
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card cyan">
                <div class="metric-with-icon">
                    <span class="metric-icon">✅</span>
                    <div>
                        <h3>{kpis['taxa_conversao']:.1f}%</h3>
                        <p>Taxa de Conversão</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-with-icon">
                    <span class="metric-icon">🎫</span>
                    <div>
                        <h3>R$ {kpis['ticket_medio']:,.0f}</h3>
                        <p>Ticket Médio</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col7:
            cor_crescimento = "green" if kpis['crescimento_receita'] >= 0 else ""
            st.markdown(f"""
            <div class="metric-card {cor_crescimento}">
                <div class="metric-with-icon">
                    <span class="metric-icon">📊</span>
                    <div>
                        <h3>{kpis['crescimento_receita']:+.1f}%</h3>
                        <p>Crescimento</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col8:
            st.markdown(f"""
            <div class="metric-card purple">
                <div class="metric-with-icon">
                    <span class="metric-icon">⏳</span>
                    <div>
                        <h3>{kpis['pedidos_pendentes']}</h3>
                        <p>Pendentes</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gráficos temporais (NOVOS)
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            fig_receita = criar_grafico_receita_mensal(df)
            st.plotly_chart(fig_receita, use_container_width=True)
        
        with col_graf2:
            fig_lucro = criar_grafico_lucro_mensal(df)
            st.plotly_chart(fig_lucro, use_container_width=True)
        
        # Gráficos existentes
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            # Top 5 Produtos (segmentados)
            top_produtos = df.groupby('produto')['valor_total'].sum().sort_values(ascending=False).head(5)
            
            fig_produtos = px.bar(
                x=top_produtos.values,
                y=top_produtos.index,
                orientation='h',
                title='Top 5 Produtos Mais Vendidos',
                color=top_produtos.values,
                color_continuous_scale='viridis'
            )
            fig_produtos.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_produtos, use_container_width=True)
        
        with col_graf4:
            # Distribuição por categoria
            dist_categoria = df.groupby('categoria')['valor_total'].sum()
            
            fig_categoria = px.pie(
                values=dist_categoria.values,
                names=dist_categoria.index,
                title='Receita por Categoria',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_categoria.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Evolução Temporal")
        
        # Gráfico de evolução mensal completo
        df['data_evento'] = pd.to_datetime(df['data_evento'])
        df['mes_ano'] = df['data_evento'].dt.to_period('M')
        
        evolucao = df.groupby('mes_ano').agg({
            'valor_total': 'sum',
            'custo_total': 'sum',
            'id': 'nunique'
        }).reset_index()
        
        evolucao['lucro'] = evolucao['valor_total'] - evolucao['custo_total']
        evolucao['mes_ano_str'] = evolucao['mes_ano'].astype(str)
        
        fig_evolucao = go.Figure()
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao['mes_ano_str'],
            y=evolucao['valor_total'],
            mode='lines+markers',
            name='Receita',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao['mes_ano_str'],
            y=evolucao['custo_total'],
            mode='lines+markers',
            name='Custos',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao['mes_ano_str'],
            y=evolucao['lucro'],
            mode='lines+markers',
            name='Lucro',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.update_layout(
            title='Evolução Financeira Mensal',
            xaxis_title='Período',
            yaxis_title='Valor (R$)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(
                bgcolor='rgba(31, 41, 55, 0.8)',
                bordercolor='rgba(255, 255, 255, 0.2)',
                borderwidth=1
            )
        )
        
        fig_evolucao.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig_evolucao.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Análise de tendências
        st.markdown("### 📊 Análise de Tendências")
        
        col_tend1, col_tend2, col_tend3 = st.columns(3)
        
        with col_tend1:
            crescimento_medio = evolucao['valor_total'].pct_change().mean() * 100
            st.markdown(f"""
            <div class="metric-card {'green' if crescimento_medio > 0 else ''}">
                <h4>Crescimento Médio Mensal</h4>
                <h2>{crescimento_medio:+.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_tend2:
            melhor_mes = evolucao.loc[evolucao['valor_total'].idxmax(), 'mes_ano_str']
            melhor_receita = evolucao['valor_total'].max()
            st.markdown(f"""
            <div class="metric-card blue">
                <h4>Melhor Mês</h4>
                <h3>{melhor_mes}</h3>
                <p>R$ {melhor_receita:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_tend3:
            margem_media = (evolucao['lucro'] / evolucao['valor_total'] * 100).mean()
            st.markdown(f"""
            <div class="metric-card purple">
                <h4>Margem Média</h4>
                <h2>{margem_media:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📋 Gestão de Pedidos")
        
        # Filtros para pedidos
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            status_filtro = st.selectbox("Status", ["Todos"] + df['status'].unique().tolist())
        
        with col_filtro2:
            cliente_filtro = st.selectbox("Cliente", ["Todos"] + df['cliente'].unique().tolist())
        
        with col_filtro3:
            if st.button("🔄 Atualizar Dados"):
                st.rerun()
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status_filtro]
        if cliente_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['cliente'] == cliente_filtro]
        
        # Tabela de pedidos com produtos segmentados
        st.markdown("#### 📊 Lista de Pedidos por Produto")
        
        # Preparar dados para exibição
        df_display = df_filtrado[['id', 'cliente', 'data_evento', 'categoria', 'produto', 
                                 'quantidade', 'valor_unitario', 'valor_total', 'status', 'vendedor']].copy()
        
        df_display['data_evento'] = pd.to_datetime(df_display['data_evento']).dt.strftime('%d/%m/%Y')
        df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f'R$ {x:,.2f}')
        df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Renomear colunas
        df_display.columns = ['ID', 'Cliente', 'Data Evento', 'Categoria', 'Produto', 
                             'Qtd', 'Valor Unit.', 'Valor Total', 'Status', 'Vendedor']
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Resumo dos pedidos filtrados
        st.markdown("#### 📈 Resumo dos Pedidos Filtrados")
        
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        
        with col_res1:
            total_itens = len(df_filtrado)
            st.markdown(f"""
            <div class="metric-card blue">
                <h4>Total de Itens</h4>
                <h2>{total_itens}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res2:
            valor_total_filtrado = df_filtrado['valor_total'].sum()
            st.markdown(f"""
            <div class="metric-card green">
                <h4>Valor Total</h4>
                <h2>R$ {valor_total_filtrado:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res3:
            pedidos_unicos = df_filtrado['id'].nunique()
            st.markdown(f"""
            <div class="metric-card purple">
                <h4>Pedidos Únicos</h4>
                <h2>{pedidos_unicos}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res4:
            ticket_medio_filtrado = valor_total_filtrado / pedidos_unicos if pedidos_unicos > 0 else 0
            st.markdown(f"""
            <div class="metric-card orange">
                <h4>Ticket Médio</h4>
                <h2>R$ {ticket_medio_filtrado:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### ⚠️ Sistema de Alertas")
        
        # Alertas críticos
        if kpis['taxa_cancelamento'] > 20:
            st.markdown(f"""
            <div class="alert-critical">
                <h4>🚨 ALERTA CRÍTICO: Taxa de Cancelamento Alta</h4>
                <p>Taxa atual: {kpis['taxa_cancelamento']:.1f}% (Limite: 20%)</p>
                <p><strong>Ação recomendada:</strong> Revisar processo de confirmação de pedidos</p>
            </div>
            """, unsafe_allow_html=True)
        
        if kpis['margem_lucro'] < 15:
            st.markdown(f"""
            <div class="alert-critical">
                <h4>🚨 ALERTA CRÍTICO: Margem de Lucro Baixa</h4>
                <p>Margem atual: {kpis['margem_lucro']:.1f}% (Mínimo: 15%)</p>
                <p><strong>Ação recomendada:</strong> Revisar precificação e custos</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Alertas de atenção
        if kpis['pedidos_pendentes'] > 10:
            st.markdown(f"""
            <div class="alert-warning">
                <h4>⚠️ ATENÇÃO: Muitos Pedidos Pendentes</h4>
                <p>Pedidos pendentes: {kpis['pedidos_pendentes']} (Limite: 10)</p>
                <p><strong>Ação recomendada:</strong> Acelerar processo de confirmação</p>
            </div>
            """, unsafe_allow_html=True)
        
        if kpis['crescimento_receita'] < -10:
            st.markdown(f"""
            <div class="alert-warning">
                <h4>⚠️ ATENÇÃO: Queda na Receita</h4>
                <p>Variação: {kpis['crescimento_receita']:.1f}% vs mês anterior</p>
                <p><strong>Ação recomendada:</strong> Intensificar ações comerciais</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Alertas positivos
        if kpis['taxa_conversao'] > 80:
            st.markdown(f"""
            <div class="alert-success">
                <h4>✅ EXCELENTE: Alta Taxa de Conversão</h4>
                <p>Taxa atual: {kpis['taxa_conversao']:.1f}%</p>
                <p><strong>Parabéns!</strong> Equipe comercial está performando muito bem!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if kpis['crescimento_receita'] > 20:
            st.markdown(f"""
            <div class="alert-success">
                <h4>✅ EXCELENTE: Forte Crescimento</h4>
                <p>Crescimento: {kpis['crescimento_receita']:.1f}% vs mês anterior</p>
                <p><strong>Parabéns!</strong> Empresa em forte expansão!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Resumo de alertas
        st.markdown("### 📊 Resumo de Alertas")
        
        alertas_criticos = 0
        alertas_atencao = 0
        alertas_positivos = 0
        
        if kpis['taxa_cancelamento'] > 20: alertas_criticos += 1
        if kpis['margem_lucro'] < 15: alertas_criticos += 1
        if kpis['pedidos_pendentes'] > 10: alertas_atencao += 1
        if kpis['crescimento_receita'] < -10: alertas_atencao += 1
        if kpis['taxa_conversao'] > 80: alertas_positivos += 1
        if kpis['crescimento_receita'] > 20: alertas_positivos += 1
        
        col_alert1, col_alert2, col_alert3 = st.columns(3)
        
        with col_alert1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🚨 Críticos</h4>
                <h2>{alertas_criticos}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_alert2:
            st.markdown(f"""
            <div class="metric-card orange">
                <h4>⚠️ Atenção</h4>
                <h2>{alertas_atencao}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_alert3:
            st.markdown(f"""
            <div class="metric-card green">
                <h4>✅ Positivos</h4>
                <h2>{alertas_positivos}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        Dashboard Primeira Linha Eventos v4.0 | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df)} itens carregados | 
        Tema Escuro Profissional
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

