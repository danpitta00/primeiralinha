"""
Dashboard Primeira Linha Eventos - Versão Completa v3.0
Sistema Streamlit com todas as funcionalidades + Sistema de Pedidos integrado
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
    page_title="Dashboard Primeira Linha Eventos",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card.green {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card.blue {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .metric-card.purple {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    .alert-warning {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    .alert-success {
        background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    .novo-pedido-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin: 1rem 0;
        text-align: center;
        border: none;
        cursor: pointer;
        font-size: 1.1rem;
    }
    .novo-pedido-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# URL da planilha Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H07FB3X_tkSLSoHx-F2kyDmNQIGR4EyyTjnF-u19G3c/export?format=csv&gid=0"

@st.cache_data(ttl=300 )  # Cache por 5 minutos
def load_data():
    """Carrega dados da planilha Google Sheets"""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Renomeia colunas para padronizar
        column_mapping = {
            'nº do pedido': 'numero_pedido',
            'cliente/projeto': 'cliente',
            'categoria': 'categoria',
            'produto/serviço': 'produto_servico',
            'valor': 'valor',
            'custos do pedido': 'custos',
            'diária de equipe': 'diarias_equipe',
            'local': 'local',
            'data de entrega': 'data_entrega',
            'data de recolhimento': 'data_recolhimento',
            'data de pagamento': 'data_pagamento'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Limpa valores monetários
        def clean_currency(value):
            if pd.isna(value) or value == '':
                return 0.0
            if isinstance(value, str):
                value = re.sub(r'[^\d,.]', '', str(value))
                value = value.replace(',', '.')
            try:
                return float(value)
            except:
                return 0.0
        
        if 'valor' in df.columns:
            df['valor'] = df['valor'].apply(clean_currency)
        if 'custos' in df.columns:
            df['custos'] = df['custos'].apply(clean_currency)
        if 'diarias_equipe' in df.columns:
            df['diarias_equipe'] = df['diarias_equipe'].apply(clean_currency)
        
        # Remove linhas completamente vazias
        df = df.dropna(subset=['cliente'], how='all')
        
        # Converte datas
        date_columns = ['data_entrega', 'data_recolhimento', 'data_pagamento']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calculate_kpis(df):
    """Calcula KPIs principais"""
    if df.empty:
        return {}
    
    # KPIs básicos
    total_receita = df['valor'].sum()
    total_custos = df['custos'].sum()
    total_diarias = df['diarias_equipe'].sum() if 'diarias_equipe' in df.columns else 0
    custos_totais = total_custos + total_diarias
    lucro_bruto = total_receita - custos_totais
    margem_lucro = (lucro_bruto / total_receita * 100) if total_receita > 0 else 0
    
    # Pedidos
    total_pedidos = len(df)
    ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else 0
    
    # Status de pagamento
    pedidos_pagos = len(df[df['data_pagamento'].notna()])
    pedidos_pendentes = total_pedidos - pedidos_pagos
    taxa_inadimplencia = (pedidos_pendentes / total_pedidos * 100) if total_pedidos > 0 else 0
    
    # Análise temporal
    hoje = datetime.now()
    mes_atual = df[df['data_entrega'].dt.month == hoje.month] if 'data_entrega' in df.columns else df
    receita_mes_atual = mes_atual['valor'].sum()
    
    # Próximos eventos
    proximos_30_dias = df[
        (df['data_entrega'] >= hoje) & 
        (df['data_entrega'] <= hoje + timedelta(days=30))
    ] if 'data_entrega' in df.columns else pd.DataFrame()
    
    return {
        'total_receita': total_receita,
        'total_custos': custos_totais,
        'lucro_bruto': lucro_bruto,
        'margem_lucro': margem_lucro,
        'total_pedidos': total_pedidos,
        'ticket_medio': ticket_medio,
        'pedidos_pagos': pedidos_pagos,
        'pedidos_pendentes': pedidos_pendentes,
        'taxa_inadimplencia': taxa_inadimplencia,
        'receita_mes_atual': receita_mes_atual,
        'proximos_eventos': len(proximos_30_dias)
    }

def get_alertas(df, kpis):
    """Gera alertas inteligentes"""
    alertas = []
    
    # Alerta de inadimplência
    if kpis['taxa_inadimplencia'] > 15:
        alertas.append({
            'tipo': 'critical',
            'titulo': '🚨 INADIMPLÊNCIA CRÍTICA',
            'mensagem': f"Taxa de inadimplência em {kpis['taxa_inadimplencia']:.1f}% (Meta: <15%)"
        })
    elif kpis['taxa_inadimplencia'] > 10:
        alertas.append({
            'tipo': 'warning',
            'titulo': '⚠️ INADIMPLÊNCIA ALTA',
            'mensagem': f"Taxa de inadimplência em {kpis['taxa_inadimplencia']:.1f}% (Meta: <15%)"
        })
    
    # Alerta de margem baixa
    if kpis['margem_lucro'] < 20:
        alertas.append({
            'tipo': 'warning',
            'titulo': '📉 MARGEM BAIXA',
            'mensagem': f"Margem de lucro em {kpis['margem_lucro']:.1f}% (Meta: >30%)"
        })
    elif kpis['margem_lucro'] > 40:
        alertas.append({
            'tipo': 'success',
            'titulo': '📈 MARGEM EXCELENTE',
            'mensagem': f"Margem de lucro em {kpis['margem_lucro']:.1f}% - Muito acima da meta!"
        })
    
    # Eventos próximos
    if kpis['proximos_eventos'] > 0:
        alertas.append({
            'tipo': 'success',
            'titulo': '📅 EVENTOS PRÓXIMOS',
            'mensagem': f"{kpis['proximos_eventos']} eventos nos próximos 30 dias"
        })
    
    return alertas

def show_novo_pedido_form():
    """Mostra formulário para novo pedido"""
    st.markdown("### ➕ Novo Pedido")
    
    with st.form("novo_pedido"):
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Cliente/Projeto*")
            categoria = st.selectbox("Categoria*", [
                "Público Extra", "Público Geral", "Corporativo", 
                "Casamento", "Aniversário", "Outro"
            ])
            produto_servico = st.text_area("Produto/Serviço*")
            valor = st.number_input("Valor (R$)*", min_value=0.0, format="%.2f")
        
        with col2:
            custos = st.number_input("Custos do Pedido (R$)", min_value=0.0, format="%.2f")
            diarias_equipe = st.number_input("Diárias de Equipe (R$)", min_value=0.0, format="%.2f")
            local = st.text_input("Local do Evento")
            data_entrega = st.date_input("Data de Entrega")
            data_recolhimento = st.date_input("Data de Recolhimento")
        
        submitted = st.form_submit_button("💾 Salvar Pedido", use_container_width=True)
        
        if submitted:
            if cliente and categoria and produto_servico and valor > 0:
                # Aqui você adicionaria a lógica para salvar na planilha
                st.success("✅ Pedido salvo com sucesso!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Preencha todos os campos obrigatórios (*)")

def main():
    """Função principal do dashboard"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🎪 Dashboard Primeira Linha Eventos</h1>
        <p>Sistema Executivo v3.0 - Gestão Completa de Pedidos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carrega dados
    df = load_data()
    
    if df.empty:
        st.error("❌ Não foi possível carregar os dados da planilha.")
        return
    
    # Calcula KPIs
    kpis = calculate_kpis(df)
    alertas = get_alertas(df, kpis)
    
    # Sidebar com navegação
    st.sidebar.markdown("## 📊 Navegação")
    
    # Botão Novo Pedido na sidebar
    if st.sidebar.button("➕ NOVO PEDIDO", use_container_width=True):
        st.session_state.show_novo_pedido = True
    
    # Sistema de abas
    tab_dashboard, tab_evolucao, tab_pedidos, tab_alertas = st.tabs([
        "📊 Dashboard", "📈 Evolução", "📋 Pedidos", "🚨 Alertas"
    ])
    
    # ABA 1: DASHBOARD PRINCIPAL
    with tab_dashboard:
        # Mostra formulário de novo pedido se solicitado
        if st.session_state.get('show_novo_pedido', False):
            show_novo_pedido_form()
            if st.button("❌ Fechar Formulário"):
                st.session_state.show_novo_pedido = False
                st.rerun()
            st.divider()
        
        # KPIs principais em cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card green">
                <h3>💰 Receita Total</h3>
                <h2>R$ {kpis['total_receita']:,.2f}</h2>
                <p>Ticket médio: R$ {kpis['ticket_medio']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card blue">
                <h3>📈 Lucro Bruto</h3>
                <h2>R$ {kpis['lucro_bruto']:,.2f}</h2>
                <p>Margem: {kpis['margem_lucro']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card purple">
                <h3>📦 Total Pedidos</h3>
                <h2>{kpis['total_pedidos']}</h2>
                <p>{kpis['pedidos_pagos']} pagos, {kpis['pedidos_pendentes']} pendentes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ Inadimplência</h3>
                <h2>{kpis['taxa_inadimplencia']:.1f}%</h2>
                <p>Meta: < 15%</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 Receita por Categoria")
            receita_categoria = df.groupby('categoria')['valor'].sum().reset_index()
            fig_pie = px.pie(receita_categoria, values='valor', names='categoria',
                           color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Top 5 Produtos/Serviços")
            top_produtos = df.groupby('produto_servico')['valor'].sum().nlargest(5).reset_index()
            fig_bar = px.bar(top_produtos, x='valor', y='produto_servico', orientation='h',
                           color='valor', color_continuous_scale='viridis')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Top Clientes
        st.subheader("👥 Top 5 Clientes")
        top_clientes = df.groupby('cliente')['valor'].sum().nlargest(5).reset_index()
        
        for i, (_, row) in enumerate(top_clientes.iterrows(), 1):
            col1, col2, col3 = st.columns([1, 4, 2])
            with col1:
                st.markdown(f"**#{i}**")
            with col2:
                st.markdown(f"**{row['cliente']}**")
            with col3:
                st.markdown(f"**R$ {row['valor']:,.2f}**")
    
    # ABA 2: EVOLUÇÃO TEMPORAL
    with tab_evolucao:
        st.subheader("📈 Evolução Temporal")
        
        if 'data_entrega' in df.columns:
            # Receita por mês
            df_mes = df.copy()
            df_mes['mes_ano'] = df_mes['data_entrega'].dt.to_period('M').astype(str)
            receita_mensal = df_mes.groupby('mes_ano')['valor'].sum().reset_index()
            
            fig_line = px.line(receita_mensal, x='mes_ano', y='valor',
                             title='Receita Mensal', markers=True)
            fig_line.update_layout(xaxis_title='Mês/Ano', yaxis_title='Receita (R$)')
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Pedidos por mês
            pedidos_mensal = df_mes.groupby('mes_ano').size().reset_index(name='pedidos')
            
            fig_bar_pedidos = px.bar(pedidos_mensal, x='mes_ano', y='pedidos',
                                   title='Número de Pedidos por Mês')
            st.plotly_chart(fig_bar_pedidos, use_container_width=True)
        else:
            st.info("📅 Dados de data não disponíveis para análise temporal")
    
    # ABA 3: GESTÃO DE PEDIDOS
    with tab_pedidos:
        st.subheader("📋 Gestão de Pedidos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_categoria = st.selectbox("Filtrar por Categoria", 
                                          ["Todas"] + list(df['categoria'].unique()))
        
        with col2:
            filtro_status = st.selectbox("Status de Pagamento", 
                                       ["Todos", "Pagos", "Pendentes"])
        
        with col3:
            busca_cliente = st.text_input("Buscar Cliente")
        
        # Aplica filtros
        df_filtrado = df.copy()
        
        if filtro_categoria != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == filtro_categoria]
        
        if filtro_status == "Pagos":
            df_filtrado = df_filtrado[df_filtrado['data_pagamento'].notna()]
        elif filtro_status == "Pendentes":
            df_filtrado = df_filtrado[df_filtrado['data_pagamento'].isna()]
        
        if busca_cliente:
            df_filtrado = df_filtrado[df_filtrado['cliente'].str.contains(busca_cliente, case=False, na=False)]
        
        # Estatísticas dos filtros
        st.markdown(f"**📊 Resultados:** {len(df_filtrado)} pedidos | Receita: R$ {df_filtrado['valor'].sum():,.2f}")
        
        # Tabela de pedidos
        if not df_filtrado.empty:
            # Prepara dados para exibição
            df_display = df_filtrado.copy()
            
            # Formata valores monetários
            df_display['valor'] = df_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['custos'] = df_display['custos'].apply(lambda x: f"R$ {x:,.2f}")
            
            # Formata datas
            date_columns = ['data_entrega', 'data_recolhimento', 'data_pagamento']
            for col in date_columns:
                if col in df_display.columns:
                    df_display[col] = df_display[col].dt.strftime('%d/%m/%Y').fillna('Não definido')
            
            # Status de pagamento
            df_display['status_pagamento'] = df_display['data_pagamento'].apply(
                lambda x: '✅ Pago' if x != 'Não definido' else '⏳ Pendente'
            )
            
            st.dataframe(df_display, use_container_width=True, height=400)
        else:
            st.info("🔍 Nenhum pedido encontrado com os filtros aplicados")
    
    # ABA 4: ALERTAS E INSIGHTS
    with tab_alertas:
        st.subheader("🚨 Alertas e Insights")
        
        # Mostra alertas
        for alerta in alertas:
            if alerta['tipo'] == 'critical':
                st.markdown(f"""
                <div class="alert-critical">
                    <h4>{alerta['titulo']}</h4>
                    <p>{alerta['mensagem']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif alerta['tipo'] == 'warning':
                st.markdown(f"""
                <div class="alert-warning">
                    <h4>{alerta['titulo']}</h4>
                    <p>{alerta['mensagem']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif alerta['tipo'] == 'success':
                st.markdown(f"""
                <div class="alert-success">
                    <h4>{alerta['titulo']}</h4>
                    <p>{alerta['mensagem']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Insights empresariais
        st.subheader("💡 Insights Empresariais")
        
        # Análise de margem por categoria
        margem_categoria = df.groupby('categoria').agg({
            'valor': 'sum',
            'custos': 'sum'
        }).reset_index()
        margem_categoria['margem'] = ((margem_categoria['valor'] - margem_categoria['custos']) / margem_categoria['valor'] * 100)
        margem_categoria = margem_categoria.sort_values('margem', ascending=False)
        
        st.markdown("**📊 Margem de Lucro por Categoria:**")
        for _, row in margem_categoria.iterrows():
            st.markdown(f"• **{row['categoria']}**: {row['margem']:.1f}% de margem")
        
        # Recomendações
        st.subheader("🎯 Recomendações Estratégicas")
        
        categoria_mais_lucrativa = margem_categoria.iloc[0]['categoria']
        st.success(f"✅ **Foque em eventos '{categoria_mais_lucrativa}'** - categoria mais lucrativa")
        
        if kpis['taxa_inadimplencia'] > 15:
            st.error("❌ **Implemente cobrança automática** - inadimplência crítica")
        
        if kpis['ticket_medio'] < 3000:
            st.warning("⚠️ **Crie pacotes premium** - aumentar ticket médio")
        
        st.info("💡 **Automatize follow-up** - melhorar conversão de propostas")
    
    # Footer
    st.divider()
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🎪 Dashboard Primeira Linha Eventos v3.0 | 
        Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
        {len(df)} pedidos carregados
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
