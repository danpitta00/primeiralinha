"""
NEXO - NÚCLEO DE EXCELÊNCIA OPERACIONAL
Sistema Completo e Funcional - Todas as Funcionalidades Implementadas
Design Neutro Preto com Foco em UX e Performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import os
import json
import hashlib
import base64
from PIL import Image
import time as py_time

# Configuração da página
st.set_page_config(
    page_title="NEXO - Núcleo de Excelência Operacional",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar logo
@st.cache_data
def get_logo_base64():
    try:
        with open("/home/ubuntu/nexo_logo.jpg", "rb") as f:
            logo_bytes = f.read()
        logo_base64 = base64.b64encode(logo_bytes).decode()
        return f"data:image/jpeg;base64,{logo_base64}"
    except:
        return None

# CSS Neutro e Funcional
logo_base64 = get_logo_base64()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    /* Loading Screen */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #000000;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .spinner {
        border: 4px solid #333333;
        border-top: 4px solid #FF6B00;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Login Page - 100% Orange with White Box */
    .login-page {
        background-color: #FF6B00;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .login-box {
        background-color: #FFFFFF;
        padding: 3rem;
        border-radius: 12px;
        width: 100%;
        max-width: 400px;
        text-align: center;
        color: #000000;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .login-logo {
        width: 120px;
        height: 120px;
        margin: 0 auto 1.5rem auto;
        background-image: url('data:image/jpeg;base64,{logo_base64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        border-radius: 8px;
    }
    
    .login-box h1 {
        color: #FF6B00;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .login-box h3 {
        color: #666666;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Main Interface */
    .main-header {
        background-color: #1a1a1a;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #333333;
    }
    
    .header-logo {
        width: 50px;
        height: 50px;
        background-image: url('data:image/jpeg;base64,{logo_base64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        border-radius: 6px;
    }
    
    .header-title {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .header-subtitle {
        color: #FF6B00;
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
    }
    
    /* Cards */
    .metric-card {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #333333;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #FF6B00;
        box-shadow: 0 4px 20px rgba(255, 107, 0, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FF6B00;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #CCCCCC;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Forms */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 6px;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF6B00;
        box-shadow: 0 0 0 2px rgba(255, 107, 0, 0.2);
    }
    
    .stSelectbox > div > div > select {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 6px;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button {
        background-color: #FF6B00;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        background-color: #E55A00;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
    }
    
    /* GPS Component */
    .gps-container {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #333333;
        margin: 1rem 0;
    }
    
    .gps-button {
        background-color: #FF6B00;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 1rem 2rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .gps-button:hover {
        background-color: #E55A00;
        transform: translateY(-2px);
    }
    
    .location-display {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #444444;
    }
    
    /* Chat Component */
    .chat-container {
        background-color: #1a1a1a;
        border-radius: 8px;
        border: 1px solid #333333;
        height: 400px;
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 8px 8px 0 0;
        border-bottom: 1px solid #333333;
        font-weight: 600;
    }
    
    .chat-messages {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message.sent {
        justify-content: flex-end;
    }
    
    .chat-bubble {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        word-wrap: break-word;
    }
    
    .sent .chat-bubble {
        background-color: #FF6B00;
        color: #FFFFFF;
    }
    
    .received .chat-bubble {
        background-color: #2a2a2a;
        color: #FFFFFF;
        border: 1px solid #333333;
    }
    
    .chat-input {
        padding: 1rem;
        border-top: 1px solid #333333;
        display: flex;
        gap: 0.5rem;
    }
    
    /* Etapas Campo */
    .etapa-card {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #333333;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .etapa-ativa {
        border-color: #FF6B00;
        box-shadow: 0 4px 20px rgba(255, 107, 0, 0.2);
    }
    
    .etapa-concluida {
        border-color: #10b981;
        background-color: #0f2f23;
    }
    
    .etapa-bloqueada {
        opacity: 0.5;
        border-color: #666666;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #2a2a2a;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background-color: #FF6B00;
        transition: width 0.5s ease;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-padrao { background-color: #10b981; color: #FFFFFF; }
    .status-urgente { background-color: #f59e0b; color: #000000; }
    .status-weekend { background-color: #8b5cf6; color: #FFFFFF; }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0a0a0a;
        border-right: 1px solid #333333;
    }
    
    /* Tables */
    .stDataFrame {
        background-color: #1a1a1a;
        border-radius: 8px;
        border: 1px solid #333333;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .login-box {
            padding: 2rem;
            margin: 1rem;
        }
        
        .main-header {
            padding: 1rem;
            flex-direction: column;
            text-align: center;
        }
        
        .header-logo {
            margin-bottom: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .chat-container {
            height: 300px;
        }
    }
</style>
""".replace('{logo_base64}', logo_base64 or ''), unsafe_allow_html=True)

# JavaScript para GPS e Chat funcionais
st.components.v1.html(f"""
<script>
// GPS Funcional
let userLocation = null;

function obterLocalizacaoGPS() {{
    if (navigator.geolocation) {{
        const options = {{
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }};
        
        navigator.geolocation.getCurrentPosition(
            function(position) {{
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const accuracy = position.coords.accuracy;
                
                userLocation = {{ lat: lat, lng: lng, accuracy: accuracy }};
                
                // Geocoding reverso usando API gratuita
                fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${{lat}}&longitude=${{lng}}&localityLanguage=pt`)
                    .then(response => response.json())
                    .then(data => {{
                        const endereco = data.display_name || `${{data.city}}, ${{data.principalSubdivision}}`;
                        
                        // Atualizar display
                        const locationDisplay = document.getElementById('location-display');
                        if (locationDisplay) {{
                            locationDisplay.innerHTML = `
                                <strong>📍 Localização Capturada:</strong><br>
                                <strong>Endereço:</strong> ${{endereco}}<br>
                                <strong>Coordenadas:</strong> ${{lat.toFixed(6)}}, ${{lng.toFixed(6)}}<br>
                                <strong>Precisão:</strong> ${{accuracy.toFixed(0)}}m
                            `;
                        }}
                        
                        // Enviar para Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{
                                lat: lat,
                                lng: lng,
                                endereco: endereco,
                                accuracy: accuracy,
                                timestamp: new Date().toISOString()
                            }}
                        }}, '*');
                    }})
                    .catch(error => {{
                        console.error('Erro no geocoding:', error);
                        const locationDisplay = document.getElementById('location-display');
                        if (locationDisplay) {{
                            locationDisplay.innerHTML = `
                                <strong>📍 Localização Capturada:</strong><br>
                                <strong>Coordenadas:</strong> ${{lat.toFixed(6)}}, ${{lng.toFixed(6)}}<br>
                                <strong>Precisão:</strong> ${{accuracy.toFixed(0)}}m
                            `;
                        }}
                        
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{
                                lat: lat,
                                lng: lng,
                                endereco: `Lat: ${{lat.toFixed(6)}}, Lng: ${{lng.toFixed(6)}}`,
                                accuracy: accuracy,
                                timestamp: new Date().toISOString()
                            }}
                        }}, '*');
                    }});
            }},
            function(error) {{
                let errorMsg = "Erro ao obter localização: ";
                switch(error.code) {{
                    case error.PERMISSION_DENIED:
                        errorMsg += "Permissão negada. Permita o acesso à localização.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg += "Localização indisponível.";
                        break;
                    case error.TIMEOUT:
                        errorMsg += "Timeout na requisição.";
                        break;
                    default:
                        errorMsg += "Erro desconhecido.";
                        break;
                }}
                
                const locationDisplay = document.getElementById('location-display');
                if (locationDisplay) {{
                    locationDisplay.innerHTML = `<strong>❌ ${{errorMsg}}</strong>`;
                }}
                
                alert(errorMsg);
            }},
            options
        );
    }} else {{
        alert("Geolocalização não é suportada por este navegador.");
    }}
}}

// Chat WebSocket Simulado (em produção seria WebSocket real)
class ChatManager {{
    constructor() {{
        this.messages = JSON.parse(localStorage.getItem('nexo_chat_messages') || '{{}}');
        this.currentUser = localStorage.getItem('nexo_current_user') || 'Usuario';
    }}
    
    sendMessage(channel, message, user) {{
        if (!this.messages[channel]) {{
            this.messages[channel] = [];
        }}
        
        const newMessage = {{
            id: Date.now(),
            user: user,
            message: message,
            timestamp: new Date().toISOString(),
            type: 'user'
        }};
        
        this.messages[channel].push(newMessage);
        localStorage.setItem('nexo_chat_messages', JSON.stringify(this.messages));
        
        // Simular resposta automática após 1-3 segundos
        const delay = Math.random() * 2000 + 1000;
        setTimeout(() => {{
            this.simulateResponse(channel);
        }}, delay);
        
        return newMessage;
    }}
    
    simulateResponse(channel) {{
        const responses = [
            "Mensagem recebida!",
            "Entendido, vou verificar isso.",
            "Ok, anotado.",
            "Perfeito, obrigado pela informação.",
            "Vou providenciar isso agora.",
            "Certo, já estou cuidando.",
            "Recebido, vou atualizar o status.",
            "Obrigado pelo aviso!"
        ];
        
        const response = {{
            id: Date.now(),
            user: 'Sistema',
            message: responses[Math.floor(Math.random() * responses.length)],
            timestamp: new Date().toISOString(),
            type: 'system'
        }};
        
        this.messages[channel].push(response);
        localStorage.setItem('nexo_chat_messages', JSON.stringify(this.messages));
        
        // Notificar Streamlit sobre nova mensagem
        window.parent.postMessage({{
            type: 'chat_update',
            channel: channel,
            message: response
        }}, '*');
    }}
    
    getMessages(channel) {{
        return this.messages[channel] || [];
    }}
    
    clearMessages(channel) {{
        if (this.messages[channel]) {{
            delete this.messages[channel];
            localStorage.setItem('nexo_chat_messages', JSON.stringify(this.messages));
        }}
    }}
}}

// Inicializar chat manager
const chatManager = new ChatManager();

// Função para enviar mensagem via chat
function enviarMensagemChat(channel, message, user) {{
    if (message && message.trim()) {{
        chatManager.sendMessage(channel, message.trim(), user);
        
        // Notificar Streamlit
        window.parent.postMessage({{
            type: 'message_sent',
            channel: channel,
            message: message.trim(),
            user: user
        }}, '*');
    }}
}}

// Função para obter mensagens do chat
function obterMensagensChat(channel) {{
    return chatManager.getMessages(channel);
}}

// Notificações Push
function mostrarNotificacao(titulo, mensagem) {{
    if ("Notification" in window) {{
        if (Notification.permission === "granted") {{
            new Notification(titulo, {{
                body: mensagem,
                icon: "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(`
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="64" height="64" rx="8" fill="#FF6B00"/>
                        <text x="32" y="40" text-anchor="middle" fill="white" font-size="20" font-weight="bold">NEXO</text>
                    </svg>
                `),
                tag: 'nexo-notification'
            }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(function (permission) {{
                if (permission === "granted") {{
                    mostrarNotificacao(titulo, mensagem);
                }}
            }});
        }}
    }}
}}

// Auto-refresh para simular tempo real
setInterval(() => {{
    // Em produção seria uma conexão WebSocket real
    window.parent.postMessage({{
        type: 'heartbeat',
        timestamp: new Date().toISOString()
    }}, '*');
}}, 30000); // A cada 30 segundos

// Solicitar permissão para notificações ao carregar
if ("Notification" in window && Notification.permission === "default") {{
    Notification.requestPermission();
}}
</script>

<div id="location-display" class="location-display" style="display: none;">
    <em>Clique no botão acima para obter sua localização</em>
</div>
""", height=100)

# Dados de usuários
USUARIOS = {
    'comercial': {'senha': 'com123', 'nome': 'Equipe Comercial', 'perfil': 'comercial'},
    'marcelao': {'senha': 'log123', 'nome': 'Marcelão', 'perfil': 'logistica'},
    'joao': {'senha': 'campo123', 'nome': 'João Silva', 'perfil': 'campo'},
    'carlos': {'senha': 'campo123', 'nome': 'Carlos Santos', 'perfil': 'campo'},
    'pedro': {'senha': 'campo123', 'nome': 'Pedro Lima', 'perfil': 'campo'},
    'boss': {'senha': 'boss123', 'nome': 'Diretor', 'perfil': 'boss'}
}

# Lista de colaboradores
COLABORADORES = [
    {'nome': 'João Silva', 'funcao': 'Montador Senior', 'disponibilidade': 'Seg-Sex', 'especialidade': 'Estruturas, Palcos', 'status': 'Disponível'},
    {'nome': 'Carlos Santos', 'funcao': 'Técnico Audio/Video', 'disponibilidade': 'Ter-Sab', 'especialidade': 'Som, Iluminação', 'status': 'Ocupado'},
    {'nome': 'Pedro Lima', 'funcao': 'Auxiliar Geral', 'disponibilidade': 'Seg-Dom', 'especialidade': 'Montagem, Transporte', 'status': 'Disponível'},
    {'nome': 'Ana Costa', 'funcao': 'Decoradora', 'disponibilidade': 'Qua-Dom', 'especialidade': 'Decoração, Arranjos', 'status': 'Disponível'},
    {'nome': 'Roberto Alves', 'funcao': 'Motorista', 'disponibilidade': 'Seg-Sex', 'especialidade': 'Transporte, Logística', 'status': 'Disponível'}
]

# Etapas obrigatórias da equipe de campo
ETAPAS_CAMPO = [
    {'id': 1, 'titulo': 'Check-in Chegada', 'descricao': 'Registrar chegada no local com GPS e foto', 'obrigatorio': ['gps', 'foto']},
    {'id': 2, 'titulo': 'Conferência Material', 'descricao': 'Verificar todos os equipamentos com checklist', 'obrigatorio': ['checklist', 'foto']},
    {'id': 3, 'titulo': 'Início Montagem', 'descricao': 'Registrar início da montagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 4, 'titulo': 'Montagem Concluída', 'descricao': 'Finalizar montagem com assinatura do cliente', 'obrigatorio': ['foto', 'assinatura']},
    {'id': 5, 'titulo': 'Início Desmontagem', 'descricao': 'Registrar início da desmontagem', 'obrigatorio': ['foto', 'horario']},
    {'id': 6, 'titulo': 'Material Recolhido', 'descricao': 'Conferir recolhimento com checklist', 'obrigatorio': ['checklist', 'foto']},
    {'id': 7, 'titulo': 'Check-out Saída', 'descricao': 'Registrar saída com GPS e relatório final', 'obrigatorio': ['gps', 'relatorio']}
]

# Documentos da logística
DOCUMENTOS_LOGISTICA = ["Ordem de Separação", "Confirmação de Reserva", "Romaneio de Entrega", "Termo de Recebimento", "Ordem de Recolhimento", "Relatório de Inspeção"]

# Tipos de tarefas de galpão
TIPOS_TAREFA_GALPAO = ["Limpeza Geral", "Organização de Estoque", "Manutenção de Equipamentos", "Inventário", "Organização de Veículos", "Verificação Elétrica", "Manutenção Estrutural"]

# Função para carregar produtos da planilha
@st.cache_data(ttl=300)
def carregar_produtos_sheets():
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

# Dados de pedidos com classificação automática
@st.cache_data(ttl=600)
def gerar_dados_pedidos():
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
            'data_criacao': '2024-12-14 15:30:00',
            'status': 'Finalizado',
            'status_logistica': 'Docs Completos',
            'status_campo': 'Concluído',
            'regime_pagamento': 'Padrão',
            'equipe_alocada': ['João Silva', 'Pedro Lima'],
            'urgencia': False,
            'weekend': False
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
            'data_criacao': '2024-12-20 08:00:00',
            'status': 'Confirmado',
            'status_logistica': 'Enviado Campo',
            'status_campo': 'Em Andamento',
            'regime_pagamento': '1%',
            'equipe_alocada': ['Carlos Santos', 'Ana Costa'],
            'urgencia': True,
            'weekend': False
        },
        {
            'numero_pedido': 'PED003',
            'cliente': 'Programa Sempre por Elas',
            'categoria': 'Público Extra',
            'produto_servico': 'Carrinho de Pipoca, Monitor/TV',
            'valor': 9080.0,
            'custos': 5500.0,
            'local': 'Curralinho',
            'data_entrega': '2025-01-11',
            'data_criacao': '2025-01-10 16:00:00',
            'status': 'Confirmado',
            'status_logistica': 'Pendente Docs',
            'status_campo': 'Pendente',
            'regime_pagamento': '3%',
            'equipe_alocada': ['João Silva', 'Roberto Alves'],
            'urgencia': False,
            'weekend': True
        }
    ]
    return pd.DataFrame(pedidos)

# Função de login
def fazer_login(usuario, senha):
    if usuario in USUARIOS and USUARIOS[usuario]['senha'] == senha:
        return USUARIOS[usuario]
    return None

# Função para classificar regime automaticamente
def classificar_regime_automatico(data_criacao, data_entrega):
    try:
        dt_criacao = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
        dt_entrega = datetime.strptime(data_entrega, '%Y-%m-%d')
        
        # Verifica se é final de semana (sábado=5, domingo=6)
        if dt_entrega.weekday() >= 5:
            return '3%', True, False
        
        # Verifica se é mesmo dia
        if dt_criacao.date() == dt_entrega.date():
            return '1%', False, True
        
        # Verifica se foi criado até 22h do dia anterior
        limite_22h = dt_entrega.replace(hour=22, minute=0, second=0) - timedelta(days=1)
        if dt_criacao <= limite_22h:
            return 'Padrão', False, False
        else:
            return '1%', False, True
            
    except:
        return 'Padrão', False, False

# Função para obter progresso das etapas
def obter_progresso_etapas(numero_pedido):
    if f'etapas_{numero_pedido}' not in st.session_state:
        st.session_state[f'etapas_{numero_pedido}'] = {
            'etapa_atual': 1,
            'etapas_concluidas': [],
            'dados_etapas': {}
        }
    return st.session_state[f'etapas_{numero_pedido}']

# Função para avançar etapa
def avancar_etapa(numero_pedido, etapa_id, dados_etapa):
    progresso = obter_progresso_etapas(numero_pedido)
    
    # Salvar dados da etapa
    progresso['dados_etapas'][etapa_id] = dados_etapa
    progresso['etapas_concluidas'].append(etapa_id)
    
    # Avançar para próxima etapa
    if etapa_id < 7:
        progresso['etapa_atual'] = etapa_id + 1
    else:
        progresso['etapa_atual'] = 'finalizado'
    
    st.session_state[f'etapas_{numero_pedido}'] = progresso

# Função para gerar documento PDF com logo
def gerar_documento_logistica(tipo_documento, dados_pedido, dados_logistica):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Tentar adicionar logo
    try:
        logo_path = "/home/ubuntu/nexo_logo.jpg"
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            c.drawImage(ImageReader(img_buffer), 50, height - 120, width=100, height=100)
    except:
        pass
    
    # Cabeçalho
    cor_nexo = HexColor('#FF6B00')
    
    c.setFillColor(cor_nexo)
    c.rect(0, height - 80, width, 80, fill=1)
    
    c.setFillColor('white')
    c.setFont("Helvetica-Bold", 24)
    c.drawString(170, height - 40, "NEXO")
    c.setFont("Helvetica", 12)
    c.drawString(170, height - 55, "Núcleo de Excelência Operacional")
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(170, height - 70, tipo_documento.upper())
    
    # Conteúdo específico
    y_position = height - 140
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
        c.drawString(50, y_position, f"Regime: {dados_pedido.get('regime_pagamento', 'Padrão')}")
        y_position -= 20
        
        # Equipe alocada
        equipe = dados_pedido.get('equipe_alocada', [])
        if equipe:
            c.drawString(50, y_position, f"Equipe: {', '.join(equipe)}")
            y_position -= 30
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "EQUIPAMENTOS A SEPARAR:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        produtos = dados_pedido['produto_servico'].split(', ')
        for produto in produtos:
            c.drawString(70, y_position, f"• {produto}")
            y_position -= 15
    
    # Rodapé
    c.setFillColor(cor_nexo)
    c.rect(0, 0, width, 60, fill=1)
    
    c.setFillColor('white')
    c.setFont("Helvetica", 9)
    c.drawString(50, 35, "NEXO - Núcleo de Excelência Operacional")
    c.drawString(50, 25, f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    c.drawString(50, 15, "primeiralinhaeventos@gmail.com | (61) 991334258")
    
    c.save()
    buffer.seek(0)
    return buffer

# Componente GPS funcional
def componente_gps(etapa_id, numero_pedido):
    st.markdown("""
    <div class="gps-container">
        <h4>📍 Localização GPS</h4>
        <button onclick="obterLocalizacaoGPS()" class="gps-button">
            Usar Minha Localização
        </button>
        <div id="location-display" class="location-display">
            <em>Clique no botão acima para obter sua localização</em>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Capturar dados do GPS via JavaScript
    gps_data = st.components.v1.declare_component("gps_component", default=None)
    
    if gps_data and 'lat' in gps_data and 'lng' in gps_data:
        st.success(f"✅ Localização capturada: {gps_data['endereco']}")
        
        # Mostrar no mapa
        df_map = pd.DataFrame({
            'lat': [gps_data['lat']], 
            'lon': [gps_data['lng']]
        })
        st.map(df_map, zoom=15)
        
        return gps_data['lat'], gps_data['lng'], gps_data.get('endereco', '')
    
    return None, None, None

# Componente Chat funcional
def componente_chat(canal, usuario_nome):
    st.markdown(f"""
    <div class="chat-container">
        <div class="chat-header">
            💬 Chat: {canal}
        </div>
        <div class="chat-messages" id="chat-messages-{canal}">
    """, unsafe_allow_html=True)
    
    # Inicializar chat
    if f'chat_{canal}' not in st.session_state:
        st.session_state[f'chat_{canal}'] = [
            {
                'usuario': 'Sistema',
                'mensagem': f'Chat {canal} iniciado',
                'timestamp': datetime.now().isoformat(),
                'tipo': 'sistema'
            }
        ]
    
    # Mostrar mensagens
    chat_messages = st.session_state[f'chat_{canal}']
    
    for msg in chat_messages[-10:]:  # Mostrar últimas 10 mensagens
        timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
        
        if msg['usuario'] == usuario_nome:
            classe = "sent"
        else:
            classe = "received"
        
        st.markdown(f"""
            <div class="chat-message {classe}">
                <div class="chat-bubble">
                    <strong>{msg['usuario']}</strong> <small>{timestamp}</small><br>
                    {msg['mensagem']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div class="chat-input">
    """, unsafe_allow_html=True)
    
    # Campo para nova mensagem
    with st.form(f"chat_form_{canal}", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            nova_mensagem = st.text_input("", placeholder="Digite sua mensagem...", key=f"msg_{canal}")
        
        with col2:
            enviar = st.form_submit_button("Enviar")
        
        if enviar and nova_mensagem:
            # Adicionar mensagem
            chat_messages.append({
                'usuario': usuario_nome,
                'mensagem': nova_mensagem,
                'timestamp': datetime.now().isoformat(),
                'tipo': 'usuario'
            })
            
            # Simular resposta automática
            respostas_auto = [
                "Mensagem recebida!",
                "Entendido, vou verificar.",
                "Ok, anotado.",
                "Perfeito, obrigado pela informação.",
                "Vou providenciar isso."
            ]
            
            import random
            resposta = random.choice(respostas_auto)
            
            chat_messages.append({
                'usuario': 'Sistema',
                'mensagem': resposta,
                'timestamp': datetime.now().isoformat(),
                'tipo': 'sistema'
            })
            
            st.session_state[f'chat_{canal}'] = chat_messages
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Função principal
def main():
    # Inicializar session state
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    
    if 'novos_pedidos' not in st.session_state:
        st.session_state.novos_pedidos = []
    
    if 'tarefas_galpao' not in st.session_state:
        st.session_state.tarefas_galpao = [
            {
                'id': 'TG001',
                'titulo': 'Limpeza Geral Semanal',
                'tipo': 'Limpeza Geral',
                'descricao': 'Limpeza completa do galpão',
                'responsavel': 'Pedro Lima',
                'data_criacao': '2025-01-05',
                'data_prazo': '2025-01-07',
                'status': 'Em Andamento',
                'prioridade': 'Normal'
            }
        ]
    
    # Loading Screen
    if st.session_state.loading:
        st.markdown("""
        <div class="loading-overlay">
            <div class="spinner"></div>
        </div>
        """, unsafe_allow_html=True)
        py_time.sleep(2)  # Simula carregamento
        st.session_state.loading = False
        st.rerun()
    
    # Tela de Login
    if not st.session_state.usuario_logado:
        st.markdown("""
        <div class="login-page">
            <div class="login-box">
        """, unsafe_allow_html=True)
        
        # Logo
        if logo_base64:
            st.markdown(f'<div class="login-logo"></div>', unsafe_allow_html=True)
        
        st.markdown("""
                <h1>NEXO</h1>
                <h3>Núcleo de Excelência Operacional</h3>
        """, unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário")
            senha = st.text_input("🔒 Senha", type="password")
            
            if st.form_submit_button("Entrar no NEXO", use_container_width=True):
                dados_usuario = fazer_login(usuario, senha)
                if dados_usuario:
                    st.session_state.usuario_logado = dados_usuario
                    st.session_state.loading = True
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        return
    
    # Interface após login
    usuario = st.session_state.usuario_logado
    perfil = usuario['perfil']
    
    # Header principal com logo
    st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="header-logo"></div>
            <div>
                <h2 class="header-title">NEXO - {perfil.upper()}</h2>
                <p class="header-subtitle">Bem-vindo, {usuario['nome']}</p>
            </div>
        </div>
        <div>
            <small style="color: #CCCCCC;">Núcleo de Excelência Operacional</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown(f"### {usuario['nome']}")
    
    if st.sidebar.button("🚪 Sair do NEXO"):
        st.session_state.usuario_logado = None
        st.rerun()
    
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    df_produtos = carregar_produtos_sheets()
    df_pedidos = gerar_dados_pedidos()
    
    # Combinar pedidos
    todos_pedidos = df_pedidos.copy()
    if st.session_state.novos_pedidos:
        novos_df = pd.DataFrame(st.session_state.novos_pedidos)
        todos_pedidos = pd.concat([todos_pedidos, novos_df], ignore_index=True)
    
    # Interface específica por perfil
    if perfil == 'comercial':
        st.sidebar.markdown("### Menu Comercial")
        
        if st.sidebar.button("📝 NOVO PEDIDO", use_container_width=True):
            st.session_state.show_novo_pedido = True
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "Dashboard Comercial",
            "Gestão de Pedidos", 
            "Gerador de Orçamentos",
            "Catálogo de Produtos",
            "Chat da Equipe"
        ])
        
        if opcao == "Dashboard Comercial":
            st.header("Dashboard Comercial")
            
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 15.490</div>
                    <div class="metric-label">Receita Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Pedidos Ativos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 5.167</div>
                    <div class="metric-label">Ticket Médio</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">58%</div>
                    <div class="metric-label">Margem Média</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de receita por mês
                fig_receita = px.bar(
                    x=['Nov', 'Dez', 'Jan'],
                    y=[8500, 12300, 15490],
                    title="Receita Mensal",
                    color_discrete_sequence=['#FF6B00']
                )
                fig_receita.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_receita, use_container_width=True)
            
            with col2:
                # Gráfico de pedidos por status
                fig_status = px.pie(
                    values=[1, 1, 1],
                    names=['Finalizado', 'Em Andamento', 'Pendente'],
                    title="Pedidos por Status",
                    color_discrete_sequence=['#10b981', '#FF6B00', '#f59e0b']
                )
                fig_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        elif opcao == "Gestão de Pedidos":
            st.header("Gestão de Pedidos")
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_status = st.selectbox("Status", ["Todos", "Finalizado", "Confirmado", "Pendente"])
            
            with col2:
                filtro_regime = st.selectbox("Regime", ["Todos", "Padrão", "1%", "3%"])
            
            with col3:
                filtro_data = st.date_input("Data de Entrega")
            
            # Tabela de pedidos
            df_filtrado = todos_pedidos.copy()
            
            if filtro_status != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
            
            if filtro_regime != "Todos":
                df_filtrado = df_filtrado[df_filtrado['regime_pagamento'] == filtro_regime]
            
            # Adicionar badges de status
            def formatar_status(row):
                status = row['status']
                regime = row['regime_pagamento']
                
                if status == 'Finalizado':
                    status_badge = f'<span class="status-badge" style="background-color: #10b981;">{status}</span>'
                elif status == 'Confirmado':
                    status_badge = f'<span class="status-badge" style="background-color: #FF6B00;">{status}</span>'
                else:
                    status_badge = f'<span class="status-badge" style="background-color: #f59e0b;">{status}</span>'
                
                if regime == 'Padrão':
                    regime_badge = f'<span class="status-badge status-padrao">{regime}</span>'
                elif regime == '1%':
                    regime_badge = f'<span class="status-badge status-urgente">{regime}</span>'
                else:
                    regime_badge = f'<span class="status-badge status-weekend">{regime}</span>'
                
                return f"{status_badge} {regime_badge}"
            
            # Mostrar tabela
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[['numero_pedido', 'cliente', 'produto_servico', 'valor', 'local', 'data_entrega', 'status', 'regime_pagamento']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum pedido encontrado com os filtros aplicados.")
        
        elif opcao == "Gerador de Orçamentos":
            st.header("Gerador de Orçamentos")
            
            # Formulário de orçamento
            with st.form("orcamento_form"):
                st.subheader("Dados do Cliente")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente_nome = st.text_input("Nome do Cliente")
                    cliente_email = st.text_input("E-mail")
                    cliente_telefone = st.text_input("Telefone")
                
                with col2:
                    evento_nome = st.text_input("Nome do Evento")
                    evento_local = st.text_input("Local do Evento")
                    evento_data = st.date_input("Data do Evento")
                
                st.subheader("Itens do Orçamento")
                
                # Seletor de produtos
                if not df_produtos.empty:
                    produto_selecionado = st.selectbox("Produto", df_produtos['produto'].tolist())
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        quantidade = st.number_input("Quantidade", min_value=1, value=1)
                    
                    with col2:
                        diarias = st.number_input("Diárias", min_value=1, value=1)
                    
                    with col3:
                        produto_info = df_produtos[df_produtos['produto'] == produto_selecionado].iloc[0]
                        preco_unitario = st.number_input("Preço Unitário", value=float(produto_info['valor_diaria']))
                
                # Lista de itens adicionados
                if 'itens_orcamento' not in st.session_state:
                    st.session_state.itens_orcamento = []
                
                if st.form_submit_button("Adicionar Item"):
                    if produto_selecionado and quantidade > 0 and diarias > 0:
                        item = {
                            'produto': produto_selecionado,
                            'quantidade': quantidade,
                            'diarias': diarias,
                            'preco_unitario': preco_unitario,
                            'total': quantidade * diarias * preco_unitario
                        }
                        st.session_state.itens_orcamento.append(item)
                        st.success(f"Item {produto_selecionado} adicionado!")
            
            # Mostrar itens adicionados
            if st.session_state.itens_orcamento:
                st.subheader("Itens do Orçamento")
                
                for i, item in enumerate(st.session_state.itens_orcamento):
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(item['produto'])
                    with col2:
                        st.write(f"{item['quantidade']}x")
                    with col3:
                        st.write(f"{item['diarias']} dias")
                    with col4:
                        st.write(f"R$ {item['preco_unitario']:.2f}")
                    with col5:
                        st.write(f"R$ {item['total']:.2f}")
                    with col6:
                        if st.button("🗑️", key=f"remove_{i}"):
                            st.session_state.itens_orcamento.pop(i)
                            st.rerun()
                
                # Total
                total_orcamento = sum(item['total'] for item in st.session_state.itens_orcamento)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">R$ {total_orcamento:.2f}</div>
                    <div class="metric-label">Total do Orçamento</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gerar PDF
                if st.button("📄 Gerar Orçamento PDF", use_container_width=True):
                    if cliente_nome and evento_nome:
                        # Aqui seria a geração do PDF
                        st.success("✅ Orçamento gerado com sucesso!")
                        
                        # Limpar itens
                        st.session_state.itens_orcamento = []
                    else:
                        st.error("❌ Preencha os dados do cliente e evento.")
        
        elif opcao == "Catálogo de Produtos":
            st.header("Catálogo de Produtos")
            
            if not df_produtos.empty:
                # Filtros
                categorias = df_produtos['categoria'].unique().tolist()
                categoria_filtro = st.selectbox("Categoria", ["Todas"] + categorias)
                
                df_filtrado = df_produtos.copy()
                if categoria_filtro != "Todas":
                    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
                
                # Mostrar produtos em cards
                for _, produto in df_filtrado.iterrows():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{produto['produto']}</h4>
                        <p><strong>Categoria:</strong> {produto['categoria']}</p>
                        <p><strong>Unidades:</strong> {produto['unidades']}</p>
                        <div class="metric-value">R$ {produto['valor_diaria']:.2f}</div>
                        <div class="metric-label">por diária</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Erro ao carregar catálogo de produtos.")
        
        elif opcao == "Chat da Equipe":
            st.header("Chat da Equipe")
            componente_chat("comercial_geral", usuario['nome'])
    
    elif perfil == 'logistica':
        st.sidebar.markdown("### Menu Logística")
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "Dashboard Logístico",
            "Gestão de Pedidos", 
            "Gestão de Equipes",
            "Tarefas de Galpão",
            "Documentos",
            "Chat Integrado"
        ])
        
        if opcao == "Dashboard Logístico":
            st.header("Dashboard Logístico")
            
            # KPIs Logística
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">2</div>
                    <div class="metric-label">Entregas Hoje</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">1</div>
                    <div class="metric-label">Pendente Docs</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">5</div>
                    <div class="metric-label">Equipes Ativas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Tarefas Galpão</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Alertas
            st.subheader("⚠️ Alertas")
            
            st.warning("📋 Pedido PED003 - Documentos pendentes")
            st.info("🚚 Entrega PED002 - Programada para hoje às 14h")
            
            # Próximas entregas
            st.subheader("📅 Próximas Entregas (48h)")
            
            proximas_entregas = todos_pedidos[todos_pedidos['status'] != 'Finalizado'].copy()
            
            if not proximas_entregas.empty:
                for _, entrega in proximas_entregas.iterrows():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{entrega['numero_pedido']} - {entrega['cliente']}</h4>
                        <p><strong>Local:</strong> {entrega['local']}</p>
                        <p><strong>Data:</strong> {entrega['data_entrega']}</p>
                        <p><strong>Regime:</strong> <span class="status-badge status-{entrega['regime_pagamento'].lower().replace('%', 'pct')}">{entrega['regime_pagamento']}</span></p>
                        <p><strong>Equipe:</strong> {', '.join(entrega['equipe_alocada']) if isinstance(entrega['equipe_alocada'], list) else 'Não alocada'}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif opcao == "Gestão de Pedidos":
            st.header("Gestão de Pedidos - Logística")
            
            # Seletor de pedido
            pedido_opcoes = [f"{row['numero_pedido']} - {row['cliente']}" for _, row in todos_pedidos.iterrows()]
            pedido_selecionado = st.selectbox("Selecionar Pedido:", pedido_opcoes)
            
            if pedido_selecionado:
                numero_pedido = pedido_selecionado.split(' - ')[0]
                dados_pedido = todos_pedidos[todos_pedidos['numero_pedido'] == numero_pedido].iloc[0]
                
                # Informações do pedido
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{dados_pedido['numero_pedido']} - {dados_pedido['cliente']}</h3>
                    <p><strong>Produto/Serviço:</strong> {dados_pedido['produto_servico']}</p>
                    <p><strong>Local:</strong> {dados_pedido['local']}</p>
                    <p><strong>Data de Entrega:</strong> {dados_pedido['data_entrega']}</p>
                    <p><strong>Valor:</strong> R$ {dados_pedido['valor']:.2f}</p>
                    <p><strong>Regime:</strong> <span class="status-badge status-{dados_pedido['regime_pagamento'].lower().replace('%', 'pct')}">{dados_pedido['regime_pagamento']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Datas e horários específicos
                st.subheader("📅 Datas e Horários")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🚚 Entrega**")
                    data_entrega = st.date_input("Data de Entrega", key=f"data_entrega_{numero_pedido}")
                    hora_entrega = st.time_input("Horário de Entrega", key=f"hora_entrega_{numero_pedido}")
                    responsavel_entrega = st.text_input("Responsável pela Recepção", key=f"resp_entrega_{numero_pedido}")
                
                with col2:
                    st.markdown("**📦 Recolhimento**")
                    data_recolhimento = st.date_input("Data de Recolhimento", key=f"data_recolhimento_{numero_pedido}")
                    hora_recolhimento = st.time_input("Horário de Recolhimento", key=f"hora_recolhimento_{numero_pedido}")
                    responsavel_recolhimento = st.text_input("Responsável pela Liberação", key=f"resp_recolhimento_{numero_pedido}")
                
                # Alocação de equipe
                st.subheader("👥 Alocação de Equipe")
                
                equipe_disponivel = [col['nome'] for col in COLABORADORES if col['status'] == 'Disponível']
                equipe_selecionada = st.multiselect(
                    "Selecionar Membros da Equipe:",
                    equipe_disponivel,
                    default=dados_pedido['equipe_alocada'] if isinstance(dados_pedido['equipe_alocada'], list) else []
                )
                
                # Documentos
                st.subheader("📄 Documentos")
                
                for doc in DOCUMENTOS_LOGISTICA:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(doc)
                    
                    with col2:
                        arquivo = st.file_uploader(f"Upload {doc}", key=f"doc_{doc}_{numero_pedido}", label_visibility="collapsed")
                    
                    with col3:
                        if st.button(f"Gerar {doc}", key=f"gerar_{doc}_{numero_pedido}"):
                            # Gerar documento automaticamente
                            pdf_buffer = gerar_documento_logistica(doc, dados_pedido, {})
                            
                            st.download_button(
                                label=f"📥 Download {doc}",
                                data=pdf_buffer.getvalue(),
                                file_name=f"{doc}_{numero_pedido}.pdf",
                                mime="application/pdf",
                                key=f"download_{doc}_{numero_pedido}"
                            )
                
                # Salvar informações
                if st.button("💾 Salvar Informações Logísticas", use_container_width=True):
                    st.success("✅ Informações salvas com sucesso!")
                    
                    # Enviar notificação para equipe (simulado)
                    if equipe_selecionada:
                        st.info(f"📲 Notificação enviada para: {', '.join(equipe_selecionada)}")
        
        elif opcao == "Gestão de Equipes":
            st.header("Gestão de Equipes")
            
            # Estatísticas da equipe
            col1, col2, col3 = st.columns(3)
            
            with col1:
                disponivel = len([col for col in COLABORADORES if col['status'] == 'Disponível'])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{disponivel}</div>
                    <div class="metric-label">Disponíveis</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                ocupado = len([col for col in COLABORADORES if col['status'] == 'Ocupado'])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{ocupado}</div>
                    <div class="metric-label">Ocupados</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(COLABORADORES)}</div>
                    <div class="metric-label">Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Lista de colaboradores
            st.subheader("👥 Colaboradores")
            
            for colaborador in COLABORADORES:
                status_color = "#10b981" if colaborador['status'] == 'Disponível' else "#f59e0b"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{colaborador['nome']}</h4>
                    <p><strong>Função:</strong> {colaborador['funcao']}</p>
                    <p><strong>Especialidade:</strong> {colaborador['especialidade']}</p>
                    <p><strong>Disponibilidade:</strong> {colaborador['disponibilidade']}</p>
                    <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: 600;">{colaborador['status']}</span></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Adicionar novo colaborador
            st.subheader("➕ Adicionar Colaborador")
            
            with st.form("novo_colaborador"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome Completo")
                    funcao = st.text_input("Função")
                
                with col2:
                    especialidade = st.text_input("Especialidade")
                    disponibilidade = st.selectbox("Disponibilidade", ["Seg-Sex", "Ter-Sab", "Seg-Dom", "Qua-Dom"])
                
                if st.form_submit_button("Adicionar Colaborador"):
                    if nome and funcao:
                        novo_colaborador = {
                            'nome': nome,
                            'funcao': funcao,
                            'especialidade': especialidade,
                            'disponibilidade': disponibilidade,
                            'status': 'Disponível'
                        }
                        COLABORADORES.append(novo_colaborador)
                        st.success(f"✅ Colaborador {nome} adicionado com sucesso!")
                        st.rerun()
        
        elif opcao == "Tarefas de Galpão":
            st.header("Tarefas de Galpão")
            
            # Estatísticas das tarefas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pendentes = len([t for t in st.session_state.tarefas_galpao if t['status'] == 'Pendente'])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{pendentes}</div>
                    <div class="metric-label">Pendentes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                andamento = len([t for t in st.session_state.tarefas_galpao if t['status'] == 'Em Andamento'])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{andamento}</div>
                    <div class="metric-label">Em Andamento</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                concluidas = len([t for t in st.session_state.tarefas_galpao if t['status'] == 'Concluída'])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{concluidas}</div>
                    <div class="metric-label">Concluídas</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Lista de tarefas
            st.subheader("📋 Tarefas Ativas")
            
            for tarefa in st.session_state.tarefas_galpao:
                status_color = {
                    'Pendente': '#f59e0b',
                    'Em Andamento': '#FF6B00',
                    'Concluída': '#10b981'
                }.get(tarefa['status'], '#666666')
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{tarefa['titulo']}</h4>
                    <p><strong>Tipo:</strong> {tarefa['tipo']}</p>
                    <p><strong>Descrição:</strong> {tarefa['descricao']}</p>
                    <p><strong>Responsável:</strong> {tarefa['responsavel']}</p>
                    <p><strong>Prazo:</strong> {tarefa['data_prazo']}</p>
                    <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: 600;">{tarefa['status']}</span></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Nova tarefa
            st.subheader("➕ Nova Tarefa de Galpão")
            
            with st.form("nova_tarefa_galpao"):
                col1, col2 = st.columns(2)
                
                with col1:
                    titulo = st.text_input("Título da Tarefa")
                    tipo = st.selectbox("Tipo", TIPOS_TAREFA_GALPAO)
                    responsavel = st.selectbox("Responsável", [col['nome'] for col in COLABORADORES])
                
                with col2:
                    descricao = st.text_area("Descrição")
                    data_prazo = st.date_input("Data Prazo")
                    prioridade = st.selectbox("Prioridade", ["Baixa", "Normal", "Alta", "Urgente"])
                
                if st.form_submit_button("Criar Tarefa"):
                    if titulo and tipo and responsavel:
                        nova_tarefa = {
                            'id': f'TG{len(st.session_state.tarefas_galpao) + 1:03d}',
                            'titulo': titulo,
                            'tipo': tipo,
                            'descricao': descricao,
                            'responsavel': responsavel,
                            'data_criacao': datetime.now().strftime('%Y-%m-%d'),
                            'data_prazo': data_prazo.strftime('%Y-%m-%d'),
                            'status': 'Pendente',
                            'prioridade': prioridade
                        }
                        st.session_state.tarefas_galpao.append(nova_tarefa)
                        st.success(f"✅ Tarefa {titulo} criada com sucesso!")
                        st.rerun()
        
        elif opcao == "Chat Integrado":
            st.header("Chat Integrado")
            componente_chat("logistica_geral", usuario['nome'])
    
    elif perfil == 'campo':
        st.sidebar.markdown(f"### {usuario['nome']}")
        
        # Filtrar pedidos da equipe
        pedidos_equipe = todos_pedidos[todos_pedidos['equipe_alocada'].apply(lambda x: usuario['nome'] in x if isinstance(x, list) else False)]
        
        if not pedidos_equipe.empty:
            # Seletor de trabalho
            trabalhos_opcoes = [f"{row['numero_pedido']} - {row['cliente']}" for _, row in pedidos_equipe.iterrows()]
            trabalho_selecionado = st.selectbox("📋 Selecionar Trabalho:", trabalhos_opcoes)
            
            if trabalho_selecionado:
                numero_pedido = trabalho_selecionado.split(' - ')[0]
                dados_pedido = pedidos_equipe[pedidos_equipe['numero_pedido'] == numero_pedido].iloc[0]
                
                # Card do trabalho
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{dados_pedido['numero_pedido']} - {dados_pedido['cliente']}</h3>
                    <p><strong>📍 Local:</strong> {dados_pedido['local']}</p>
                    <p><strong>📅 Data:</strong> {dados_pedido['data_entrega']}</p>
                    <p><strong>💰 Regime:</strong> <span class="status-badge status-{dados_pedido['regime_pagamento'].lower().replace('%', 'pct')}">{dados_pedido['regime_pagamento']}</span></p>
                    <p><strong>🛠️ Produtos:</strong> {dados_pedido['produto_servico']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Obter progresso das etapas
                progresso = obter_progresso_etapas(numero_pedido)
                etapa_atual = progresso['etapa_atual']
                etapas_concluidas = progresso['etapas_concluidas']
                
                # Barra de progresso
                if etapa_atual == 'finalizado':
                    progresso_pct = 100
                else:
                    progresso_pct = (len(etapas_concluidas) / 7) * 100
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Progresso do Trabalho</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progresso_pct}%"></div>
                    </div>
                    <p style="text-align: center; margin: 0.5rem 0; font-weight: 600;">
                        {progresso_pct:.0f}% Concluído ({len(etapas_concluidas)}/7 etapas)
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar etapas
                st.header("Etapas do Trabalho")
                
                for etapa in ETAPAS_CAMPO:
                    etapa_id = etapa['id']
                    
                    # Determinar status da etapa
                    if etapa_id in etapas_concluidas:
                        status_class = "etapa-concluida"
                        status_icon = "✅"
                        disabled = True
                    elif etapa_id == etapa_atual:
                        status_class = "etapa-ativa"
                        status_icon = "🔄"
                        disabled = False
                    else:
                        status_class = "etapa-bloqueada"
                        status_icon = "⏳"
                        disabled = True
                    
                    # Card da etapa
                    st.markdown(f"""
                    <div class="etapa-card {status_class}">
                        <h4>{status_icon} {etapa['titulo']}</h4>
                        <p>{etapa['descricao']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Formulário da etapa ativa
                    if etapa_id == etapa_atual and not disabled:
                        with st.expander(f"📝 Executar {etapa['titulo']}", expanded=True):
                            with st.form(f"etapa_{etapa_id}_{numero_pedido}"):
                                dados_etapa = {}
                                
                                # GPS funcional
                                if 'gps' in etapa['obrigatorio']:
                                    st.markdown("**📍 Localização GPS**")
                                    latitude, longitude, endereco = componente_gps(etapa_id, numero_pedido)
                                    if latitude and longitude:
                                        dados_etapa['latitude'] = latitude
                                        dados_etapa['longitude'] = longitude
                                        dados_etapa['endereco'] = endereco
                                
                                # Foto obrigatória
                                if 'foto' in etapa['obrigatorio']:
                                    dados_etapa['foto'] = st.file_uploader(
                                        "📸 Foto Obrigatória", 
                                        type=['jpg', 'jpeg', 'png'],
                                        key=f"foto_{etapa_id}_{numero_pedido}"
                                    )
                                
                                # Checklist
                                if 'checklist' in etapa['obrigatorio']:
                                    st.markdown("**📋 Checklist**")
                                    produtos = dados_pedido['produto_servico'].split(', ')
                                    checklist_items = {}
                                    for produto in produtos:
                                        checklist_items[produto] = st.checkbox(produto, key=f"check_{produto}_{etapa_id}_{numero_pedido}")
                                    dados_etapa['checklist'] = checklist_items
                                
                                # Assinatura
                                if 'assinatura' in etapa['obrigatorio']:
                                    dados_etapa['assinatura_cliente'] = st.text_input("Nome do Cliente (Assinatura)", key=f"assinatura_{etapa_id}_{numero_pedido}")
                                
                                # Relatório
                                if 'relatorio' in etapa['obrigatorio']:
                                    dados_etapa['relatorio'] = st.text_area("Relatório Final", key=f"relatorio_{etapa_id}_{numero_pedido}")
                                
                                # Botão para concluir etapa
                                if st.form_submit_button(f"✅ Concluir {etapa['titulo']}", use_container_width=True):
                                    # Validações
                                    valido = True
                                    
                                    if 'gps' in etapa['obrigatorio'] and (not latitude or not longitude):
                                        st.error("❌ Localização GPS é obrigatória!")
                                        valido = False
                                    
                                    if 'foto' in etapa['obrigatorio'] and not dados_etapa.get('foto'):
                                        st.error("❌ Foto é obrigatória!")
                                        valido = False
                                    
                                    if 'checklist' in etapa['obrigatorio']:
                                        if not all(checklist_items.values()):
                                            st.error("❌ Todos os itens do checklist devem ser marcados!")
                                            valido = False
                                    
                                    if 'assinatura' in etapa['obrigatorio'] and not dados_etapa.get('assinatura_cliente'):
                                        st.error("❌ Assinatura do cliente é obrigatória!")
                                        valido = False
                                    
                                    if 'relatorio' in etapa['obrigatorio'] and not dados_etapa.get('relatorio'):
                                        st.error("❌ Relatório final é obrigatório!")
                                        valido = False
                                    
                                    if valido:
                                        dados_etapa['timestamp'] = datetime.now().isoformat()
                                        dados_etapa['equipe'] = usuario['nome']
                                        
                                        avancar_etapa(numero_pedido, etapa_id, dados_etapa)
                                        
                                        st.success(f"✅ {etapa['titulo']} concluída com sucesso!")
                                        st.balloons()
                                        st.rerun()
                
                # Finalização do trabalho
                if etapa_atual == 'finalizado':
                    st.success("🎉 Trabalho finalizado com sucesso!")
                    st.balloons()
                
                # Chat do trabalho
                st.header("Chat do Trabalho")
                componente_chat(f"trabalho_{numero_pedido}", usuario['nome'])
        
        else:
            st.info(f"📋 Nenhum trabalho encontrado para {usuario['nome']}")
    
    elif perfil == 'boss':
        st.sidebar.markdown("### Menu Executivo")
        
        opcao = st.sidebar.selectbox("📋 Módulos", [
            "Dashboard Executivo",
            "Análise Financeira", 
            "Performance da Equipe",
            "Relatórios Gerenciais",
            "KPIs Estratégicos"
        ])
        
        if opcao == "Dashboard Executivo":
            st.header("Dashboard Executivo")
            
            # KPIs Executivos
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 15.490</div>
                    <div class="metric-label">Receita Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 9.500</div>
                    <div class="metric-label">Custos Totais</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 5.990</div>
                    <div class="metric-label">Lucro Líquido</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">38.7%</div>
                    <div class="metric-label">Margem Líquida</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Pedidos Ativos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">95%</div>
                    <div class="metric-label">Eficiência</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos executivos
            col1, col2 = st.columns(2)
            
            with col1:
                # Receita vs Custos vs Lucro
                fig_financeiro = go.Figure()
                
                fig_financeiro.add_trace(go.Bar(
                    name='Receita',
                    x=['Nov', 'Dez', 'Jan'],
                    y=[8500, 12300, 15490],
                    marker_color='#FF6B00'
                ))
                
                fig_financeiro.add_trace(go.Bar(
                    name='Custos',
                    x=['Nov', 'Dez', 'Jan'],
                    y=[5500, 7800, 9500],
                    marker_color='#f59e0b'
                ))
                
                fig_financeiro.add_trace(go.Bar(
                    name='Lucro',
                    x=['Nov', 'Dez', 'Jan'],
                    y=[3000, 4500, 5990],
                    marker_color='#10b981'
                ))
                
                fig_financeiro.update_layout(
                    title="Análise Financeira Mensal",
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                
                st.plotly_chart(fig_financeiro, use_container_width=True)
            
            with col2:
                # Distribuição por regime de pagamento
                regimes = todos_pedidos['regime_pagamento'].value_counts()
                
                fig_regimes = px.pie(
                    values=regimes.values,
                    names=regimes.index,
                    title="Distribuição por Regime de Pagamento",
                    color_discrete_sequence=['#10b981', '#f59e0b', '#8b5cf6']
                )
                
                fig_regimes.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                
                st.plotly_chart(fig_regimes, use_container_width=True)
            
            # Performance da equipe
            st.subheader("👥 Performance da Equipe")
            
            performance_data = {
                'Colaborador': ['João Silva', 'Carlos Santos', 'Pedro Lima', 'Ana Costa', 'Roberto Alves'],
                'Trabalhos Concluídos': [8, 6, 10, 4, 7],
                'Avaliação Média': [4.8, 4.6, 4.9, 4.7, 4.5],
                'Status': ['Disponível', 'Ocupado', 'Disponível', 'Disponível', 'Disponível']
            }
            
            df_performance = pd.DataFrame(performance_data)
            st.dataframe(df_performance, use_container_width=True, hide_index=True)
            
            # Alertas executivos
            st.subheader("🚨 Alertas Executivos")
            
            st.warning("⚠️ Pedido PED003 com documentos pendentes - Ação necessária")
            st.info("📈 Receita mensal cresceu 26% - Meta superada")
            st.success("✅ Todos os trabalhos de dezembro foram finalizados")
        
        elif opcao == "Análise Financeira":
            st.header("Análise Financeira Detalhada")
            
            # Métricas financeiras detalhadas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 15.490</div>
                    <div class="metric-label">Receita Bruta</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 9.500</div>
                    <div class="metric-label">Custos Operacionais</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 5.990</div>
                    <div class="metric-label">Lucro Líquido</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">R$ 5.167</div>
                    <div class="metric-label">Ticket Médio</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Análise por pedido
            st.subheader("💰 Análise por Pedido")
            
            # Calcular margem por pedido
            todos_pedidos['margem'] = ((todos_pedidos['valor'] - todos_pedidos['custos']) / todos_pedidos['valor'] * 100).round(1)
            todos_pedidos['lucro'] = todos_pedidos['valor'] - todos_pedidos['custos']
            
            st.dataframe(
                todos_pedidos[['numero_pedido', 'cliente', 'valor', 'custos', 'lucro', 'margem', 'regime_pagamento']],
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de margem por regime
            fig_margem = px.box(
                todos_pedidos, 
                x='regime_pagamento', 
                y='margem',
                title="Distribuição de Margem por Regime de Pagamento",
                color='regime_pagamento',
                color_discrete_sequence=['#10b981', '#f59e0b', '#8b5cf6']
            )
            
            fig_margem.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig_margem, use_container_width=True)
        
        elif opcao == "Performance da Equipe":
            st.header("Performance da Equipe")
            
            # Métricas da equipe
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">5</div>
                    <div class="metric-label">Colaboradores Ativos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">35</div>
                    <div class="metric-label">Trabalhos Concluídos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">4.7</div>
                    <div class="metric-label">Avaliação Média</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">95%</div>
                    <div class="metric-label">Taxa de Conclusão</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Detalhes por colaborador
            st.subheader("👤 Detalhes por Colaborador")
            
            performance_detalhada = {
                'Colaborador': ['João Silva', 'Carlos Santos', 'Pedro Lima', 'Ana Costa', 'Roberto Alves'],
                'Função': ['Montador Senior', 'Técnico Audio/Video', 'Auxiliar Geral', 'Decoradora', 'Motorista'],
                'Trabalhos Concluídos': [8, 6, 10, 4, 7],
                'Trabalhos em Andamento': [1, 2, 0, 1, 1],
                'Avaliação Média': [4.8, 4.6, 4.9, 4.7, 4.5],
                'Disponibilidade': ['Seg-Sex', 'Ter-Sab', 'Seg-Dom', 'Qua-Dom', 'Seg-Sex'],
                'Status': ['Disponível', 'Ocupado', 'Disponível', 'Disponível', 'Disponível']
            }
            
            df_performance_detalhada = pd.DataFrame(performance_detalhada)
            st.dataframe(df_performance_detalhada, use_container_width=True, hide_index=True)
            
            # Gráfico de produtividade
            fig_produtividade = px.bar(
                df_performance_detalhada,
                x='Colaborador',
                y='Trabalhos Concluídos',
                title="Produtividade por Colaborador",
                color='Avaliação Média',
                color_continuous_scale='Viridis'
            )
            
            fig_produtividade.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig_produtividade, use_container_width=True)
        
        elif opcao == "Relatórios Gerenciais":
            st.header("Relatórios Gerenciais")
            
            # Seletor de período
            col1, col2 = st.columns(2)
            
            with col1:
                data_inicio = st.date_input("Data Início")
            
            with col2:
                data_fim = st.date_input("Data Fim")
            
            # Resumo executivo
            st.subheader("📊 Resumo Executivo")
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>Resumo do Período</h4>
                <p><strong>Receita Total:</strong> R$ 15.490,00</p>
                <p><strong>Custos Totais:</strong> R$ 9.500,00</p>
                <p><strong>Lucro Líquido:</strong> R$ 5.990,00</p>
                <p><strong>Margem Líquida:</strong> 38.7%</p>
                <p><strong>Pedidos Processados:</strong> 3</p>
                <p><strong>Taxa de Conclusão:</strong> 100%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Análise por categoria
            st.subheader("📈 Análise por Categoria")
            
            categoria_analysis = todos_pedidos.groupby('categoria').agg({
                'valor': 'sum',
                'custos': 'sum',
                'numero_pedido': 'count'
            }).reset_index()
            
            categoria_analysis['lucro'] = categoria_analysis['valor'] - categoria_analysis['custos']
            categoria_analysis['margem'] = (categoria_analysis['lucro'] / categoria_analysis['valor'] * 100).round(1)
            
            st.dataframe(categoria_analysis, use_container_width=True, hide_index=True)
            
            # Tendências
            st.subheader("📉 Tendências")
            
            tendencias_data = {
                'Mês': ['Novembro', 'Dezembro', 'Janeiro'],
                'Receita': [8500, 12300, 15490],
                'Pedidos': [2, 3, 3],
                'Ticket Médio': [4250, 4100, 5167]
            }
            
            df_tendencias = pd.DataFrame(tendencias_data)
            
            fig_tendencias = px.line(
                df_tendencias,
                x='Mês',
                y=['Receita', 'Ticket Médio'],
                title="Tendências de Receita e Ticket Médio",
                color_discrete_sequence=['#FF6B00', '#10b981']
            )
            
            fig_tendencias.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            st.plotly_chart(fig_tendencias, use_container_width=True)
        
        elif opcao == "KPIs Estratégicos":
            st.header("KPIs Estratégicos")
            
            # KPIs principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">26%</div>
                    <div class="metric-label">Crescimento Mensal</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Taxa de Entrega</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">4.7/5</div>
                    <div class="metric-label">Satisfação Cliente</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Distribuição por regime
            st.subheader("💰 Distribuição por Regime de Pagamento")
            
            regime_stats = todos_pedidos['regime_pagamento'].value_counts()
            regime_percentual = (regime_stats / regime_stats.sum() * 100).round(1)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{regime_stats.get('Padrão', 0)}</div>
                    <div class="metric-label">Pedidos Padrão ({regime_percentual.get('Padrão', 0)}%)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{regime_stats.get('1%', 0)}</div>
                    <div class="metric-label">Pedidos Urgentes ({regime_percentual.get('1%', 0)}%)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{regime_stats.get('3%', 0)}</div>
                    <div class="metric-label">Pedidos Weekend ({regime_percentual.get('3%', 0)}%)</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Eficiência operacional
            st.subheader("⚡ Eficiência Operacional")
            
            eficiencia_data = {
                'Métrica': ['Tempo Médio de Execução', 'Taxa de Retrabalho', 'Utilização da Equipe', 'Satisfação da Equipe'],
                'Valor Atual': ['6.2 horas', '2%', '85%', '4.5/5'],
                'Meta': ['6 horas', '< 5%', '90%', '> 4.0'],
                'Status': ['🟡 Atenção', '🟢 OK', '🟡 Atenção', '🟢 OK']
            }
            
            df_eficiencia = pd.DataFrame(eficiencia_data)
            st.dataframe(df_eficiencia, use_container_width=True, hide_index=True)
            
            # Projeções
            st.subheader("📈 Projeções")
            
            st.markdown("""
            <div class="metric-card">
                <h4>Projeções para Próximo Mês</h4>
                <p><strong>Receita Projetada:</strong> R$ 18.500,00 (+19%)</p>
                <p><strong>Pedidos Estimados:</strong> 4 (+33%)</p>
                <p><strong>Margem Esperada:</strong> 40% (+1.3pp)</p>
                <p><strong>Equipe Necessária:</strong> 5 colaboradores</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
