"""
Dashboard Primeira Linha Eventos - Versão 4.0 Corrigida
Sistema Streamlit com estrutura real da planilha + segmentação de produtos
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
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
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

def extrair_produtos_individuais(descricao_completa):
    """Extrai produtos individuais da descrição completa do pedido"""
    produtos_conhecidos = {
        'stand': 'Stand Octanorme',
        'banqueta': 'Banqueta',
        'púlpito': 'Púlpito',
        'palco': 'Palco Tablado',
        'brinquedo inflável': 'Brinquedo Inflável',
        'cama elástica': 'Cama Elástica',
        'carrinho de pipoca': 'Carrinho de Pipoca',
        'carrinho de algodão doce': 'Carrinho de Algodão Doce',
        'monitor': 'Monitor/TV',
        'bebedouro': 'Bebedouro',
        'suporte para tv': 'Suporte para TV',
        'plotagem': 'Plotagem/Impressão',
        'som': 'Som Profissional',
        'iluminação': 'Iluminação',
        'tenda': 'Tenda',
        'mesa': 'Mesa',
        'cadeira': 'Cadeira',
        'toalha': 'Toalha de Mesa',
        'decoração': 'Decoração',
        'segurança': 'Segurança',
        'garçom': 'Garçom',
        'buffet': 'Buffet',
        'gerador': 'Gerador'
    }
    
    produtos_encontrados = []
    descricao_lower = descricao_completa.lower()
    
    for palavra_chave, produto_normalizado in produtos_conhecidos.items():
        if palavra_chave in descricao_lower:
            produtos_encontrados.append(produto_normalizado)
    
    if not produtos_encontrados:
        produtos_encontrados = [descricao_completa[:50] + "..." if len(descricao_completa) > 50 else descricao_completa]
    
    return produtos_encontrados

def criar_dados_reais_estrutura():
    """Cria dados baseados na estrutura REAL da planilha"""
    np.random.seed(42)
    
    clientes_reais = [
        'Caixa Econômica Federal', 'Sec. da Mulher', 'Programa "Sempre por Elas"',
        'Prefeitura de Brasília', 'Banco do Brasil', 'Correios',
        'Ministério da Saúde', 'UnB - Universidade de Brasília', 'GDF - Governo do DF',
        'Empresa Privada A', 'Empresa Privada B', 'Festa Particular'
    ]
    
    categorias_reais = ['Particular', 'Público Extra', 'Corporativo']
    
    locais_reais = [
        'Hotel Ramada', 'Torre de TV', 'Curralinho', 'Esplanada dos Ministérios',
        'Parque da Cidade', 'Centro de Convenções', 'Clube do Congresso',
        'Shopping Brasília', 'Setor Bancário Sul', 'Asa Norte', 'Asa Sul',
        'Taguatinga', 'Ceilândia', 'Sobradinho'
    ]
    
    produtos_servicos_reais = [
        'Stand octanorme plotado + 2 banquetas, púlpito, palco tablado 6x3, brinquedos infláveis, cama elástica, carrinho de pipoca, carrinho de algodão doce, monitores',
        'Cama elástica, carrinho de pipoca, carrinho de algodão doce, monitores, infláveis, bebedouros',
        'Infláveis, bebedouros, cama elástica, carrinho de pipoca, carrinho de algodão doce, suportes para TV',
        'Tenda 10x10m, mesas redondas, cadeiras, som profissional, iluminação',
        'Palco 6x4m, sistema de som, iluminação cênica, camarim',
        'Buffet completo, garçons, decoração, arranjos florais',
        'Stand promocional, plotagem, banners, material gráfico',
        'Brinquedos infláveis, monitores, segurança, limpeza',
        'Som profissional, DJ, iluminação, efeitos especiais',
        'Tenda cristal, decoração premium, mobiliário de luxo',
        'Equipamentos audiovisuais, projetor, telão, microfones',
        'Gerador 15kva, extensões, quadro de força'
    ]
    
    data = []
    for i in range(100):
        data_entrega = datetime.now() - timedelta(days=np.random.randint(0, 365))
        data_recolhimento = data_entrega + timedelta(days=np.random.randint(1, 5))
        data_pagamento = data_entrega + timedelta(days=np.random.randint(-5, 30))
        
        valor_base = np.random.choice([1850, 4560, 9080, 2500, 3200, 5800, 7200, 1200, 6500, 4800])
        valor_com_variacao = valor_base * np.random.uniform(0.8, 1.5)
        custos = valor_com_variacao * np.random.uniform(0.2, 0.4)
        
        descricao_produto = np.random.choice(produtos_servicos_reais)
        produtos_individuais = extrair_produtos_individuais(descricao_produto)
        
        for produto_individual in produtos_individuais:
            valor_produto = valor_com_variacao / len(produtos_individuais)
            custo_produto = custos / len(produtos_individuais)
            
            data.append({
                'numero_pedido': f'PED{i+1:03d}',
                'cliente_projeto': np.random.choice(clientes_reais),
                'categoria': np.random.choice(categorias_reais),
                'produto_servico_completo': descricao_produto,
                'produto_individual': produto_individual,
                'valor': valor_produto,
                'custos_pedido': custo_produto,
                'diaria_equipe': np.random.randint(1, 8),
                'local': np.random.choice(locais_reais),
                'data_entrega': data_entrega.strftime('%d/%m/%Y'),
                'data_recolhimento': data_recolhimento.strftime('%d/%m/%Y'),
                'data_pagamento': data_pagamento.strftime('%d/%m/%Y') if np.random.random() > 0.1 else 'Pendente',
                'status': np.random.choice(['Confirmado', 'Pendente', 'Finalizado', 'Em Andamento'])
            })
    
    return pd.DataFrame(data)

def calcular_kpis_reais(df):
    """Calcula KPIs baseados na estrutura real"""
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
    df_mes_atual = df[(df['data_entrega_dt'].dt.month == mes_atual) & 
                      (df['data_entrega_dt'].dt.year == ano_atual)]
    
    receita_total = df_mes_atual['valor'].sum()
    custo_total = df_mes_atual['custos_pedido'].sum()
    lucro_total = receita_total - custo_total
    margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
    
    total_pedidos = df_mes_atual['numero_pedido'].nunique()
    pedidos_confirmados = df_mes_atual[df_mes_atual['status'] == 'Confirmado']['numero_pedido'].nunique()
    pedidos_pendentes = df_mes_atual[df_mes_atual['status'] == 'Pendente']['numero_pedido'].nunique()
    pedidos_finalizados = df_mes_atual[df_mes_atual['status'] == 'Finalizado']['numero_pedido'].nunique()
    
    taxa_conversao = (pedidos_confirmados / total_pedidos * 100) if total_pedidos > 0 else 0
    taxa_finalizacao = (pedidos_finalizados / total_pedidos * 100) if total_pedidos > 0 else 0
    
    receita_por_pedido = df_mes_atual.groupby('numero_pedido')['valor'].sum()
    ticket_medio = receita_por_pedido.mean() if len(receita_por_pedido) > 0 else 0
    
    total_diarias = df_mes_atual['diaria_equipe'].sum()
    pagamentos_pendentes = len(df_mes_atual[df_mes_atual['data_pagamento'] == 'Pendente'])
    
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
    
    df_mes_anterior = df[(df['data_entrega_dt'].dt.month == mes_anterior) & 
                         (df['data_entrega_dt'].dt.year == ano_anterior)]
    receita_mes_anterior = df_mes_anterior['valor'].sum()
    crescimento_receita = ((receita_total - receita_mes_anterior) / receita_mes_anterior * 100) if receita_mes_anterior > 0 else 0
    
    return {
        'receita_total': receita_total,
        'custo_total': custo_total,
        'lucro_total': lucro_total,
        'margem_lucro': margem_lucro,
        'total_pedidos': total_pedidos,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_finalizados': pedidos_finalizados,
        'taxa_conversao': taxa_conversao,
        'taxa_finalizacao': taxa_finalizacao,
        'ticket_medio': ticket_medio,
        'total_diarias': total_diarias,
        'pagamentos_pendentes': pagamentos_pendentes,
        'crescimento_receita': crescimento_receita
    }

def criar_grafico_receita_mensal_real(df):
    """Cria gráfico de receita mensal com dados reais"""
    df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
    df['mes_ano'] = df['data_entrega_dt'].dt.to_period('M')
    
    receita_mensal = df.groupby('mes_ano')['valor'].sum().reset_index()
    receita_mensal['mes_ano_str'] = receita_mensal['mes_ano'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=receita_mensal['mes_ano_str'],
        y=receita_mensal['valor'],
        name='Receita Mensal',
        marker_color='#3b82f6',
        text=receita_mensal['valor'].apply(lambda x: f'R$ {x:,.0f}'),
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

def criar_grafico_lucro_mensal_real(df):
    """Cria gráfico de lucro mensal com dados reais"""
    df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
    df['mes_ano'] = df['data_entrega_dt'].dt.to_period('M')
    
    dados_mensais = df.groupby('mes_ano').agg({
        'valor': 'sum',
        'custos_pedido': 'sum'
    }).reset_index()
    
    dados_mensais['lucro'] = dados_mensais['valor'] - dados_mensais['custos_pedido']
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
    st.markdown("""
    <div class="main-header">
        <h1>🎪 Dashboard Primeira Linha Eventos</h1>
        <h3>Versão 4.0 - Estrutura Real + Produtos Segmentados</h3>
        <p>Gestão Completa de Eventos e Equipamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎛️ Controles")
        
        if st.button("➕ Novo Pedido", use_container_width=True):
            st.success("Funcionalidade de novo pedido será implementada!")
        
        st.markdown("---")
        
        st.markdown("### 📊 Filtros")
        periodo = st.selectbox("Período", ["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"])
        categoria = st.selectbox("Categoria", ["Todas", "Particular", "Público Extra", "Corporativo"])
        local = st.selectbox("Local", ["Todos", "Hotel Ramada", "Torre de TV", "Curralinho", "Esplanada dos Ministérios"])
    
    df = criar_dados_reais_estrutura()
    kpis = calcular_kpis_reais(df)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Evolução", "📋 Pedidos", "⚠️ Alertas"])
    
    with tab1:
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
            st.markdown(f"""
            <div class="metric-card orange">
                <div class="metric-with-icon">
                    <span class="metric-icon">👥</span>
                    <div>
                        <h3>{kpis['total_diarias']}</h3>
                        <p>Diárias de Equipe</p>
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
                        <h3>{kpis['pagamentos_pendentes']}</h3>
                        <p>Pagtos Pendentes</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            fig_receita = criar_grafico_receita_mensal_real(df)
            st.plotly_chart(fig_receita, use_container_width=True)
        
        with col_graf2:
            fig_lucro = criar_grafico_lucro_mensal_real(df)
            st.plotly_chart(fig_lucro, use_container_width=True)
        
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("#### 🏆 Top 5 Produtos Mais Vendidos")
            top_produtos = df.groupby('produto_individual')['valor'].sum().sort_values(ascending=False).head(5)
            
            fig_produtos = px.bar(
                x=top_produtos.values,
                y=top_produtos.index,
                orientation='h',
                title='Receita por Produto Individual',
                color=top_produtos.values,
                color_continuous_scale='viridis'
            )
            fig_produtos.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_produtos, use_container_width=True)
        
        with col_graf4:
            st.markdown("#### 📊 Receita por Categoria")
            dist_categoria = df.groupby('categoria')['valor'].sum()
            
            fig_categoria = px.pie(
                values=dist_categoria.values,
                names=dist_categoria.index,
                title='Distribuição da Receita',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_categoria.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Evolução Temporal")
        
        df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
        df['mes_ano'] = df['data_entrega_dt'].dt.to_period('M')
        
        evolucao = df.groupby('mes_ano').agg({
            'valor': 'sum',
            'custos_pedido': 'sum',
            'numero_pedido': 'nunique'
        }).reset_index()
        
        evolucao['lucro'] = evolucao['valor'] - evolucao['custos_pedido']
        evolucao['mes_ano_str'] = evolucao['mes_ano'].astype(str)
        
        fig_evolucao = go.Figure()
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao['mes_ano_str'],
            y=evolucao['valor'],
            mode='lines+markers',
            name='Receita',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolucao.add_trace(go.Scatter(
            x=evolucao['mes_ano_str'],
            y=evolucao['custos_pedido'],
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
        
        st.markdown("### 📊 Análise de Tendências")
        
        col_tend1, col_tend2, col_tend3 = st.columns(3)
        
        with col_tend1:
            crescimento_medio = evolucao['valor'].pct_change().mean() * 100
            st.markdown(f"""
            <div class="metric-card {'green' if crescimento_medio > 0 else ''}">
                <h4>Crescimento Médio Mensal</h4>
                <h2>{crescimento_medio:+.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_tend2:
            melhor_mes = evolucao.loc[evolucao['valor'].idxmax(), 'mes_ano_str']
            melhor_receita = evolucao['valor'].max()
            st.markdown(f"""
            <div class="metric-card blue">
                <h4>Melhor Mês</h4>
                <h3>{melhor_mes}</h3>
                <p>R$ {melhor_receita:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_tend3:
            margem_media = (evolucao['lucro'] / evolucao['valor'] * 100).mean()
            st.markdown(f"""
            <div class="metric-card purple">
                <h4>Margem Média</h4>
                <h2>{margem_media:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📋 Gestão de Pedidos")
        
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            status_filtro = st.selectbox("Status", ["Todos"] + df['status'].unique().tolist())
        
        with col_filtro2:
            cliente_filtro = st.selectbox("Cliente", ["Todos"] + df['cliente_projeto'].unique().tolist())
        
        with col_filtro3:
            if st.button("🔄 Atualizar Dados"):
                st.rerun()
        
        df_filtrado = df.copy()
        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status_filtro]
        if cliente_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['cliente_projeto'] == cliente_filtro]
        
        st.markdown("#### 📊 Lista de Pedidos por Produto Individual")
        
        df_display = df_filtrado[['numero_pedido', 'cliente_projeto', 'data_entrega', 'categoria', 
                                 'produto_individual', 'valor', 'local', 'status']].copy()
        
        df_display['valor'] = df_display['valor'].apply(lambda x: f'R$ {x:,.2f}')
        
        df_display.columns = ['Nº Pedido', 'Cliente/Projeto', 'Data Entrega', 'Categoria', 
                             'Produto', 'Valor', 'Local', 'Status']
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
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
            valor_total_filtrado = df_filtrado['valor'].sum()
            st.markdown(f"""
            <div class="metric-card green">
                <h4>Valor Total</h4>
                <h2>R$ {valor_total_filtrado:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res3:
            pedidos_unicos = df_filtrado['numero_pedido'].nunique()
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
        
        if kpis['margem_lucro'] < 20:
            st.error(f"🚨 MARGEM BAIXA: {kpis['margem_lucro']:.1f}% (Mín: 20%)")
        
        if kpis['pagamentos_pendentes'] > 5:
            st.error(f"🚨 PAGAMENTOS PENDENTES: {kpis['pagamentos_pendentes']} (Máx: 5)")
        
        if kpis['pedidos_pendentes'] > 3:
            st.warning(f"⚠️ PEDIDOS PENDENTES: {kpis['pedidos_pendentes']} (Máx: 3)")
        
        if kpis['taxa_conversao'] > 70:
            st.success(f"✅ ALTA CONVERSÃO: {kpis['taxa_conversao']:.1f}%")
        
        if kpis['crescimento_receita'] > 15:
            st.success(f"✅ FORTE CRESCIMENTO: {kpis['crescimento_receita']:.1f}%")
    
    st.markdown(f"""
    <div class="footer">
        🎪 Dashboard Primeira Linha Eventos v4.0 | 
        Estrutura Real da Planilha + Produtos Segmentados | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df)} itens carregados
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
