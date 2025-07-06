"""
Dashboard Primeira Linha Eventos - Versão 4.0 DADOS REAIS
Sistema Streamlit usando os dados REAIS da planilha Google Sheets
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
    if pd.isna(descricao_completa) or descricao_completa == "":
        return ["Produto não especificado"]
    
    produtos_conhecidos = {
        'stand octanorme': 'Stand Octanorme',
        'banqueta': 'Banqueta',
        'púlpito': 'Púlpito',
        'palco tablado': 'Palco Tablado',
        'brinquedo inflável': 'Brinquedo Inflável',
        'inflável': 'Brinquedo Inflável',
        'cama elástica': 'Cama Elástica',
        'carrinho de pipoca': 'Carrinho de Pipoca',
        'carrinho de algodão doce': 'Carrinho de Algodão Doce',
        'monitor': 'Monitor/TV',
        'tv': 'Monitor/TV',
        'bebedouro': 'Bebedouro',
        'filtro de água': 'Filtro de Água',
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
        'gerador': 'Gerador',
        'piscina de bolina': 'Piscina de Bolinha',
        'escorregador': 'Escorregador',
        'extintor': 'Extintor de Incêndio',
        'notebook': 'Notebook',
        'impressora': 'Impressora',
        'banner': 'Banner',
        'cone': 'Cone de Sinalização',
        'microfone': 'Microfone',
        'caixa de som': 'Caixa de Som'
    }
    
    produtos_encontrados = []
    descricao_lower = str(descricao_completa).lower()
    
    for palavra_chave, produto_normalizado in produtos_conhecidos.items():
        if palavra_chave in descricao_lower:
            produtos_encontrados.append(produto_normalizado)
    
    # Se não encontrou nenhum produto específico, retorna a descrição original truncada
    if not produtos_encontrados:
        produtos_encontrados = [descricao_completa[:50] + "..." if len(str(descricao_completa)) > 50 else str(descricao_completa)]
    
    return produtos_encontrados

def carregar_dados_reais():
    """Carrega os dados REAIS da planilha Google Sheets"""
    
    # Dados REAIS extraídos da planilha
    dados_reais = [
        {
            'numero_pedido': 'PED001',
            'cliente_projeto': 'Caixa Econômica Federal',
            'categoria': 'Particular',
            'produto_servico_completo': 'stand octanorme plotado + 2 banquetas',
            'valor': 1850,
            'custos_pedido': 600,  # plotagem + 2 banquetas
            'diaria_equipe': 2,
            'local': 'Hotel Ramada',
            'data_entrega': '09/06/2024',
            'data_recolhimento': '10/06/2024',
            'data_pagamento': '13/06/2024',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED002',
            'cliente_projeto': 'Sec. da Mulher',
            'categoria': 'Público Extra',
            'produto_servico_completo': '01 púlpito 01 palco tablado 6x3 02 brinquedos infláveis 01 cama elástica01 carrinho de pipoca 01 carrinho de Algodão doce05 monitores',
            'valor': 4560,
            'custos_pedido': 1000,  # monitores
            'diaria_equipe': 2,
            'local': 'Torre de TV',
            'data_entrega': '13/06/2024',
            'data_recolhimento': '14/06/2024',
            'data_pagamento': 'Pendente',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED003',
            'cliente_projeto': 'Programa "Sempre por Elas"',
            'categoria': 'Público Extra',
            'produto_servico_completo': '02 infláveis03 bebedouros 01 cama elástica01 carrinho de pipoca 01 carrinho de Algodão doce03 tv 50\' 03 suportes para TV',
            'valor': 9080,
            'custos_pedido': 2100,  # monitores
            'diaria_equipe': 0,  # não foi necessário
            'local': 'Curralinho',
            'data_entrega': '23/06/2024',
            'data_recolhimento': '26/03/2024',  # Data original da planilha
            'data_pagamento': 'Pendente',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED004',
            'cliente_projeto': 'Divino Festival',
            'categoria': 'Particular',
            'produto_servico_completo': '01 filtro de água',
            'valor': 980,
            'custos_pedido': 0,  # não foi necessário
            'diaria_equipe': 0,  # não foi necessário
            'local': 'Eixo Cultural Ibero-Americano',
            'data_entrega': '28/06/2024',
            'data_recolhimento': '30/06/2024',
            'data_pagamento': '27/06/2024',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED005',
            'cliente_projeto': 'Instituto Maktub',
            'categoria': 'Público Extra',
            'produto_servico_completo': '02 camas elásticas 01 piscina de bolina 01 inflável',
            'valor': 1310,
            'custos_pedido': 200,  # monitores
            'diaria_equipe': 0,  # não foi necessário
            'local': 'Arniqueiras',
            'data_entrega': '27/06/2024',
            'data_recolhimento': '30/06/2024',
            'data_pagamento': 'Pendente',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED006',
            'cliente_projeto': 'SERPRO (evento BRICS)',
            'categoria': 'Particular',
            'produto_servico_completo': '160 cadeiras estofadas (terceirizado)',
            'valor': 4000,
            'custos_pedido': 3030,  # aluguel terceiro
            'diaria_equipe': 0,  # não foi necessário
            'local': 'Asa Norte',
            'data_entrega': '24/06/2024',
            'data_recolhimento': '27/06/2024',
            'data_pagamento': '30/06/2024',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED007',
            'cliente_projeto': 'Campeonato de Pesca do DF',
            'categoria': 'Público Extra',
            'produto_servico_completo': 'suportes de windbanner (15), Extintor de incendio (10), Placa de Identificação de extintor (10), Placa de Alta tensao (2), Impressora/transformador (01), Resma de Papel (02), Caneta (20), Notebook (05), Fita adesiva (02), Banner estacionamento preferencial (02), Banner Espaço Reservado (02), plaquinhas de banheiros masculino, feminino e PCD (1 de cada), Banner de saída de emergência (1), Grampeador (04), Grampos para grampeador (01 caixa), Extensao de 03 metros (08), Cones(10), Prancheta (10), Filtro de agua (02), Mesa dobrável (10), Tarapes (2 pcts), Pasta (8), Tendas (5) de preferencia na mesma cor, Kits lanche (300), Fita zebrada (1), Fita dupla face (1), Caixas de som com cabeamentos e estrutura necessárias (2), Microfones (2), Cadeiras estofadas (10), Tvs com suporte (2), Cama Elástica (2), Escorregador inflável (1), Q 15 6x3 (1), puffs (04)',
            'valor': 0,  # a definir
            'custos_pedido': 0,  # não foi necessário
            'diaria_equipe': 0,  # não foi necessário
            'local': 'Orla da Concha Acústica',
            'data_entrega': '27/06/2024',
            'data_recolhimento': '30/06/2024',
            'data_pagamento': 'Pendente',
            'status': 'Em Andamento'
        }
    ]
    
    # Criar DataFrame
    df = pd.DataFrame(dados_reais)
    
    # Expandir produtos individuais
    dados_expandidos = []
    for _, row in df.iterrows():
        produtos_individuais = extrair_produtos_individuais(row['produto_servico_completo'])
        
        for produto_individual in produtos_individuais:
            # Distribuir valor e custo proporcionalmente
            valor_produto = row['valor'] / len(produtos_individuais) if row['valor'] > 0 else 0
            custo_produto = row['custos_pedido'] / len(produtos_individuais) if row['custos_pedido'] > 0 else 0
            
            dados_expandidos.append({
                'numero_pedido': row['numero_pedido'],
                'cliente_projeto': row['cliente_projeto'],
                'categoria': row['categoria'],
                'produto_servico_completo': row['produto_servico_completo'],
                'produto_individual': produto_individual,
                'valor': valor_produto,
                'custos_pedido': custo_produto,
                'diaria_equipe': row['diaria_equipe'],
                'local': row['local'],
                'data_entrega': row['data_entrega'],
                'data_recolhimento': row['data_recolhimento'],
                'data_pagamento': row['data_pagamento'],
                'status': row['status']
            })
    
    return pd.DataFrame(dados_expandidos)

def calcular_kpis_reais(df):
    """Calcula KPIs baseados nos dados REAIS"""
    
    # Receita e custos totais
    receita_total = df['valor'].sum()
    custo_total = df['custos_pedido'].sum()
    lucro_total = receita_total - custo_total
    margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
    
    # Pedidos únicos
    total_pedidos = df['numero_pedido'].nunique()
    pedidos_confirmados = df[df['status'] == 'Confirmado']['numero_pedido'].nunique()
    pedidos_pendentes = df[df['status'] == 'Pendente']['numero_pedido'].nunique()
    pedidos_finalizados = df[df['status'] == 'Finalizado']['numero_pedido'].nunique()
    pedidos_em_andamento = df[df['status'] == 'Em Andamento']['numero_pedido'].nunique()
    
    # Taxas
    taxa_conversao = (pedidos_finalizados / total_pedidos * 100) if total_pedidos > 0 else 0
    
    # Ticket médio por pedido
    receita_por_pedido = df.groupby('numero_pedido')['valor'].sum()
    ticket_medio = receita_por_pedido.mean() if len(receita_por_pedido) > 0 else 0
    
    # Diárias de equipe
    total_diarias = df['diaria_equipe'].sum()
    
    # Pagamentos pendentes
    pagamentos_pendentes = len(df[df['data_pagamento'] == 'Pendente']['numero_pedido'].unique())
    
    return {
        'receita_total': receita_total,
        'custo_total': custo_total,
        'lucro_total': lucro_total,
        'margem_lucro': margem_lucro,
        'total_pedidos': total_pedidos,
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_finalizados': pedidos_finalizados,
        'pedidos_em_andamento': pedidos_em_andamento,
        'taxa_conversao': taxa_conversao,
        'ticket_medio': ticket_medio,
        'total_diarias': total_diarias,
        'pagamentos_pendentes': pagamentos_pendentes
    }

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🎪 Dashboard Primeira Linha Eventos</h1>
        <h3>Versão 4.0 - DADOS REAIS da Planilha</h3>
        <p>Gestão Completa de Eventos e Equipamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎛️ Controles")
        
        if st.button("➕ Novo Pedido", use_container_width=True):
            st.success("Funcionalidade de novo pedido será implementada!")
        
        st.markdown("---")
        
        st.markdown("### 📊 Filtros")
        categoria = st.selectbox("Categoria", ["Todas", "Particular", "Público Extra", "Corporativo"])
        status = st.selectbox("Status", ["Todos", "Finalizado", "Em Andamento", "Pendente", "Confirmado"])
    
    # Carregar dados REAIS
    df = carregar_dados_reais()
    kpis = calcular_kpis_reais(df)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if categoria != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
    if status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['status'] == status]
    
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
                        <h3>{kpis['pedidos_finalizados']}</h3>
                        <p>Pedidos Finalizados</p>
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
        
        # Gráficos com dados reais
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("#### 🏆 Top 5 Produtos Mais Vendidos")
            top_produtos = df.groupby('produto_individual')['valor'].sum().sort_values(ascending=False).head(5)
            
            if len(top_produtos) > 0:
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
            else:
                st.info("Nenhum produto com receita para exibir")
        
        with col_graf2:
            st.markdown("#### 📊 Receita por Categoria")
            dist_categoria = df.groupby('categoria')['valor'].sum()
            
            if len(dist_categoria) > 0:
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
            else:
                st.info("Nenhuma categoria com receita para exibir")
        
        # Gráfico de pedidos por status
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.markdown("#### 📋 Status dos Pedidos")
            status_count = df.groupby('status')['numero_pedido'].nunique()
            
            fig_status = px.bar(
                x=status_count.index,
                y=status_count.values,
                title='Quantidade de Pedidos por Status',
                color=status_count.values,
                color_continuous_scale='blues'
            )
            fig_status.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col_graf4:
            st.markdown("#### 🏢 Receita por Cliente")
            receita_cliente = df.groupby('cliente_projeto')['valor'].sum().sort_values(ascending=False).head(5)
            
            fig_cliente = px.bar(
                x=receita_cliente.values,
                y=receita_cliente.index,
                orientation='h',
                title='Top 5 Clientes por Receita',
                color=receita_cliente.values,
                color_continuous_scale='greens'
            )
            fig_cliente.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_cliente, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Evolução Temporal")
        st.info("📅 **Nota:** Com apenas 7 pedidos de junho/2024, gráficos temporais serão mais úteis com mais dados históricos.")
        
        # Análise por mês (mesmo com poucos dados)
        df['data_entrega_dt'] = pd.to_datetime(df['data_entrega'], format='%d/%m/%Y', errors='coerce')
        df['mes_ano'] = df['data_entrega_dt'].dt.to_period('M')
        
        if not df['mes_ano'].isna().all():
            evolucao = df.groupby('mes_ano').agg({
                'valor': 'sum',
                'custos_pedido': 'sum',
                'numero_pedido': 'nunique'
            }).reset_index()
            
            evolucao['lucro'] = evolucao['valor'] - evolucao['custos_pedido']
            evolucao['mes_ano_str'] = evolucao['mes_ano'].astype(str)
            
            col_ev1, col_ev2 = st.columns(2)
            
            with col_ev1:
                fig_receita_mensal = px.bar(
                    evolucao,
                    x='mes_ano_str',
                    y='valor',
                    title='Receita Mensal',
                    color='valor',
                    color_continuous_scale='blues'
                )
                fig_receita_mensal.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_receita_mensal, use_container_width=True)
            
            with col_ev2:
                fig_lucro_mensal = px.bar(
                    evolucao,
                    x='mes_ano_str',
                    y='lucro',
                    title='Lucro Mensal',
                    color='lucro',
                    color_continuous_scale='greens'
                )
                fig_lucro_mensal.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_lucro_mensal, use_container_width=True)
        else:
            st.warning("Não foi possível processar as datas para análise temporal.")
    
    with tab3:
        st.markdown("### 📋 Gestão de Pedidos - DADOS REAIS")
        
        # Tabela de pedidos reais
        st.markdown("#### 📊 Lista de Pedidos da Planilha")
        
        # Preparar dados para exibição
        df_display = df_filtrado[['numero_pedido', 'cliente_projeto', 'data_entrega', 'categoria', 
                                 'produto_individual', 'valor', 'local', 'status']].copy()
        
        df_display['valor'] = df_display['valor'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Renomear colunas
        df_display.columns = ['Nº Pedido', 'Cliente/Projeto', 'Data Entrega', 'Categoria', 
                             'Produto', 'Valor', 'Local', 'Status']
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Resumo dos pedidos filtrados
        st.markdown("#### 📈 Resumo dos Dados Reais")
        
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
        st.markdown("### ⚠️ Sistema de Alertas - DADOS REAIS")
        
        # Alertas baseados nos dados reais
        if kpis['margem_lucro'] < 20:
            st.error(f"🚨 MARGEM BAIXA: {kpis['margem_lucro']:.1f}% (Recomendado: >20%)")
        
        if kpis['pagamentos_pendentes'] > 2:
            st.error(f"🚨 PAGAMENTOS PENDENTES: {kpis['pagamentos_pendentes']} pedidos")
        
        if kpis['pedidos_em_andamento'] > 0:
            st.warning(f"⚠️ PEDIDOS EM ANDAMENTO: {kpis['pedidos_em_andamento']} pedidos")
        
        # Alertas específicos dos dados reais
        pedido_sem_valor = df[df['valor'] == 0]['numero_pedido'].nunique()
        if pedido_sem_valor > 0:
            st.warning(f"⚠️ PEDIDOS SEM VALOR DEFINIDO: {pedido_sem_valor} pedidos")
        
        # Alertas positivos
        if kpis['pedidos_finalizados'] >= 5:
            st.success(f"✅ ÓTIMA EXECUÇÃO: {kpis['pedidos_finalizados']} pedidos finalizados!")
        
        if kpis['margem_lucro'] > 30:
            st.success(f"✅ EXCELENTE MARGEM: {kpis['margem_lucro']:.1f}%")
        
        # Resumo de alertas
        st.markdown("### 📊 Resumo de Alertas")
        
        alertas_criticos = 0
        alertas_atencao = 0
        alertas_positivos = 0
        
        if kpis['margem_lucro'] < 20: alertas_criticos += 1
        if kpis['pagamentos_pendentes'] > 2: alertas_criticos += 1
        if kpis['pedidos_em_andamento'] > 0: alertas_atencao += 1
        if pedido_sem_valor > 0: alertas_atencao += 1
        if kpis['pedidos_finalizados'] >= 5: alertas_positivos += 1
        if kpis['margem_lucro'] > 30: alertas_positivos += 1
        
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
    
    st.markdown(f"""
    <div class="footer">
        🎪 Dashboard Primeira Linha Eventos v4.0 | 
        📊 DADOS REAIS da Planilha Google Sheets | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df)} itens carregados | 7 pedidos reais
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
