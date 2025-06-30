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

# Título principal
st.title("🎪 Dashboard Primeira Linha Eventos")
st.markdown("### Análise de Pedidos e Performance")

# Função para carregar e limpar dados
@st.cache_data
def load_and_clean_data(file_path):
    """Carrega e limpa os dados da planilha de pedidos"""
    try:
        df = pd.read_csv(file_path)
        
        # Renomear colunas para padronização e facilitar o uso
        df.columns = [
            'ID do Pedido', 'Cliente/Projeto', 'Categoria', 'Produto/Serviço', 
            'Valor Total', 'Custo do Pedido', 'Diárias Equipe', 'Local', 
            'Data Entrega', 'Data Recolhimento', 'Data Pagamento'
        ]

        # 1. NÃO gerar ID automático - deixar vazio para preenchimento posterior
        # df['ID do Pedido'] = df['ID do Pedido'].fillna('PENDENTE_PREENCHIMENTO')

        # 2. Padronizar as 3 categorias: Público, Público EXTRA, Privado
        df['Categoria'] = df['Categoria'].replace({
            'particular': 'Privado', 
            'Público Extra': 'Público EXTRA',
            'público': 'Público',
            'público extra': 'Público EXTRA',
            'privado': 'Privado'
        })

        # 6. Padronizar valores pendentes de fechamento com clientes
        df['Valor Total'] = df['Valor Total'].replace({'a definir': 'A DEFINIR'})
        
        # Criar coluna para identificar valores pendentes
        df['Valor_Pendente'] = df['Valor Total'].apply(lambda x: True if str(x).upper() in ['A DEFINIR', 'NAN'] else False)
        
        # Converter valores numéricos, mantendo os pendentes como string
        df['Valor_Numerico'] = pd.to_numeric(df['Valor Total'], errors='coerce')

        # Limpar e converter 'Custo do Pedido'
        df['Custo_Original'] = df['Custo do Pedido'].copy()
        df['Custo_Pendente'] = df['Custo do Pedido'].apply(lambda x: True if str(x).lower() in ['x', 'nan'] else False)
        df['Custo_Numerico'] = df['Custo do Pedido'].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # Limpar e converter 'Diárias Equipe'
        df['Diarias_Original'] = df['Diárias Equipe'].copy()
        df['Diarias_Pendente'] = df['Diárias Equipe'].apply(lambda x: True if str(x).lower() in ['x', 'nan'] else False)
        df['Diarias_Numerico'] = df['Diárias Equipe'].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # Converter colunas de data
        date_columns = ['Data Entrega', 'Data Recolhimento', 'Data Pagamento']
        for col in date_columns:
            # 4. Identificar datas pendentes
            df[f'{col}_Pendente'] = df[col].apply(lambda x: True if str(x).lower() in ['indefinido', 'nan'] else False)
            df[col] = df[col].replace({'indefinido': np.nan})
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        
        # Adicionar 'Data do Pedido' (simulada se não existir no CSV original)
        df['Data do Pedido'] = df['Data Entrega'].fillna(pd.to_datetime(datetime.now().date())) - pd.Timedelta(days=1)

        # Adicionar 'Status Pagamento' (baseado na 'Data Pagamento')
        df['Status Pagamento'] = df['Data Pagamento'].apply(
            lambda x: 'Pago' if pd.notna(x) and x <= datetime.now() 
            else ('Pendente' if pd.notna(x) and x > datetime.now() else 'Indefinido')
        )
        
        # Ajuste para casos onde a data de pagamento é futura, mas o pedido já deveria ter sido pago
        df.loc[(df['Status Pagamento'] == 'Pendente') & (df['Data Entrega'] < datetime.now()), 'Status Pagamento'] = 'Atrasado'

        # Calcular 'Lucro Bruto' apenas para pedidos com valores definidos
        custo_diaria_padrao = 150.00
        df['Lucro Bruto'] = np.where(
            df['Valor_Pendente'] | df['Custo_Pendente'] | df['Diarias_Pendente'],
            np.nan,  # Não calcular lucro se algum valor estiver pendente
            df['Valor_Numerico'] - df['Custo_Numerico'] - (df['Diarias_Numerico'] * custo_diaria_padrao)
        )
        
        return df
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Função para destacar células pendentes
def highlight_pending(val, is_pending):
    """Destaca células com informações pendentes"""
    if is_pending:
        return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    return ''

# Carregar dados
df = load_and_clean_data('Planilhasemtítulo-Página1.csv')

if not df.empty:
    # Alertas de informações pendentes
    st.markdown("### ⚠️ Informações Pendentes de Preenchimento")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pedidos_sem_id = df['ID do Pedido'].isna().sum()
        st.metric("Pedidos sem ID", pedidos_sem_id, delta=None if pedidos_sem_id == 0 else "⚠️")
    
    with col2:
        valores_pendentes = df['Valor_Pendente'].sum()
        st.metric("Valores a Definir", valores_pendentes, delta=None if valores_pendentes == 0 else "⚠️")
    
    with col3:
        custos_pendentes = df['Custo_Pendente'].sum()
        st.metric("Custos Indefinidos", custos_pendentes, delta=None if custos_pendentes == 0 else "⚠️")
    
    with col4:
        pagamentos_indefinidos = df['Data Pagamento_Pendente'].sum()
        st.metric("Pagamentos Indefinidos", pagamentos_indefinidos, delta=None if pagamentos_indefinidos == 0 else "⚠️")

    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por categoria (considerando as 3 categorias)
    categorias = ["Todos"] + sorted(df["Categoria"].dropna().unique().tolist())
    categoria_selecionada = st.sidebar.selectbox("Categoria", categorias)
    
    # Filtro por status de pagamento
    status_pagamento = ["Todos"] + sorted(df["Status Pagamento"].unique().tolist())
    status_selecionado = st.sidebar.selectbox("Status Pagamento", status_pagamento)
    
    # Filtro para mostrar apenas pendências
    mostrar_apenas_pendencias = st.sidebar.checkbox("Mostrar apenas itens com pendências")
    
    # Filtro por período
    st.sidebar.subheader("Período da Data do Pedido")
    min_date = df["Data do Pedido"].min().date() if pd.notna(df["Data do Pedido"].min()) else datetime.now().date() - timedelta(days=30)
    max_date = df["Data do Pedido"].max().date() if pd.notna(df["Data do Pedido"].max()) else datetime.now().date()

    data_inicio = st.sidebar.date_input("Data Início", min_date)
    data_fim = st.sidebar.date_input("Data Fim", max_date)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if categoria_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_selecionada]
    
    if status_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status Pagamento"] == status_selecionado]
    
    if mostrar_apenas_pendencias:
        df_filtrado = df_filtrado[
            df_filtrado['Valor_Pendente'] | 
            df_filtrado['Custo_Pendente'] | 
            df_filtrado['Diarias_Pendente'] | 
            df_filtrado['Data Pagamento_Pendente'] |
            df_filtrado['ID do Pedido'].isna()
        ]
    
    df_filtrado = df_filtrado[
        (df_filtrado["Data do Pedido"] >= pd.to_datetime(data_inicio)) &
        (df_filtrado["Data do Pedido"] <= pd.to_datetime(data_fim))
    ]
    
    # Métricas principais (apenas para pedidos com valores definidos)
    df_com_valores = df_filtrado[~df_filtrado['Valor_Pendente']]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pedidos = len(df_filtrado)
        st.metric("Total de Pedidos", total_pedidos)
    
    with col2:
        receita_total = df_com_valores["Valor_Numerico"].sum()
        st.metric("Receita Confirmada", f"R$ {receita_total:,.2f}")
    
    with col3:
        lucro_total = df_com_valores["Lucro Bruto"].sum()
        st.metric("Lucro Bruto Confirmado", f"R$ {lucro_total:,.2f}")
    
    with col4:
        margem_lucro = (lucro_total / receita_total * 100) if receita_total > 0 else 0
        st.metric("Margem de Lucro", f"{margem_lucro:.1f}%")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Receita por Categoria")
        receita_categoria = df_com_valores.groupby("Categoria")["Valor_Numerico"].sum().reset_index()
        if not receita_categoria.empty:
            fig_categoria = px.pie(
                receita_categoria, 
                values="Valor_Numerico", 
                names="Categoria",
                title="Distribuição de Receita por Categoria (Valores Confirmados)"
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
        else:
            st.info("Nenhum valor confirmado para exibir no gráfico")
    
    with col2:
        st.subheader("💰 Status de Pagamento")
        status_count = df_filtrado["Status Pagamento"].value_counts().reset_index()
        status_count.columns = ["Status", "Quantidade"]
        fig_status = px.bar(
            status_count, 
            x="Status", 
            y="Quantidade",
            title="Pedidos por Status de Pagamento",
            color="Status"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Tabela de pendências destacadas
    st.subheader("📋 Detalhes dos Pedidos com Destaques para Pendências")
    
    # Preparar dados para exibição com destaques
    df_display = df_filtrado.copy()
    
    # Substituir valores para melhor visualização
    df_display['ID do Pedido'] = df_display['ID do Pedido'].fillna('⚠️ PENDENTE')
    df_display['Valor Total'] = df_display.apply(
        lambda row: '⚠️ A DEFINIR' if row['Valor_Pendente'] else f"R$ {row['Valor_Numerico']:,.2f}",
        axis=1
    )
    df_display['Custo do Pedido'] = df_display.apply(
        lambda row: '⚠️ INDEFINIDO' if row['Custo_Pendente'] else f"R$ {row['Custo_Numerico']:,.2f}",
        axis=1
    )
    df_display['Diárias Equipe'] = df_display.apply(
        lambda row: '⚠️ INDEFINIDO' if row['Diarias_Pendente'] else str(int(row['Diarias_Numerico'])),
        axis=1
    )
    df_display['Data Pagamento'] = df_display.apply(
        lambda row: '⚠️ INDEFINIDO' if row['Data Pagamento_Pendente'] else row['Data Pagamento'].strftime('%d/%m/%Y') if pd.notna(row['Data Pagamento']) else 'Não informado',
        axis=1
    )
    
    # Colunas para exibição
    colunas_exibicao = [
        'ID do Pedido', 'Cliente/Projeto', 'Categoria', 'Produto/Serviço',
        'Valor Total', 'Custo do Pedido', 'Diárias Equipe', 'Local',
        'Data Entrega', 'Data Recolhimento', 'Data Pagamento', 'Status Pagamento'
    ]
    
    st.dataframe(
        df_display[colunas_exibicao],
        use_container_width=True,
        height=400
    )
    
    # Resumo de pendências por categoria
    st.subheader("📊 Resumo de Pendências por Categoria")
    
    resumo_pendencias = df_filtrado.groupby('Categoria').agg({
        'Valor_Pendente': 'sum',
        'Custo_Pendente': 'sum',
        'Diarias_Pendente': 'sum',
        'Data Pagamento_Pendente': 'sum'
    }).reset_index()
    
    resumo_pendencias.columns = [
        'Categoria', 'Valores a Definir', 'Custos Indefinidos', 
        'Diárias Indefinidas', 'Pagamentos Indefinidos'
    ]
    
    st.dataframe(resumo_pendencias, use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo está disponível.")

# Rodapé
st.markdown("---")
st.markdown("**Primeira Linha Eventos** - Dashboard de Gestão de Pedidos")
st.markdown("🔴 **Vermelho/⚠️**: Informações pendentes de preenchimento")

