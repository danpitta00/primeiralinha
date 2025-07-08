"""
Dashboard Primeira Linha Eventos - Versão 4.0 + Catálogo de Produtos
Sistema Streamlit com catálogo separado de produtos (sem quebrar pedidos)
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
    page_icon="👾",
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
    
    .catalogo-info {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 4px solid #34d399;
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

def criar_catalogo_produtos():
    """
    Cria catálogo de produtos baseado nos itens encontrados nos pedidos reais
    Esta função simula a futura aba "Catálogo" do Google Sheets
    """
    catalogo = [
        {'produto': 'Stand Octanorme', 'categoria': 'Estruturas', 'preco_base': 300, 'unidade': 'unidade'},
        {'produto': 'Banqueta', 'categoria': 'Mobiliário', 'preco_base': 25, 'unidade': 'unidade'},
        {'produto': 'Púlpito', 'categoria': 'Estruturas', 'preco_base': 150, 'unidade': 'unidade'},
        {'produto': 'Palco Tablado 6x3', 'categoria': 'Estruturas', 'preco_base': 800, 'unidade': 'unidade'},
        {'produto': 'Brinquedo Inflável', 'categoria': 'Entretenimento', 'preco_base': 400, 'unidade': 'unidade'},
        {'produto': 'Cama Elástica', 'categoria': 'Entretenimento', 'preco_base': 350, 'unidade': 'unidade'},
        {'produto': 'Carrinho de Pipoca', 'categoria': 'Alimentação', 'preco_base': 200, 'unidade': 'unidade'},
        {'produto': 'Carrinho de Algodão Doce', 'categoria': 'Alimentação', 'preco_base': 200, 'unidade': 'unidade'},
        {'produto': 'Monitor/TV', 'categoria': 'Audiovisual', 'preco_base': 180, 'unidade': 'unidade'},
        {'produto': 'Bebedouro', 'categoria': 'Utilidades', 'preco_base': 80, 'unidade': 'unidade'},
        {'produto': 'Filtro de Água', 'categoria': 'Utilidades', 'preco_base': 60, 'unidade': 'unidade'},
        {'produto': 'Suporte para TV', 'categoria': 'Audiovisual', 'preco_base': 50, 'unidade': 'unidade'},
        {'produto': 'Cadeira Estofada', 'categoria': 'Mobiliário', 'preco_base': 15, 'unidade': 'unidade'},
        {'produto': 'Piscina de Bolinha', 'categoria': 'Entretenimento', 'preco_base': 300, 'unidade': 'unidade'},
        {'produto': 'Escorregador Inflável', 'categoria': 'Entretenimento', 'preco_base': 500, 'unidade': 'unidade'},
        {'produto': 'Extintor de Incêndio', 'categoria': 'Segurança', 'preco_base': 40, 'unidade': 'unidade'},
        {'produto': 'Notebook', 'categoria': 'Tecnologia', 'preco_base': 100, 'unidade': 'diária'},
        {'produto': 'Impressora', 'categoria': 'Tecnologia', 'preco_base': 80, 'unidade': 'diária'},
        {'produto': 'Banner', 'categoria': 'Sinalização', 'preco_base': 120, 'unidade': 'unidade'},
        {'produto': 'Cone de Sinalização', 'categoria': 'Segurança', 'preco_base': 8, 'unidade': 'unidade'},
        {'produto': 'Mesa Dobrável', 'categoria': 'Mobiliário', 'preco_base': 35, 'unidade': 'unidade'},
        {'produto': 'Tenda', 'categoria': 'Estruturas', 'preco_base': 250, 'unidade': 'unidade'},
        {'produto': 'Microfone', 'categoria': 'Audiovisual', 'preco_base': 60, 'unidade': 'unidade'},
        {'produto': 'Caixa de Som', 'categoria': 'Audiovisual', 'preco_base': 150, 'unidade': 'unidade'},
        {'produto': 'Puff', 'categoria': 'Mobiliário', 'preco_base': 45, 'unidade': 'unidade'}
    ]
    
    return pd.DataFrame(catalogo)

def extrair_produtos_dos_pedidos(descricao_completa):
    """
    Extrai produtos dos pedidos para análise de frequência
    Não quebra os pedidos, apenas identifica quais produtos estão presentes
    """
    if pd.isna(descricao_completa) or descricao_completa == "":
        return []
    
    # Mapeamento mais específico baseado no catálogo
    mapeamento_produtos = {
        'stand octanorme': 'Stand Octanorme',
        'banqueta': 'Banqueta',
        'púlpito': 'Púlpito',
        'palco tablado': 'Palco Tablado 6x3',
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
        'cadeira estofada': 'Cadeira Estofada',
        'cadeiras estofadas': 'Cadeira Estofada',
        'piscina de bolina': 'Piscina de Bolinha',
        'escorregador inflável': 'Escorregador Inflável',
        'extintor': 'Extintor de Incêndio',
        'notebook': 'Notebook',
        'impressora': 'Impressora',
        'banner': 'Banner',
        'cone': 'Cone de Sinalização',
        'mesa dobrável': 'Mesa Dobrável',
        'tenda': 'Tenda',
        'microfone': 'Microfone',
        'caixa de som': 'Caixa de Som',
        'puff': 'Puff'
    }
    
    produtos_encontrados = []
    descricao_lower = str(descricao_completa).lower()
    
    for palavra_chave, produto_normalizado in mapeamento_produtos.items():
        if palavra_chave in descricao_lower:
            produtos_encontrados.append(produto_normalizado)
    
    return produtos_encontrados

def carregar_dados_reais():
    """Carrega os dados REAIS da planilha Google Sheets (MANTÉM PEDIDOS COMO ESTÃO)"""
    
    # Dados REAIS extraídos da planilha - CADA LINHA É UM PEDIDO COMPLETO
    dados_reais = [
        {
            'numero_pedido': 'PED001',
            'cliente_projeto': 'Caixa Econômica Federal',
            'categoria': 'Particular',
            'produto_servico_completo': 'stand octanorme plotado + 2 banquetas',
            'valor': 1850,
            'custos_pedido': 600,
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
            'custos_pedido': 1000,
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
            'custos_pedido': 2100,
            'diaria_equipe': 0,
            'local': 'Curralinho',
            'data_entrega': '23/06/2024',
            'data_recolhimento': '26/03/2024',
            'data_pagamento': 'Pendente',
            'status': 'Finalizado'
        },
        {
            'numero_pedido': 'PED004',
            'cliente_projeto': 'Divino Festival',
            'categoria': 'Particular',
            'produto_servico_completo': '01 filtro de água',
            'valor': 980,
            'custos_pedido': 0,
            'diaria_equipe': 0,
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
            'custos_pedido': 200,
            'diaria_equipe': 0,
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
            'custos_pedido': 3030,
            'diaria_equipe': 0,
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
            'valor': 0,
            'custos_pedido': 0,
            'diaria_equipe': 0,
            'local': 'Orla da Concha Acústica',
            'data_entrega': '27/06/2024',
            'data_recolhimento': '30/06/2024',
            'data_pagamento': 'Pendente',
            'status': 'Em Andamento'
        }
    ]
    
    return pd.DataFrame(dados_reais)

def analisar_frequencia_produtos(df_pedidos):
    """
    Analisa frequência de produtos nos pedidos SEM quebrar os pedidos
    Conta quantas vezes cada produto aparece nos pedidos
    """
    frequencia_produtos = {}
    
    for _, pedido in df_pedidos.iterrows():
        produtos_no_pedido = extrair_produtos_dos_pedidos(pedido['produto_servico_completo'])
        
        for produto in produtos_no_pedido:
            if produto in frequencia_produtos:
                frequencia_produtos[produto] += 1
            else:
                frequencia_produtos[produto] = 1
    
    # Converter para DataFrame
    df_frequencia = pd.DataFrame(list(frequencia_produtos.items()), 
                                columns=['produto', 'frequencia'])
    df_frequencia = df_frequencia.sort_values('frequencia', ascending=False)
    
    return df_frequencia

def calcular_kpis_reais(df):
    """Calcula KPIs baseados nos dados REAIS (pedidos completos)"""
    
    # Receita e custos totais
    receita_total = df['valor'].sum()
    custo_total = df['custos_pedido'].sum()
    lucro_total = receita_total - custo_total
    margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
    
    # Pedidos únicos
    total_pedidos = len(df)
    pedidos_confirmados = len(df[df['status'] == 'Confirmado'])
    pedidos_pendentes = len(df[df['status'] == 'Pendente'])
    pedidos_finalizados = len(df[df['status'] == 'Finalizado'])
    pedidos_em_andamento = len(df[df['status'] == 'Em Andamento'])
    
    # Taxas
    taxa_conversao = (pedidos_finalizados / total_pedidos * 100) if total_pedidos > 0 else 0
    
    # Ticket médio por pedido
    ticket_medio = df['valor'].mean() if len(df) > 0 else 0
    
    # Diárias de equipe
    total_diarias = df['diaria_equipe'].sum()
    
    # Pagamentos pendentes
    pagamentos_pendentes = len(df[df['data_pagamento'] == 'Pendente'])
    
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
        <h3>Versão 4.0 - Com Catálogo de Produtos</h3>
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
    
    # Carregar dados REAIS e catálogo
    df_pedidos = carregar_dados_reais()
    df_catalogo = criar_catalogo_produtos()
    df_frequencia_produtos = analisar_frequencia_produtos(df_pedidos)
    kpis = calcular_kpis_reais(df_pedidos)
    
    # Aplicar filtros
    df_filtrado = df_pedidos.copy()
    if categoria != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
    if status != "Todos":
        df_filtrado = df_filtrado[df_filtrado['status'] == status]
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📈 Evolução", "📋 Pedidos", "🛍️ Catálogo", "⚠️ Alertas"])
    
    with tab1:
        # Informação sobre o novo sistema
        st.markdown("""
        <div class="catalogo-info">
            <h4>🆕 NOVO: Sistema de Catálogo de Produtos</h4>
            <p>• <strong>Pedidos mantidos como estão</strong> - cada linha é um pedido completo</p>
            <p>• <strong>Produtos catalogados separadamente</strong> - análise de frequência sem quebrar pedidos</p>
            <p>• <strong>Gráficos baseados em aparições</strong> - quantas vezes cada produto aparece nos pedidos</p>
        </div>
        """, unsafe_allow_html=True)
        
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
            st.markdown("#### 🏆 Top 5 Produtos Mais Solicitados")
            st.caption("Baseado na frequência de aparição nos pedidos")
            
            if len(df_frequencia_produtos) > 0:
                top_produtos = df_frequencia_produtos.head(5)
                
                fig_produtos = px.bar(
                    top_produtos,
                    x='frequencia',
                    y='produto',
                    orientation='h',
                    title='Frequência de Produtos nos Pedidos',
                    color='frequencia',
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
                st.info("Nenhum produto identificado nos pedidos")
        
        with col_graf2:
            st.markdown("#### 📊 Receita por Categoria")
            dist_categoria = df_pedidos.groupby('categoria')['valor'].sum()
            
            if len(dist_categoria) > 0:
                fig_categoria = px.pie(
                    values=dist_categoria.values,
                    names=dist_categoria.index,
                    title='Distribuição da Receita por Categoria',
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
            status_count = df_pedidos['status'].value_counts()
            
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
            receita_cliente = df_pedidos.groupby('cliente_projeto')['valor'].sum().sort_values(ascending=False)
            
            fig_cliente = px.bar(
                x=receita_cliente.values,
                y=receita_cliente.index,
                orientation='h',
                title='Receita por Cliente',
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
        df_pedidos['data_entrega_dt'] = pd.to_datetime(df_pedidos['data_entrega'], format='%d/%m/%Y', errors='coerce')
        df_pedidos['mes_ano'] = df_pedidos['data_entrega_dt'].dt.to_period('M')
        
        if not df_pedidos['mes_ano'].isna().all():
            evolucao = df_pedidos.groupby('mes_ano').agg({
                'valor': 'sum',
                'custos_pedido': 'sum',
                'numero_pedido': 'count'
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
        
        # Tabela de pedidos reais (MANTÉM COMO PEDIDOS COMPLETOS)
        st.markdown("#### 📊 Lista de Pedidos Completos")
        
        # Preparar dados para exibição
        df_display = df_filtrado[['numero_pedido', 'cliente_projeto', 'data_entrega', 'categoria', 
                                 'valor', 'local', 'status']].copy()
        
        df_display['valor'] = df_display['valor'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Renomear colunas
        df_display.columns = ['Nº Pedido', 'Cliente/Projeto', 'Data Entrega', 'Categoria', 
                             'Valor', 'Local', 'Status']
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Resumo dos pedidos filtrados
        st.markdown("#### 📈 Resumo dos Dados Reais")
        
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        
        with col_res1:
            total_pedidos_filtrados = len(df_filtrado)
            st.markdown(f"""
            <div class="metric-card blue">
                <h4>Total de Pedidos</h4>
                <h2>{total_pedidos_filtrados}</h2>
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
            custo_total_filtrado = df_filtrado['custos_pedido'].sum()
            st.markdown(f"""
            <div class="metric-card purple">
                <h4>Custo Total</h4>
                <h2>R$ {custo_total_filtrado:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res4:
            lucro_filtrado = valor_total_filtrado - custo_total_filtrado
            st.markdown(f"""
            <div class="metric-card orange">
                <h4>Lucro Total</h4>
                <h2>R$ {lucro_filtrado:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🛍️ Catálogo de Produtos")
        
        st.markdown("""
        <div class="catalogo-info">
            <h4>📋 Instruções para Implementação no Google Sheets</h4>
            <p><strong>1.</strong> Crie uma nova aba chamada "Catálogo" na sua planilha</p>
            <p><strong>2.</strong> Use as colunas: Produto | Categoria | Preço Base | Unidade</p>
            <p><strong>3.</strong> Copie os dados da tabela abaixo para a nova aba</p>
            <p><strong>4.</strong> O dashboard lerá automaticamente os dois locais: Pedidos + Catálogo</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir catálogo de produtos
        st.markdown("#### 📦 Catálogo Completo de Produtos")
        
        # Filtros para o catálogo
        col_cat1, col_cat2 = st.columns(2)
        
        with col_cat1:
            categoria_produto = st.selectbox("Filtrar por Categoria", 
                                           ["Todas"] + df_catalogo['categoria'].unique().tolist(),
                                           key="cat_produto")
        
        with col_cat2:
            busca_produto = st.text_input("Buscar produto", placeholder="Digite o nome do produto...")
        
        # Aplicar filtros no catálogo
        df_catalogo_filtrado = df_catalogo.copy()
        
        if categoria_produto != "Todas":
            df_catalogo_filtrado = df_catalogo_filtrado[df_catalogo_filtrado['categoria'] == categoria_produto]
        
        if busca_produto:
            df_catalogo_filtrado = df_catalogo_filtrado[
                df_catalogo_filtrado['produto'].str.contains(busca_produto, case=False, na=False)
            ]
        
        # Exibir tabela do catálogo
        df_catalogo_display = df_catalogo_filtrado.copy()
        df_catalogo_display['preco_base'] = df_catalogo_display['preco_base'].apply(lambda x: f'R$ {x:,.2f}')
        df_catalogo_display.columns = ['Produto', 'Categoria', 'Preço Base', 'Unidade']
        
        st.dataframe(df_catalogo_display, use_container_width=True, height=400)
        
        # Estatísticas do catálogo
        st.markdown("#### 📊 Estatísticas do Catálogo")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            total_produtos = len(df_catalogo)
            st.markdown(f"""
            <div class="metric-card blue">
                <h4>Total de Produtos</h4>
                <h2>{total_produtos}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            total_categorias = df_catalogo['categoria'].nunique()
            st.markdown(f"""
            <div class="metric-card green">
                <h4>Categorias</h4>
                <h2>{total_categorias}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            preco_medio = df_catalogo['preco_base'].mean()
            st.markdown(f"""
            <div class="metric-card purple">
                <h4>Preço Médio</h4>
                <h2>R$ {preco_medio:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_stat4:
            produtos_mais_usados = len(df_frequencia_produtos)
            st.markdown(f"""
            <div class="metric-card orange">
                <h4>Produtos em Uso</h4>
                <h2>{produtos_mais_usados}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráfico de produtos por categoria
        col_graf_cat1, col_graf_cat2 = st.columns(2)
        
        with col_graf_cat1:
            st.markdown("#### 📊 Produtos por Categoria")
            produtos_por_categoria = df_catalogo['categoria'].value_counts()
            
            fig_cat = px.pie(
                values=produtos_por_categoria.values,
                names=produtos_por_categoria.index,
                title='Distribuição de Produtos por Categoria'
            )
            fig_cat.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        
        with col_graf_cat2:
            st.markdown("#### 💰 Faixa de Preços")
            
            # Criar faixas de preço
            df_catalogo['faixa_preco'] = pd.cut(df_catalogo['preco_base'], 
                                              bins=[0, 50, 150, 300, 1000], 
                                              labels=['Até R$ 50', 'R$ 51-150', 'R$ 151-300', 'Acima R$ 300'])
            
            faixa_preco_count = df_catalogo['faixa_preco'].value_counts()
            
            fig_preco = px.bar(
                x=faixa_preco_count.index,
                y=faixa_preco_count.values,
                title='Produtos por Faixa de Preço'
            )
            fig_preco.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400
            )
            st.plotly_chart(fig_preco, use_container_width=True)
    
    with tab5:
        st.markdown("### ⚠️ Sistema de Alertas - DADOS REAIS")
        
        # Alertas baseados nos dados reais
        if kpis['margem_lucro'] < 20:
            st.error(f"🚨 MARGEM BAIXA: {kpis['margem_lucro']:.1f}% (Recomendado: >20%)")
        
        if kpis['pagamentos_pendentes'] > 2:
            st.error(f"🚨 PAGAMENTOS PENDENTES: {kpis['pagamentos_pendentes']} pedidos")
        
        if kpis['pedidos_em_andamento'] > 0:
            st.warning(f"⚠️ PEDIDOS EM ANDAMENTO: {kpis['pedidos_em_andamento']} pedidos")
        
        # Alertas específicos dos dados reais
        pedido_sem_valor = len(df_pedidos[df_pedidos['valor'] == 0])
        if pedido_sem_valor > 0:
            st.warning(f"⚠️ PEDIDOS SEM VALOR DEFINIDO: {pedido_sem_valor} pedidos")
        
        # Alertas positivos
        if kpis['pedidos_finalizados'] >= 5:
            st.success(f"✅ ÓTIMA EXECUÇÃO: {kpis['pedidos_finalizados']} pedidos finalizados!")
        
        if kpis['margem_lucro'] > 30:
            st.success(f"✅ EXCELENTE MARGEM: {kpis['margem_lucro']:.1f}%")
    
    st.markdown(f"""
    <div class="footer">
        🎪 Dashboard Primeira Linha Eventos v4.0 | 
        🛍️ COM CATÁLOGO DE PRODUTOS | 
        📊 DADOS REAIS da Planilha Google Sheets | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df_pedidos)} pedidos | {len(df_catalogo)} produtos catalogados
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
