import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import base64
from fpdf import FPDF
import io
import time
import hashlib
import uuid
import os
import logging
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES GLOBAIS E CONSTANTES
# ==========================================

# Configuração da página
st.set_page_config(
    page_title="NEXO - Núcleo de Excelência Operacional",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constantes do sistema
class StatusPedido(Enum):
    ORCAMENTO = "Orçamento"
    APROVADO = "Aprovado"
    EM_PRODUCAO = "Em Produção"
    PRONTO_ENTREGA = "Pronto para Entrega"
    EM_ENTREGA = "Em Entrega"
    ENTREGUE = "Entregue"
    EM_RECOLHIMENTO = "Em Recolhimento"
    CONCLUIDO = "Concluído"
    CANCELADO = "Cancelado"

class TipoUsuario(Enum):
    COMERCIAL = "comercial"
    LOGISTICA = "logistica"
    CAMPO = "campo"
    BOSS = "boss"
    ADMIN = "admin"

class PrioridadePedido(Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    URGENTE = "Urgente"

class StatusEquipe(Enum):
    DISPONIVEL = "Disponível"
    OCUPADO = "Ocupado"
    MANUTENCAO = "Manutenção"
    FOLGA = "Folga"

# Configurações de cores NEXO
CORES_NEXO = {
    'laranja_primario': '#FF6B35',
    'laranja_secundario': '#FF8C42',
    'laranja_claro': '#FFB366',
    'preto': '#1E1E1E',
    'cinza_escuro': '#2D2D2D',
    'cinza_medio': '#4A4A4A',
    'cinza_claro': '#E0E0E0',
    'branco': '#FFFFFF',
    'verde_sucesso': '#4CAF50',
    'vermelho_erro': '#F44336',
    'amarelo_aviso': '#FF9800',
    'azul_info': '#2196F3'
}

# CSS personalizado ultra completo
CSS_NEXO_ULTRA = f"""
<style>
    /* Reset e configurações base */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    /* Configurações principais */
    .stApp {{
        background: linear-gradient(135deg, {CORES_NEXO['preto']} 0%, {CORES_NEXO['cinza_escuro']} 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Header principal */
    .nexo-header {{
        background: linear-gradient(90deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .nexo-logo {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {CORES_NEXO['branco']};
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }}
    
    .nexo-subtitle {{
        font-size: 0.9rem;
        color: {CORES_NEXO['branco']};
        opacity: 0.9;
        font-weight: 300;
        margin-top: -5px;
    }}
    
    /* Navegação */
    .nexo-nav {{
        background: {CORES_NEXO['cinza_escuro']};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid {CORES_NEXO['cinza_medio']};
    }}
    
    .nav-button {{
        background: linear-gradient(135deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        color: {CORES_NEXO['branco']};
        border: none;
        padding: 0.8rem 1.5rem;
        margin: 0.2rem;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.2);
    }}
    
    .nav-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        background: linear-gradient(135deg, {CORES_NEXO['laranja_secundario']} 0%, {CORES_NEXO['laranja_primario']} 100%);
    }}
    
    .nav-button.active {{
        background: linear-gradient(135deg, {CORES_NEXO['verde_sucesso']} 0%, #45a049 100%);
        transform: translateY(-1px);
    }}
    
    /* Cards e containers */
    .nexo-card {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }}
    
    .nexo-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border-color: {CORES_NEXO['laranja_primario']};
    }}
    
    .card-header {{
        background: linear-gradient(90deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        color: {CORES_NEXO['branco']};
        padding: 1rem 1.5rem;
        margin: -1.5rem -1.5rem 1.5rem -1.5rem;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        font-size: 1.1rem;
    }}
    
    /* Formulários */
    .stTextInput > div > div > input {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {CORES_NEXO['laranja_primario']};
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.3);
        outline: none;
    }}
    
    .stSelectbox > div > div > select {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 0.8rem;
    }}
    
    .stTextArea > div > div > textarea {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 0.8rem;
    }}
    
    /* Botões */
    .stButton > button {{
        background: linear-gradient(135deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        color: {CORES_NEXO['branco']};
        border: none;
        border-radius: 8px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
        background: linear-gradient(135deg, {CORES_NEXO['laranja_secundario']} 0%, {CORES_NEXO['laranja_primario']} 100%);
    }}
    
    /* Botões de ação específicos */
    .btn-success {{
        background: linear-gradient(135deg, {CORES_NEXO['verde_sucesso']} 0%, #45a049 100%) !important;
    }}
    
    .btn-danger {{
        background: linear-gradient(135deg, {CORES_NEXO['vermelho_erro']} 0%, #d32f2f 100%) !important;
    }}
    
    .btn-warning {{
        background: linear-gradient(135deg, {CORES_NEXO['amarelo_aviso']} 0%, #f57c00 100%) !important;
    }}
    
    .btn-info {{
        background: linear-gradient(135deg, {CORES_NEXO['azul_info']} 0%, #1976d2 100%) !important;
    }}
    
    /* Tabelas */
    .stDataFrame {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    .stDataFrame table {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
    }}
    
    .stDataFrame th {{
        background: {CORES_NEXO['laranja_primario']} !important;
        color: {CORES_NEXO['branco']} !important;
        font-weight: 600;
        padding: 1rem !important;
    }}
    
    .stDataFrame td {{
        padding: 0.8rem !important;
        border-bottom: 1px solid {CORES_NEXO['cinza_medio']};
    }}
    
    /* Métricas */
    .metric-card {{
        background: linear-gradient(135deg, {CORES_NEXO['cinza_escuro']} 0%, {CORES_NEXO['cinza_medio']} 100%);
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {CORES_NEXO['laranja_primario']};
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .metric-label {{
        font-size: 1rem;
        color: {CORES_NEXO['cinza_claro']};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Status badges */
    .status-badge {{
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
        display: inline-block;
        margin: 0.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    
    .status-orcamento {{
        background: linear-gradient(135deg, {CORES_NEXO['amarelo_aviso']} 0%, #f57c00 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-aprovado {{
        background: linear-gradient(135deg, {CORES_NEXO['azul_info']} 0%, #1976d2 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-producao {{
        background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-pronto {{
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-entrega {{
        background: linear-gradient(135deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-entregue {{
        background: linear-gradient(135deg, {CORES_NEXO['verde_sucesso']} 0%, #45a049 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-recolhimento {{
        background: linear-gradient(135deg, #607d8b 0%, #455a64 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-concluido {{
        background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    .status-cancelado {{
        background: linear-gradient(135deg, {CORES_NEXO['vermelho_erro']} 0%, #d32f2f 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    /* Alertas e notificações */
    .alert {{
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .alert-success {{
        background: linear-gradient(135deg, {CORES_NEXO['verde_sucesso']} 0%, #45a049 100%);
        color: {CORES_NEXO['branco']};
        border-left: 4px solid #2e7d32;
    }}
    
    .alert-error {{
        background: linear-gradient(135deg, {CORES_NEXO['vermelho_erro']} 0%, #d32f2f 100%);
        color: {CORES_NEXO['branco']};
        border-left: 4px solid #c62828;
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, {CORES_NEXO['amarelo_aviso']} 0%, #f57c00 100%);
        color: {CORES_NEXO['branco']};
        border-left: 4px solid #ef6c00;
    }}
    
    .alert-info {{
        background: linear-gradient(135deg, {CORES_NEXO['azul_info']} 0%, #1976d2 100%);
        color: {CORES_NEXO['branco']};
        border-left: 4px solid #1565c0;
    }}
    
    /* Loading e animações */
    .loading-spinner {{
        border: 4px solid {CORES_NEXO['cinza_medio']};
        border-top: 4px solid {CORES_NEXO['laranja_primario']};
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Responsividade mobile */
    @media (max-width: 768px) {{
        .nexo-header {{
            flex-direction: column;
            text-align: center;
            padding: 1rem;
        }}
        
        .nexo-logo {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .nav-button {{
            width: 100%;
            margin: 0.2rem 0;
        }}
        
        .nexo-card {{
            margin: 0.5rem 0;
            padding: 1rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
        }}
    }}
    
    /* Gráficos */
    .plotly-graph-div {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    /* Sidebar customizada */
    .css-1d391kg {{
        background: {CORES_NEXO['cinza_escuro']};
    }}
    
    .css-1d391kg .css-1v0mbdj {{
        background: {CORES_NEXO['laranja_primario']};
        color: {CORES_NEXO['branco']};
    }}
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {CORES_NEXO['cinza_medio']};
        color: {CORES_NEXO['branco']};
        border-radius: 6px;
        margin: 0.2rem;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
        color: {CORES_NEXO['branco']};
    }}
    
    /* Expander customizado */
    .streamlit-expanderHeader {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        font-weight: 600;
    }}
    
    .streamlit-expanderContent {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-top: none;
        border-radius: 0 0 8px 8px;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {CORES_NEXO['laranja_primario']} 0%, {CORES_NEXO['laranja_secundario']} 100%);
    }}
    
    /* File uploader */
    .stFileUploader {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px dashed {CORES_NEXO['laranja_primario']};
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: {CORES_NEXO['laranja_secundario']};
        background: {CORES_NEXO['cinza_medio']};
    }}
    
    /* Checkbox e radio */
    .stCheckbox > label {{
        color: {CORES_NEXO['branco']};
        font-weight: 500;
    }}
    
    .stRadio > label {{
        color: {CORES_NEXO['branco']};
        font-weight: 500;
    }}
    
    /* Slider */
    .stSlider > div > div > div > div {{
        background: {CORES_NEXO['laranja_primario']};
    }}
    
    /* Date input */
    .stDateInput > div > div > input {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
    }}
    
    /* Time input */
    .stTimeInput > div > div > input {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
    }}
    
    /* Number input */
    .stNumberInput > div > div > input {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
    }}
    
    /* Multiselect */
    .stMultiSelect > div > div > div {{
        background: {CORES_NEXO['cinza_escuro']};
        color: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
    }}
    
    /* Color picker */
    .stColorPicker > div > div > input {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
    }}
    
    /* Camera input */
    .stCameraInput {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Audio recorder */
    .stAudioRecorder {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 8px;
        padding: 1rem;
    }}
    
    /* Custom classes para componentes específicos */
    .login-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 15px;
        padding: 3rem;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        max-width: 400px;
        margin: 2rem auto;
        text-align: center;
    }}
    
    .dashboard-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }}
    
    .kpi-container {{
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 2rem 0;
    }}
    
    .form-section {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .form-section h3 {{
        color: {CORES_NEXO['laranja_primario']};
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 2px solid {CORES_NEXO['laranja_primario']};
        padding-bottom: 0.5rem;
    }}
    
    .action-buttons {{
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
        flex-wrap: wrap;
    }}
    
    .table-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        overflow-x: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    .search-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .filter-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        align-items: center;
    }}
    
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }}
    
    .chart-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    .timeline-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid {CORES_NEXO['laranja_primario']};
    }}
    
    .notification-container {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
    }}
    
    .workflow-step {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        position: relative;
        transition: all 0.3s ease;
    }}
    
    .workflow-step.active {{
        border-color: {CORES_NEXO['laranja_primario']};
        background: linear-gradient(135deg, {CORES_NEXO['cinza_escuro']} 0%, {CORES_NEXO['cinza_medio']} 100%);
    }}
    
    .workflow-step.completed {{
        border-color: {CORES_NEXO['verde_sucesso']};
        background: linear-gradient(135deg, {CORES_NEXO['cinza_escuro']} 0%, rgba(76, 175, 80, 0.1) 100%);
    }}
    
    .signature-pad {{
        background: {CORES_NEXO['branco']};
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 8px;
        width: 100%;
        height: 200px;
        margin: 1rem 0;
    }}
    
    .gps-container {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['azul_info']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }}
    
    .document-upload {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px dashed {CORES_NEXO['laranja_primario']};
        border-radius: 8px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .document-upload:hover {{
        border-color: {CORES_NEXO['laranja_secundario']};
        background: {CORES_NEXO['cinza_medio']};
    }}
    
    .priority-high {{
        border-left: 4px solid {CORES_NEXO['vermelho_erro']};
    }}
    
    .priority-medium {{
        border-left: 4px solid {CORES_NEXO['amarelo_aviso']};
    }}
    
    .priority-low {{
        border-left: 4px solid {CORES_NEXO['verde_sucesso']};
    }}
    
    .team-member-card {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 1px solid {CORES_NEXO['cinza_medio']};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
    }}
    
    .team-member-card:hover {{
        border-color: {CORES_NEXO['laranja_primario']};
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    }}
    
    .equipment-status {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }}
    
    .equipment-status.available {{
        background: {CORES_NEXO['verde_sucesso']};
    }}
    
    .equipment-status.busy {{
        background: {CORES_NEXO['vermelho_erro']};
    }}
    
    .equipment-status.maintenance {{
        background: {CORES_NEXO['amarelo_aviso']};
    }}
    
    /* Animações personalizadas */
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{
            transform: scale(1);
        }}
        50% {{
            transform: scale(1.05);
        }}
        100% {{
            transform: scale(1);
        }}
    }}
    
    .bounce {{
        animation: bounce 1s infinite;
    }}
    
    @keyframes bounce {{
        0%, 20%, 50%, 80%, 100% {{
            transform: translateY(0);
        }}
        40% {{
            transform: translateY(-10px);
        }}
        60% {{
            transform: translateY(-5px);
        }}
    }}
    
    .shake {{
        animation: shake 0.5s;
    }}
    
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
        30% {{ transform: translate(3px, 2px) rotate(0deg); }}
        40% {{ transform: translate(1px, -1px) rotate(1deg); }}
        50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
        60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
        70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
        80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
        90% {{ transform: translate(1px, 2px) rotate(0deg); }}
        100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
    }}
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {CORES_NEXO['cinza_escuro']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {CORES_NEXO['laranja_primario']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {CORES_NEXO['laranja_secundario']};
    }}
    
    /* Tooltips */
    .tooltip {{
        position: relative;
        display: inline-block;
    }}
    
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: {CORES_NEXO['preto']};
        color: {CORES_NEXO['branco']};
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    
    /* Modal personalizado */
    .modal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .modal-content {{
        background: {CORES_NEXO['cinza_escuro']};
        border: 2px solid {CORES_NEXO['laranja_primario']};
        border-radius: 12px;
        padding: 2rem;
        max-width: 90%;
        max-height: 90%;
        overflow-y: auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    
    /* Print styles */
    @media print {{
        .no-print {{
            display: none !important;
        }}
        
        .nexo-card {{
            break-inside: avoid;
        }}
        
        body {{
            background: white !important;
            color: black !important;
        }}
    }}
    
    /* Acessibilidade */
    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }}
    
    /* Focus styles para acessibilidade */
    button:focus,
    input:focus,
    select:focus,
    textarea:focus {{
        outline: 2px solid {CORES_NEXO['laranja_primario']};
        outline-offset: 2px;
    }}
    
    /* High contrast mode */
    @media (prefers-contrast: high) {{
        .nexo-card {{
            border-width: 3px;
        }}
        
        .nav-button {{
            border: 2px solid {CORES_NEXO['branco']};
        }}
    }}
    
    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {{
        /* Já estamos usando tema escuro por padrão */
    }}
    
    /* Estilos específicos para impressão de relatórios */
    .report-header {{
        background: {CORES_NEXO['branco']};
        color: {CORES_NEXO['preto']};
        padding: 2rem;
        border-bottom: 3px solid {CORES_NEXO['laranja_primario']};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .report-section {{
        background: {CORES_NEXO['branco']};
        color: {CORES_NEXO['preto']};
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {CORES_NEXO['cinza_claro']};
        border-radius: 8px;
    }}
    
    .report-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }}
    
    .report-table th,
    .report-table td {{
        border: 1px solid {CORES_NEXO['cinza_medio']};
        padding: 0.8rem;
        text-align: left;
    }}
    
    .report-table th {{
        background: {CORES_NEXO['laranja_primario']};
        color: {CORES_NEXO['branco']};
        font-weight: 600;
    }}
    
    .report-footer {{
        background: {CORES_NEXO['cinza_claro']};
        color: {CORES_NEXO['preto']};
        padding: 1rem;
        text-align: center;
        font-size: 0.9rem;
        border-top: 2px solid {CORES_NEXO['laranja_primario']};
        margin-top: 2rem;
    }}
</style>
"""

# ==========================================
# CLASSES DE DADOS E ESTRUTURAS
# ==========================================

@dataclass
class Usuario:
    """Classe para representar um usuário do sistema"""
    id: str
    nome: str
    email: str
    tipo: TipoUsuario
    ativo: bool = True
    data_criacao: datetime = None
    ultimo_acesso: datetime = None
    permissoes: List[str] = None
    
    def __post_init__(self):
        if self.data_criacao is None:
            self.data_criacao = datetime.now()
        if self.permissoes is None:
            self.permissoes = []

@dataclass
class Produto:
    """Classe para representar um produto do catálogo"""
    id: str
    nome: str
    categoria: str
    preco_unitario: float
    unidade: str
    descricao: str = ""
    ativo: bool = True
    estoque_minimo: int = 0
    estoque_atual: int = 0
    fornecedor: str = ""
    codigo_barras: str = ""
    peso: float = 0.0
    dimensoes: str = ""
    data_criacao: datetime = None
    data_atualizacao: datetime = None
    
    def __post_init__(self):
        if self.data_criacao is None:
            self.data_criacao = datetime.now()
        if self.data_atualizacao is None:
            self.data_atualizacao = datetime.now()

@dataclass
class ItemPedido:
    """Classe para representar um item de pedido"""
    produto_id: str
    produto_nome: str
    quantidade: int
    diarias: int
    preco_unitario: float
    desconto: float = 0.0
    observacoes: str = ""
    
    @property
    def subtotal(self) -> float:
        return (self.quantidade * self.diarias * self.preco_unitario) - self.desconto

@dataclass
class Pedido:
    """Classe para representar um pedido completo"""
    id: str
    numero: str
    cliente_nome: str
    cliente_email: str
    cliente_telefone: str
    cliente_documento: str
    evento_nome: str
    evento_data_inicio: datetime
    evento_data_fim: datetime
    evento_local: str
    evento_endereco: str
    evento_observacoes: str
    itens: List[ItemPedido]
    status: StatusPedido
    prioridade: PrioridadePedido
    valor_total: float
    desconto_total: float = 0.0
    taxa_entrega: float = 0.0
    observacoes_internas: str = ""
    vendedor_id: str = ""
    vendedor_nome: str = ""
    data_criacao: datetime = None
    data_atualizacao: datetime = None
    data_aprovacao: datetime = None
    data_entrega: datetime = None
    data_recolhimento: datetime = None
    data_conclusao: datetime = None
    equipe_responsavel: str = ""
    documentos_anexados: List[str] = None
    historico_status: List[Dict] = None
    coordenadas_entrega: Dict[str, float] = None
    coordenadas_recolhimento: Dict[str, float] = None
    assinatura_entrega: str = ""
    assinatura_recolhimento: str = ""
    fotos_entrega: List[str] = None
    fotos_recolhimento: List[str] = None
    
    def __post_init__(self):
        if self.data_criacao is None:
            self.data_criacao = datetime.now()
        if self.data_atualizacao is None:
            self.data_atualizacao = datetime.now()
        if self.documentos_anexados is None:
            self.documentos_anexados = []
        if self.historico_status is None:
            self.historico_status = []
        if self.coordenadas_entrega is None:
            self.coordenadas_entrega = {}
        if self.coordenadas_recolhimento is None:
            self.coordenadas_recolhimento = {}
        if self.fotos_entrega is None:
            self.fotos_entrega = []
        if self.fotos_recolhimento is None:
            self.fotos_recolhimento = []
    
    @property
    def valor_final(self) -> float:
        return self.valor_total - self.desconto_total + self.taxa_entrega
    
    @property
    def duracao_evento(self) -> int:
        return (self.evento_data_fim - self.evento_data_inicio).days + 1

@dataclass
class Colaborador:
    """Classe para representar um colaborador da equipe"""
    id: str
    nome: str
    cargo: str
    telefone: str
    email: str
    documento: str
    data_admissao: datetime
    salario: float
    status: StatusEquipe
    especialidades: List[str]
    avaliacoes: List[Dict] = None
    historico_pedidos: List[str] = None
    disponibilidade: Dict[str, bool] = None
    endereco: str = ""
    data_nascimento: datetime = None
    contato_emergencia: str = ""
    observacoes: str = ""
    ativo: bool = True
    
    def __post_init__(self):
        if self.avaliacoes is None:
            self.avaliacoes = []
        if self.historico_pedidos is None:
            self.historico_pedidos = []
        if self.disponibilidade is None:
            self.disponibilidade = {
                'segunda': True, 'terca': True, 'quarta': True,
                'quinta': True, 'sexta': True, 'sabado': True, 'domingo': True
            }

@dataclass
class Equipamento:
    """Classe para representar equipamentos da empresa"""
    id: str
    nome: str
    tipo: str
    modelo: str
    numero_serie: str
    data_aquisicao: datetime
    valor_aquisicao: float
    status: str
    localizacao_atual: str
    responsavel_id: str
    manutencoes: List[Dict] = None
    historico_uso: List[str] = None
    observacoes: str = ""
    ativo: bool = True
    
    def __post_init__(self):
        if self.manutencoes is None:
            self.manutencoes = []
        if self.historico_uso is None:
            self.historico_uso = []

@dataclass
class Documento:
    """Classe para representar documentos do sistema"""
    id: str
    nome: str
    tipo: str
    pedido_id: str
    caminho_arquivo: str
    tamanho: int
    data_upload: datetime
    usuario_upload: str
    assinado: bool = False
    data_assinatura: datetime = None
    usuario_assinatura: str = ""
    observacoes: str = ""
    
    def __post_init__(self):
        if self.data_upload is None:
            self.data_upload = datetime.now()

@dataclass
class LogSistema:
    """Classe para logs do sistema"""
    id: str
    timestamp: datetime
    usuario_id: str
    acao: str
    modulo: str
    detalhes: str
    ip_address: str = ""
    user_agent: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# ==========================================
# SISTEMA DE LOGGING E AUDITORIA
# ==========================================

class LoggerNexo:
    """Sistema de logging avançado para o NEXO"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nexo.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('NEXO')
    
    def log_acao(self, usuario_id: str, acao: str, modulo: str, detalhes: str = ""):
        """Registra uma ação no sistema"""
        log_entry = LogSistema(
            id=str(uuid.uuid4()),
            usuario_id=usuario_id,
            acao=acao,
            modulo=modulo,
            detalhes=detalhes
        )
        
        # Salva no session_state para consulta posterior
        if 'logs_sistema' not in st.session_state:
            st.session_state.logs_sistema = []
        
        st.session_state.logs_sistema.append(asdict(log_entry))
        
        # Log no arquivo
        self.logger.info(f"Usuario: {usuario_id} | Acao: {acao} | Modulo: {modulo} | Detalhes: {detalhes}")
    
    def log_erro(self, usuario_id: str, erro: str, modulo: str):
        """Registra um erro no sistema"""
        self.logger.error(f"ERRO - Usuario: {usuario_id} | Modulo: {modulo} | Erro: {erro}")
        self.log_acao(usuario_id, "ERRO", modulo, erro)
    
    def log_login(self, usuario_id: str, sucesso: bool):
        """Registra tentativa de login"""
        status = "SUCESSO" if sucesso else "FALHA"
        self.log_acao(usuario_id, f"LOGIN_{status}", "AUTENTICACAO", f"Login {status.lower()}")
    
    def log_logout(self, usuario_id: str):
        """Registra logout"""
        self.log_acao(usuario_id, "LOGOUT", "AUTENTICACAO", "Usuario fez logout")

# Instância global do logger
logger_nexo = LoggerNexo()

# ==========================================
# SISTEMA DE BANCO DE DADOS
# ==========================================

class DatabaseNexo:
    """Sistema de banco de dados para o NEXO"""
    
    def __init__(self):
        self.db_path = "nexo_database.db"
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo TEXT NOT NULL,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso TIMESTAMP,
                permissoes TEXT
            )
        ''')
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco_unitario REAL NOT NULL,
                unidade TEXT NOT NULL,
                descricao TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                estoque_minimo INTEGER DEFAULT 0,
                estoque_atual INTEGER DEFAULT 0,
                fornecedor TEXT,
                codigo_barras TEXT,
                peso REAL DEFAULT 0.0,
                dimensoes TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                numero TEXT UNIQUE NOT NULL,
                cliente_nome TEXT NOT NULL,
                cliente_email TEXT,
                cliente_telefone TEXT,
                cliente_documento TEXT,
                evento_nome TEXT NOT NULL,
                evento_data_inicio TIMESTAMP NOT NULL,
                evento_data_fim TIMESTAMP NOT NULL,
                evento_local TEXT NOT NULL,
                evento_endereco TEXT,
                evento_observacoes TEXT,
                status TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                valor_total REAL NOT NULL,
                desconto_total REAL DEFAULT 0.0,
                taxa_entrega REAL DEFAULT 0.0,
                observacoes_internas TEXT,
                vendedor_id TEXT,
                vendedor_nome TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_aprovacao TIMESTAMP,
                data_entrega TIMESTAMP,
                data_recolhimento TIMESTAMP,
                data_conclusao TIMESTAMP,
                equipe_responsavel TEXT,
                documentos_anexados TEXT,
                historico_status TEXT,
                coordenadas_entrega TEXT,
                coordenadas_recolhimento TEXT,
                assinatura_entrega TEXT,
                assinatura_recolhimento TEXT,
                fotos_entrega TEXT,
                fotos_recolhimento TEXT
            )
        ''')
        
        # Tabela de itens de pedido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id TEXT PRIMARY KEY,
                pedido_id TEXT NOT NULL,
                produto_id TEXT NOT NULL,
                produto_nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                diarias INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                desconto REAL DEFAULT 0.0,
                observacoes TEXT,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        
        # Tabela de colaboradores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                cargo TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                documento TEXT UNIQUE,
                data_admissao TIMESTAMP NOT NULL,
                salario REAL,
                status TEXT NOT NULL,
                especialidades TEXT,
                avaliacoes TEXT,
                historico_pedidos TEXT,
                disponibilidade TEXT,
                endereco TEXT,
                data_nascimento TIMESTAMP,
                contato_emergencia TEXT,
                observacoes TEXT,
                ativo BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Tabela de equipamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipamentos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                modelo TEXT,
                numero_serie TEXT UNIQUE,
                data_aquisicao TIMESTAMP NOT NULL,
                valor_aquisicao REAL,
                status TEXT NOT NULL,
                localizacao_atual TEXT,
                responsavel_id TEXT,
                manutencoes TEXT,
                historico_uso TEXT,
                observacoes TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (responsavel_id) REFERENCES colaboradores (id)
            )
        ''')
        
        # Tabela de documentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                pedido_id TEXT NOT NULL,
                caminho_arquivo TEXT NOT NULL,
                tamanho INTEGER,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_upload TEXT NOT NULL,
                assinado BOOLEAN DEFAULT FALSE,
                data_assinatura TIMESTAMP,
                usuario_assinatura TEXT,
                observacoes TEXT,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (usuario_upload) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabela de logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_sistema (
                id TEXT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id TEXT,
                acao TEXT NOT NULL,
                modulo TEXT NOT NULL,
                detalhes TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def executar_query(self, query: str, params: tuple = ()):
        """Executa uma query no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def buscar_dados(self, query: str, params: tuple = ()):
        """Busca dados no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        dados = cursor.fetchall()
        conn.close()
        return dados
    
    def inserir_usuario(self, usuario: Usuario, senha_hash: str):
        """Insere um novo usuário no banco"""
        query = '''
            INSERT INTO usuarios (id, nome, email, senha_hash, tipo, ativo, permissoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            usuario.id, usuario.nome, usuario.email, senha_hash,
            usuario.tipo.value, usuario.ativo, json.dumps(usuario.permissoes)
        )
        self.executar_query(query, params)
    
    def buscar_usuario_por_email(self, email: str):
        """Busca um usuário por email"""
        query = "SELECT * FROM usuarios WHERE email = ? AND ativo = TRUE"
        return self.buscar_dados(query, (email,))
    
    def inserir_produto(self, produto: Produto):
        """Insere um novo produto no banco"""
        query = '''
            INSERT INTO produtos (
                id, nome, categoria, preco_unitario, unidade, descricao,
                ativo, estoque_minimo, estoque_atual, fornecedor,
                codigo_barras, peso, dimensoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            produto.id, produto.nome, produto.categoria, produto.preco_unitario,
            produto.unidade, produto.descricao, produto.ativo, produto.estoque_minimo,
            produto.estoque_atual, produto.fornecedor, produto.codigo_barras,
            produto.peso, produto.dimensoes
        )
        self.executar_query(query, params)
    
    def buscar_produtos_ativos(self):
        """Busca todos os produtos ativos"""
        query = "SELECT * FROM produtos WHERE ativo = TRUE ORDER BY nome"
        return self.buscar_dados(query)
    
    def inserir_pedido(self, pedido: Pedido):
        """Insere um novo pedido no banco"""
        query = '''
            INSERT INTO pedidos (
                id, numero, cliente_nome, cliente_email, cliente_telefone,
                cliente_documento, evento_nome, evento_data_inicio, evento_data_fim,
                evento_local, evento_endereco, evento_observacoes, status,
                prioridade, valor_total, desconto_total, taxa_entrega,
                observacoes_internas, vendedor_id, vendedor_nome,
                equipe_responsavel, documentos_anexados, historico_status,
                coordenadas_entrega, coordenadas_recolhimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            pedido.id, pedido.numero, pedido.cliente_nome, pedido.cliente_email,
            pedido.cliente_telefone, pedido.cliente_documento, pedido.evento_nome,
            pedido.evento_data_inicio, pedido.evento_data_fim, pedido.evento_local,
            pedido.evento_endereco, pedido.evento_observacoes, pedido.status.value,
            pedido.prioridade.value, pedido.valor_total, pedido.desconto_total,
            pedido.taxa_entrega, pedido.observacoes_internas, pedido.vendedor_id,
            pedido.vendedor_nome, pedido.equipe_responsavel,
            json.dumps(pedido.documentos_anexados), json.dumps(pedido.historico_status),
            json.dumps(pedido.coordenadas_entrega), json.dumps(pedido.coordenadas_recolhimento)
        )
        self.executar_query(query, params)
        
        # Inserir itens do pedido
        for item in pedido.itens:
            self.inserir_item_pedido(pedido.id, item)
    
    def inserir_item_pedido(self, pedido_id: str, item: ItemPedido):
        """Insere um item de pedido no banco"""
        query = '''
            INSERT INTO itens_pedido (
                id, pedido_id, produto_id, produto_nome, quantidade,
                diarias, preco_unitario, desconto, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            str(uuid.uuid4()), pedido_id, item.produto_id, item.produto_nome,
            item.quantidade, item.diarias, item.preco_unitario, item.desconto,
            item.observacoes
        )
        self.executar_query(query, params)
    
    def buscar_pedidos(self, filtros: Dict = None):
        """Busca pedidos com filtros opcionais"""
        query = "SELECT * FROM pedidos"
        params = []
        
        if filtros:
            conditions = []
            if 'status' in filtros:
                conditions.append("status = ?")
                params.append(filtros['status'])
            if 'cliente' in filtros:
                conditions.append("cliente_nome LIKE ?")
                params.append(f"%{filtros['cliente']}%")
            if 'data_inicio' in filtros:
                conditions.append("evento_data_inicio >= ?")
                params.append(filtros['data_inicio'])
            if 'data_fim' in filtros:
                conditions.append("evento_data_fim <= ?")
                params.append(filtros['data_fim'])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY data_criacao DESC"
        return self.buscar_dados(query, tuple(params))
    
    def atualizar_status_pedido(self, pedido_id: str, novo_status: StatusPedido, usuario_id: str):
        """Atualiza o status de um pedido"""
        # Buscar histórico atual
        query_historico = "SELECT historico_status FROM pedidos WHERE id = ?"
        resultado = self.buscar_dados(query_historico, (pedido_id,))
        
        historico = []
        if resultado and resultado[0][0]:
            historico = json.loads(resultado[0][0])
        
        # Adicionar nova entrada no histórico
        historico.append({
            'status': novo_status.value,
            'data': datetime.now().isoformat(),
            'usuario': usuario_id
        })
        
        # Atualizar pedido
        query_update = '''
            UPDATE pedidos 
            SET status = ?, historico_status = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (novo_status.value, json.dumps(historico), pedido_id)
        self.executar_query(query_update, params)

# Instância global do banco de dados
db_nexo = DatabaseNexo()

# ==========================================
# SISTEMA DE AUTENTICAÇÃO E SEGURANÇA
# ==========================================

class AuthNexo:
    """Sistema de autenticação do NEXO"""
    
    @staticmethod
    def hash_senha(senha: str) -> str:
        """Gera hash da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    @staticmethod
    def verificar_senha(senha: str, hash_senha: str) -> bool:
        """Verifica se a senha confere com o hash"""
        return AuthNexo.hash_senha(senha) == hash_senha
    
    @staticmethod
    def criar_usuario_padrao():
        """Cria usuários padrão do sistema"""
        usuarios_padrao = [
            ("comercial", "comercial@nexo.com", "123", TipoUsuario.COMERCIAL),
            ("logistica", "logistica@nexo.com", "123", TipoUsuario.LOGISTICA),
            ("campo", "campo@nexo.com", "123", TipoUsuario.CAMPO),
            ("boss", "boss@nexo.com", "123", TipoUsuario.BOSS),
            ("admin", "admin@nexo.com", "admin123", TipoUsuario.ADMIN)
        ]
        
        for nome, email, senha, tipo in usuarios_padrao:
            # Verificar se usuário já existe
            usuario_existente = db_nexo.buscar_usuario_por_email(email)
            if not usuario_existente:
                usuario = Usuario(
                    id=str(uuid.uuid4()),
                    nome=nome.title(),
                    email=email,
                    tipo=tipo,
                    permissoes=AuthNexo.get_permissoes_padrao(tipo)
                )
                senha_hash = AuthNexo.hash_senha(senha)
                db_nexo.inserir_usuario(usuario, senha_hash)
    
    @staticmethod
    def get_permissoes_padrao(tipo: TipoUsuario) -> List[str]:
        """Retorna permissões padrão por tipo de usuário"""
        permissoes = {
            TipoUsuario.COMERCIAL: [
                "criar_pedido", "editar_pedido", "visualizar_pedido",
                "gerar_orcamento", "visualizar_catalogo", "visualizar_clientes"
            ],
            TipoUsuario.LOGISTICA: [
                "visualizar_pedido", "atualizar_status_pedido", "gerenciar_equipe",
                "gerenciar_documentos", "visualizar_tarefas", "alocar_recursos"
            ],
            TipoUsuario.CAMPO: [
                "visualizar_pedido_campo", "atualizar_entrega", "atualizar_recolhimento",
                "capturar_assinatura", "tirar_fotos", "registrar_gps"
            ],
            TipoUsuario.BOSS: [
                "visualizar_dashboard", "visualizar_relatorios", "visualizar_kpis",
                "exportar_dados", "visualizar_financeiro", "visualizar_performance"
            ],
            TipoUsuario.ADMIN: [
                "gerenciar_usuarios", "gerenciar_sistema", "visualizar_logs",
                "backup_dados", "configurar_sistema", "todas_permissoes"
            ]
        }
        return permissoes.get(tipo, [])
    
    @staticmethod
    def autenticar_usuario(email: str, senha: str) -> Optional[Dict]:
        """Autentica um usuário"""
        usuario_data = db_nexo.buscar_usuario_por_email(email)
        
        if usuario_data:
            usuario = usuario_data[0]
            if AuthNexo.verificar_senha(senha, usuario[3]):  # usuario[3] é senha_hash
                logger_nexo.log_login(usuario[0], True)
                return {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2],
                    'tipo': usuario[4],
                    'ativo': usuario[5],
                    'permissoes': json.loads(usuario[8]) if usuario[8] else []
                }
        
        logger_nexo.log_login(email, False)
        return None
    
    @staticmethod
    def verificar_permissao(usuario: Dict, permissao: str) -> bool:
        """Verifica se o usuário tem uma permissão específica"""
        if not usuario:
            return False
        
        permissoes = usuario.get('permissoes', [])
        return permissao in permissoes or 'todas_permissoes' in permissoes

# ==========================================
# SISTEMA DE CATÁLOGO DE PRODUTOS
# ==========================================

class CatalogoNexo:
    """Sistema de catálogo de produtos do NEXO"""
    
    @staticmethod
    def carregar_produtos_padrao():
        """Carrega produtos padrão no sistema"""
        produtos_padrao = [
            # Equipamentos de Som
            ("Caixa de Som JBL 15\"", "Som", 150.0, "unidade", "Caixa de som profissional JBL 15 polegadas"),
            ("Microfone Shure SM58", "Som", 80.0, "unidade", "Microfone dinâmico profissional"),
            ("Mesa de Som Yamaha 16 Canais", "Som", 300.0, "unidade", "Mesa de som digital 16 canais"),
            ("Amplificador Crown 2000W", "Som", 200.0, "unidade", "Amplificador de potência profissional"),
            ("Cabo XLR 10m", "Som", 25.0, "unidade", "Cabo balanceado XLR macho/fêmea 10 metros"),
            
            # Equipamentos de Iluminação
            ("Refletor LED 200W", "Iluminação", 120.0, "unidade", "Refletor LED RGB 200W com controle DMX"),
            ("Moving Head Beam 230W", "Iluminação", 400.0, "unidade", "Moving head beam profissional 230W"),
            ("Par LED 54x3W", "Iluminação", 180.0, "unidade", "Par LED RGB 54x3W com controle DMX"),
            ("Máquina de Fumaça 1500W", "Iluminação", 250.0, "unidade", "Máquina de fumaça profissional 1500W"),
            ("Mesa DMX 512", "Iluminação", 350.0, "unidade", "Mesa de controle DMX 512 canais"),
            
            # Estruturas e Tendas
            ("Tenda 10x10m", "Estrutura", 800.0, "unidade", "Tenda de lona 10x10 metros com estrutura"),
            ("Palco 8x6m", "Estrutura", 1200.0, "unidade", "Palco modular 8x6 metros altura 1m"),
            ("Treliça Q30 3m", "Estrutura", 150.0, "unidade", "Treliça quadrada Q30 3 metros"),
            ("Pé de Treliça 3m", "Estrutura", 80.0, "unidade", "Pé de treliça telescópico até 3 metros"),
            ("Cerca Móvel", "Estrutura", 45.0, "unidade", "Cerca móvel galvanizada 2x1m"),
            
            # Mobiliário
            ("Mesa Redonda 1,60m", "Mobiliário", 35.0, "unidade", "Mesa redonda tampo 1,60m para 8 pessoas"),
            ("Cadeira Plástica", "Mobiliário", 8.0, "unidade", "Cadeira plástica branca empilhável"),
            ("Cadeira Tiffany", "Mobiliário", 15.0, "unidade", "Cadeira Tiffany transparente"),
            ("Toalha Mesa Redonda", "Mobiliário", 12.0, "unidade", "Toalha para mesa redonda 1,60m"),
            ("Balcão Bar", "Mobiliário", 120.0, "unidade", "Balcão bar com tampo em granito"),
            
            # Equipamentos de Energia
            ("Gerador 15KVA", "Energia", 500.0, "unidade", "Gerador diesel silenciado 15KVA"),
            ("Quadro de Distribuição", "Energia", 180.0, "unidade", "Quadro elétrico com 12 tomadas"),
            ("Cabo de Força 50m", "Energia", 120.0, "unidade", "Cabo de força 4mm² 50 metros"),
            ("Extensão 20m", "Energia", 35.0, "unidade", "Extensão elétrica 20 metros"),
            ("Disjuntor 32A", "Energia", 25.0, "unidade", "Disjuntor tripolar 32 amperes"),
            
            # Equipamentos de Segurança
            ("Extintor PQS 6kg", "Segurança", 45.0, "unidade", "Extintor pó químico seco 6kg"),
            ("Cone de Sinalização", "Segurança", 15.0, "unidade", "Cone de sinalização laranja 75cm"),
            ("Fita Zebrada", "Segurança", 8.0, "metro", "Fita zebrada para isolamento"),
            ("Placa de Sinalização", "Segurança", 25.0, "unidade", "Placa de sinalização personalizada"),
            ("Kit Primeiros Socorros", "Segurança", 80.0, "unidade", "Kit completo primeiros socorros"),
            
            # Decoração
            ("Arranjo Floral Grande", "Decoração", 180.0, "unidade", "Arranjo floral grande para mesa principal"),
            ("Vaso Decorativo", "Decoração", 45.0, "unidade", "Vaso decorativo cerâmica grande"),
            ("Tecido Voil 10m", "Decoração", 60.0, "unidade", "Tecido voil para decoração 10 metros"),
            ("Balão Metalizado", "Decoração", 12.0, "unidade", "Balão metalizado números ou letras"),
            ("Painel de Flores", "Decoração", 350.0, "unidade", "Painel decorativo com flores artificiais"),
            
            # Equipamentos de Cozinha
            ("Fogão Industrial 4 Bocas", "Cozinha", 200.0, "unidade", "Fogão industrial inox 4 bocas"),
            ("Geladeira 300L", "Cozinha", 150.0, "unidade", "Geladeira comercial 300 litros"),
            ("Freezer Horizontal", "Cozinha", 180.0, "unidade", "Freezer horizontal 400 litros"),
            ("Panela Pressão 20L", "Cozinha", 80.0, "unidade", "Panela de pressão industrial 20 litros"),
            ("Botijão Gás 45kg", "Cozinha", 120.0, "unidade", "Botijão de gás 45kg com regulador"),
            
            # Equipamentos de Limpeza
            ("Aspirador Industrial", "Limpeza", 120.0, "unidade", "Aspirador de pó e água industrial"),
            ("Lavadora Alta Pressão", "Limpeza", 180.0, "unidade", "Lavadora alta pressão 2200 libras"),
            ("Carrinho de Limpeza", "Limpeza", 85.0, "unidade", "Carrinho completo para limpeza"),
            ("Balde com Espremedor", "Limpeza", 25.0, "unidade", "Balde 20L com espremedor"),
            ("Kit Produtos Limpeza", "Limpeza", 45.0, "unidade", "Kit completo produtos de limpeza"),
            
            # Transporte e Logística
            ("Carrinho de Carga", "Transporte", 120.0, "unidade", "Carrinho de carga capacidade 300kg"),
            ("Corda Nylon 50m", "Transporte", 35.0, "unidade", "Corda nylon 12mm 50 metros"),
            ("Cinta Catraca 5m", "Transporte", 28.0, "unidade", "Cinta com catraca 5 metros"),
            ("Lona Encerada 6x4m", "Transporte", 80.0, "unidade", "Lona encerada 6x4 metros"),
            ("Palete Madeira", "Transporte", 45.0, "unidade", "Palete de madeira 1,20x1,00m")
        ]
        
        for nome, categoria, preco, unidade, descricao in produtos_padrao:
            # Verificar se produto já existe
            produtos_existentes = db_nexo.buscar_dados(
                "SELECT id FROM produtos WHERE nome = ?", (nome,)
            )
            
            if not produtos_existentes:
                produto = Produto(
                    id=str(uuid.uuid4()),
                    nome=nome,
                    categoria=categoria,
                    preco_unitario=preco,
                    unidade=unidade,
                    descricao=descricao,
                    estoque_atual=10,  # Estoque inicial
                    estoque_minimo=2
                )
                db_nexo.inserir_produto(produto)
    
    @staticmethod
    def buscar_produtos(filtros: Dict = None) -> List[Dict]:
        """Busca produtos com filtros opcionais"""
        query = "SELECT * FROM produtos WHERE ativo = TRUE"
        params = []
        
        if filtros:
            if 'categoria' in filtros and filtros['categoria']:
                query += " AND categoria = ?"
                params.append(filtros['categoria'])
            if 'nome' in filtros and filtros['nome']:
                query += " AND nome LIKE ?"
                params.append(f"%{filtros['nome']}%")
        
        query += " ORDER BY categoria, nome"
        produtos_data = db_nexo.buscar_dados(query, tuple(params))
        
        produtos = []
        for produto_data in produtos_data:
            produtos.append({
                'id': produto_data[0],
                'nome': produto_data[1],
                'categoria': produto_data[2],
                'preco_unitario': produto_data[3],
                'unidade': produto_data[4],
                'descricao': produto_data[5],
                'ativo': produto_data[6],
                'estoque_minimo': produto_data[7],
                'estoque_atual': produto_data[8],
                'fornecedor': produto_data[9],
                'codigo_barras': produto_data[10],
                'peso': produto_data[11],
                'dimensoes': produto_data[12]
            })
        
        return produtos
    
    @staticmethod
    def get_categorias() -> List[str]:
        """Retorna lista de categorias disponíveis"""
        query = "SELECT DISTINCT categoria FROM produtos WHERE ativo = TRUE ORDER BY categoria"
        categorias_data = db_nexo.buscar_dados(query)
        return [cat[0] for cat in categorias_data]

# ==========================================
# SISTEMA DE GERAÇÃO DE PDF
# ==========================================

class PDFGeneratorNexo:
    """Sistema de geração de PDFs do NEXO"""
    
    @staticmethod
    def gerar_orcamento(pedido: Dict, itens: List[Dict]) -> bytes:
        """Gera PDF do orçamento"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Cabeçalho
        pdf.cell(0, 10, 'PRIMEIRA LINHA EVENTOS', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'NEXO - Núcleo de Excelência Operacional', 0, 1, 'C')
        pdf.ln(10)
        
        # Informações do orçamento
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'ORÇAMENTO Nº: {pedido["numero"]}', 0, 1)
        pdf.cell(0, 8, f'DATA: {datetime.now().strftime("%d/%m/%Y")}', 0, 1)
        pdf.ln(5)
        
        # Dados do cliente
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'DADOS DO CLIENTE:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f'Nome: {pedido["cliente_nome"]}', 0, 1)
        pdf.cell(0, 6, f'E-mail: {pedido["cliente_email"]}', 0, 1)
        pdf.cell(0, 6, f'Telefone: {pedido["cliente_telefone"]}', 0, 1)
        pdf.cell(0, 6, f'Documento: {pedido["cliente_documento"]}', 0, 1)
        pdf.ln(5)
        
        # Dados do evento
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'DADOS DO EVENTO:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f'Evento: {pedido["evento_nome"]}', 0, 1)
        pdf.cell(0, 6, f'Local: {pedido["evento_local"]}', 0, 1)
        pdf.cell(0, 6, f'Endereço: {pedido["evento_endereco"]}', 0, 1)
        
        data_inicio = datetime.fromisoformat(pedido["evento_data_inicio"]).strftime("%d/%m/%Y")
        data_fim = datetime.fromisoformat(pedido["evento_data_fim"]).strftime("%d/%m/%Y")
        pdf.cell(0, 6, f'Período: {data_inicio} a {data_fim}', 0, 1)
        pdf.ln(10)
        
        # Tabela de itens
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'ITENS DO ORÇAMENTO:', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(80, 8, 'ITEM', 1, 0, 'C')
        pdf.cell(20, 8, 'QTD', 1, 0, 'C')
        pdf.cell(20, 8, 'DIÁRIAS', 1, 0, 'C')
        pdf.cell(25, 8, 'VALOR UNIT.', 1, 0, 'C')
        pdf.cell(25, 8, 'SUBTOTAL', 1, 1, 'C')
        
        # Itens
        pdf.set_font('Arial', '', 8)
        total_geral = 0
        
        for item in itens:
            subtotal = item['quantidade'] * item['diarias'] * item['preco_unitario']
            total_geral += subtotal
            
            pdf.cell(80, 6, item['produto_nome'][:35], 1, 0)
            pdf.cell(20, 6, str(item['quantidade']), 1, 0, 'C')
            pdf.cell(20, 6, str(item['diarias']), 1, 0, 'C')
            pdf.cell(25, 6, f'R$ {item["preco_unitario"]:.2f}', 1, 0, 'R')
            pdf.cell(25, 6, f'R$ {subtotal:.2f}', 1, 1, 'R')
        
        # Total
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(145, 8, 'TOTAL GERAL:', 1, 0, 'R')
        pdf.cell(25, 8, f'R$ {total_geral:.2f}', 1, 1, 'R')
        pdf.ln(10)
        
        # Observações
        if pedido.get("evento_observacoes"):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'OBSERVAÇÕES:', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, pedido["evento_observacoes"])
            pdf.ln(5)
        
        # Rodapé
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 6, 'Este orçamento é válido por 15 dias a partir da data de emissão.', 0, 1, 'C')
        pdf.cell(0, 6, 'Primeira Linha Eventos - NEXO Sistema de Gestão', 0, 1, 'C')
        pdf.cell(0, 6, f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}', 0, 1, 'C')
        
        return pdf.output(dest='S').encode('latin-1')
    
    @staticmethod
    def gerar_ordem_separacao(pedido: Dict, itens: List[Dict]) -> bytes:
        """Gera PDF da ordem de separação"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Cabeçalho
        pdf.cell(0, 10, 'ORDEM DE SEPARAÇÃO', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'PRIMEIRA LINHA EVENTOS - NEXO', 0, 1, 'C')
        pdf.ln(10)
        
        # Informações do pedido
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'PEDIDO Nº: {pedido["numero"]}', 0, 1)
        pdf.cell(0, 8, f'CLIENTE: {pedido["cliente_nome"]}', 0, 1)
        pdf.cell(0, 8, f'EVENTO: {pedido["evento_nome"]}', 0, 1)
        
        data_inicio = datetime.fromisoformat(pedido["evento_data_inicio"]).strftime("%d/%m/%Y")
        data_fim = datetime.fromisoformat(pedido["evento_data_fim"]).strftime("%d/%m/%Y")
        pdf.cell(0, 8, f'PERÍODO: {data_inicio} a {data_fim}', 0, 1)
        pdf.ln(10)
        
        # Tabela de itens para separação
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'ITENS PARA SEPARAÇÃO:', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(20, 8, 'QTD', 1, 0, 'C')
        pdf.cell(100, 8, 'ITEM', 1, 0, 'C')
        pdf.cell(30, 8, 'CATEGORIA', 1, 0, 'C')
        pdf.cell(20, 8, 'OK', 1, 1, 'C')
        
        # Itens
        pdf.set_font('Arial', '', 9)
        for item in itens:
            pdf.cell(20, 8, str(item['quantidade']), 1, 0, 'C')
            pdf.cell(100, 8, item['produto_nome'][:45], 1, 0)
            pdf.cell(30, 8, 'Equipamento', 1, 0, 'C')  # Categoria simplificada
            pdf.cell(20, 8, '[ ]', 1, 1, 'C')
        
        pdf.ln(10)
        
        # Assinaturas
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'RESPONSÁVEIS:', 0, 1)
        pdf.ln(10)
        
        pdf.cell(85, 8, 'Separado por: ________________________', 0, 0)
        pdf.cell(85, 8, 'Conferido por: ________________________', 0, 1)
        pdf.ln(5)
        pdf.cell(85, 8, 'Data: ____/____/____', 0, 0)
        pdf.cell(85, 8, 'Data: ____/____/____', 0, 1)
        
        pdf.ln(15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 6, f'Documento gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}', 0, 1, 'C')
        
        return pdf.output(dest='S').encode('latin-1')
    
    @staticmethod
    def gerar_romaneio_entrega(pedido: Dict, itens: List[Dict]) -> bytes:
        """Gera PDF do romaneio de entrega"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Cabeçalho
        pdf.cell(0, 10, 'ROMANEIO DE ENTREGA', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'PRIMEIRA LINHA EVENTOS - NEXO', 0, 1, 'C')
        pdf.ln(10)
        
        # Informações do pedido
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'PEDIDO Nº: {pedido["numero"]}', 0, 1)
        pdf.cell(0, 8, f'CLIENTE: {pedido["cliente_nome"]}', 0, 1)
        pdf.cell(0, 8, f'EVENTO: {pedido["evento_nome"]}', 0, 1)
        pdf.cell(0, 8, f'LOCAL: {pedido["evento_local"]}', 0, 1)
        pdf.cell(0, 8, f'ENDEREÇO: {pedido["evento_endereco"]}', 0, 1)
        
        data_inicio = datetime.fromisoformat(pedido["evento_data_inicio"]).strftime("%d/%m/%Y")
        pdf.cell(0, 8, f'DATA ENTREGA: {data_inicio}', 0, 1)
        pdf.ln(10)
        
        # Tabela de itens
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'ITENS PARA ENTREGA:', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(20, 8, 'QTD', 1, 0, 'C')
        pdf.cell(90, 8, 'ITEM', 1, 0, 'C')
        pdf.cell(25, 8, 'DIÁRIAS', 1, 0, 'C')
        pdf.cell(35, 8, 'ENTREGUE', 1, 1, 'C')
        
        # Itens
        pdf.set_font('Arial', '', 9)
        for item in itens:
            pdf.cell(20, 8, str(item['quantidade']), 1, 0, 'C')
            pdf.cell(90, 8, item['produto_nome'][:40], 1, 0)
            pdf.cell(25, 8, str(item['diarias']), 1, 0, 'C')
            pdf.cell(35, 8, '[ ] OK', 1, 1, 'C')
        
        pdf.ln(10)
        
        # Observações de entrega
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'OBSERVAÇÕES DA ENTREGA:', 0, 1)
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 30, '', 1, 1)  # Espaço para observações
        
        pdf.ln(5)
        
        # Assinaturas
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'ASSINATURAS:', 0, 1)
        pdf.ln(5)
        
        pdf.cell(85, 8, 'Entregue por: ________________________', 0, 0)
        pdf.cell(85, 8, 'Recebido por: ________________________', 0, 1)
        pdf.ln(5)
        pdf.cell(85, 8, 'Data: ____/____/____ Hora: ____:____', 0, 0)
        pdf.cell(85, 8, 'CPF: ________________________', 0, 1)
        
        pdf.ln(15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 6, f'Documento gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}', 0, 1, 'C')
        
        return pdf.output(dest='S').encode('latin-1')

# ==========================================
# SISTEMA DE NOTIFICAÇÕES
# ==========================================

class NotificacaoNexo:
    """Sistema de notificações do NEXO"""
    
    @staticmethod
    def mostrar_sucesso(mensagem: str):
        """Mostra notificação de sucesso"""
        st.success(f"✅ {mensagem}")
    
    @staticmethod
    def mostrar_erro(mensagem: str):
        """Mostra notificação de erro"""
        st.error(f"❌ {mensagem}")
    
    @staticmethod
    def mostrar_aviso(mensagem: str):
        """Mostra notificação de aviso"""
        st.warning(f"⚠️ {mensagem}")
    
    @staticmethod
    def mostrar_info(mensagem: str):
        """Mostra notificação de informação"""
        st.info(f"ℹ️ {mensagem}")
    
    @staticmethod
    def criar_alerta_personalizado(tipo: str, titulo: str, mensagem: str):
        """Cria alerta personalizado com HTML"""
        classe_css = f"alert alert-{tipo}"
        st.markdown(f"""
            <div class="{classe_css}">
                <strong>{titulo}</strong><br>
                {mensagem}
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# SISTEMA DE VALIDAÇÕES
# ==========================================

class ValidadorNexo:
    """Sistema de validações do NEXO"""
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida formato de telefone brasileiro"""
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'\D', '', telefone)
        # Verifica se tem 10 ou 11 dígitos
        return len(telefone_limpo) in [10, 11]
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos calculados conferem
        return cpf[-2:] == f"{digito1}{digito2}"
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """Valida CNPJ brasileiro"""
        # Remove caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calcula primeiro dígito verificador
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos calculados conferem
        return cnpj[-2:] == f"{digito1}{digito2}"
    
    @staticmethod
    def validar_data(data_str: str) -> bool:
        """Valida formato de data"""
        try:
            datetime.strptime(data_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_valor_monetario(valor: str) -> bool:
        """Valida formato de valor monetário"""
        try:
            float(valor.replace(',', '.'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_campos_obrigatorios(dados: Dict, campos: List[str]) -> List[str]:
        """Valida se campos obrigatórios estão preenchidos"""
        erros = []
        for campo in campos:
            if campo not in dados or not dados[campo]:
                erros.append(f"Campo '{campo}' é obrigatório")
        return erros

# ==========================================
# SISTEMA DE BACKUP E RECUPERAÇÃO
# ==========================================

class BackupNexo:
    """Sistema de backup e recuperação do NEXO"""
    
    @staticmethod
    def criar_backup() -> str:
        """Cria backup dos dados do sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_data = {
            'timestamp': timestamp,
            'versao': '1.0',
            'dados': {
                'pedidos': st.session_state.get('pedidos', []),
                'colaboradores': st.session_state.get('colaboradores', []),
                'equipamentos': st.session_state.get('equipamentos', []),
                'documentos': st.session_state.get('documentos', []),
                'logs': st.session_state.get('logs_sistema', [])
            }
        }
        
        backup_json = json.dumps(backup_data, indent=2, default=str)
        backup_filename = f"backup_nexo_{timestamp}.json"
        
        # Salvar no session_state para download
        st.session_state.ultimo_backup = {
            'filename': backup_filename,
            'data': backup_json,
            'timestamp': timestamp
        }
        
        return backup_filename
    
    @staticmethod
    def restaurar_backup(backup_data: str) -> bool:
        """Restaura dados do backup"""
        try:
            dados = json.loads(backup_data)
            
            if 'dados' in dados:
                for chave, valor in dados['dados'].items():
                    st.session_state[chave] = valor
                
                NotificacaoNexo.mostrar_sucesso("Backup restaurado com sucesso!")
                return True
            else:
                NotificacaoNexo.mostrar_erro("Formato de backup inválido!")
                return False
                
        except json.JSONDecodeError:
            NotificacaoNexo.mostrar_erro("Erro ao decodificar arquivo de backup!")
            return False
        except Exception as e:
            NotificacaoNexo.mostrar_erro(f"Erro ao restaurar backup: {str(e)}")
            return False

# ==========================================
# INICIALIZAÇÃO DO SISTEMA
# ==========================================

def init_session_state():
    """Inicializa o estado da sessão com dados limpos"""
    
    # Estado de autenticação
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if 'tentativas_login' not in st.session_state:
        st.session_state.tentativas_login = 0
    
    # Dados principais do sistema (ZERADOS)
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = []
    
    if 'colaboradores' not in st.session_state:
        st.session_state.colaboradores = []
    
    if 'equipamentos' not in st.session_state:
        st.session_state.equipamentos = []
    
    if 'documentos' not in st.session_state:
        st.session_state.documentos = []
    
    if 'tarefas_galpao' not in st.session_state:
        st.session_state.tarefas_galpao = []
    
    if 'logs_sistema' not in st.session_state:
        st.session_state.logs_sistema = []
    
    # Configurações da interface
    if 'interface_atual' not in st.session_state:
        st.session_state.interface_atual = 'login'
    
    if 'aba_comercial' not in st.session_state:
        st.session_state.aba_comercial = 'Dashboard'
    
    if 'aba_logistica' not in st.session_state:
        st.session_state.aba_logistica = 'Dashboard'
    
    if 'aba_campo' not in st.session_state:
        st.session_state.aba_campo = 'Pedidos Designados'
    
    if 'aba_boss' not in st.session_state:
        st.session_state.aba_boss = 'Dashboard Executivo'
    
    # Dados temporários para formulários
    if 'novo_pedido_itens' not in st.session_state:
        st.session_state.novo_pedido_itens = []
    
    if 'contador_produtos' not in st.session_state:
        st.session_state.contador_produtos = 1
    
    if 'orcamento_gerado' not in st.session_state:
        st.session_state.orcamento_gerado = None
    
    # Filtros e buscas
    if 'filtro_status_pedidos' not in st.session_state:
        st.session_state.filtro_status_pedidos = 'Todos'
    
    if 'filtro_categoria_produtos' not in st.session_state:
        st.session_state.filtro_categoria_produtos = 'Todas'
    
    if 'busca_cliente' not in st.session_state:
        st.session_state.busca_cliente = ''
    
    # Configurações de GPS e localização
    if 'gps_ativo' not in st.session_state:
        st.session_state.gps_ativo = False
    
    if 'localizacao_atual' not in st.session_state:
        st.session_state.localizacao_atual = None
    
    # Configurações de notificações
    if 'notificacoes_ativas' not in st.session_state:
        st.session_state.notificacoes_ativas = True
    
    if 'som_notificacoes' not in st.session_state:
        st.session_state.som_notificacoes = True
    
    # Dados de performance e métricas (ZERADOS)
    if 'metricas_comercial' not in st.session_state:
        st.session_state.metricas_comercial = {
            'pedidos_mes': 0,
            'faturamento_mes': 0.0,
            'conversao_orcamentos': 0.0,
            'ticket_medio': 0.0
        }
    
    if 'metricas_logistica' not in st.session_state:
        st.session_state.metricas_logistica = {
            'pedidos_preparados': 0,
            'pedidos_entregues': 0,
            'tempo_medio_preparacao': 0,
            'eficiencia_equipe': 0.0
        }
    
    if 'metricas_campo' not in st.session_state:
        st.session_state.metricas_campo = {
            'entregas_realizadas': 0,
            'recolhimentos_realizados': 0,
            'tempo_medio_entrega': 0,
            'satisfacao_cliente': 0.0
        }
    
    # Configurações do sistema
    if 'configuracoes_sistema' not in st.session_state:
        st.session_state.configuracoes_sistema = {
            'empresa_nome': 'Primeira Linha Eventos',
            'empresa_cnpj': '00.000.000/0001-00',
            'empresa_telefone': '(11) 99999-9999',
            'empresa_email': 'contato@primeiralinhaventos.com.br',
            'empresa_endereco': 'Rua das Empresas, 123 - São Paulo/SP',
            'sistema_versao': '1.0.0',
            'sistema_ambiente': 'producao',
            'backup_automatico': True,
            'logs_detalhados': True
        }

def carregar_dados_iniciais():
    """Carrega dados iniciais do sistema"""
    # Criar usuários padrão
    AuthNexo.criar_usuario_padrao()
    
    # Carregar produtos padrão
    CatalogoNexo.carregar_produtos_padrao()
    
    # Log de inicialização
    logger_nexo.logger.info("Sistema NEXO inicializado com sucesso")

# ==========================================
# INTERFACE DE LOGIN
# ==========================================

def interface_login():
    """Interface de login do sistema"""
    st.markdown(CSS_NEXO_ULTRA, unsafe_allow_html=True)
    
    # Container centralizado para login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-container fade-in">
                <div class="nexo-logo">NEXO</div>
                <div class="nexo-subtitle">Núcleo de Excelência Operacional</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Acesso ao Sistema")
        
        # Formulário de login
        with st.form("form_login", clear_on_submit=False):
            email = st.text_input(
                "📧 Email:",
                placeholder="Digite seu email",
                key="login_email"
            )
            
            senha = st.text_input(
                "🔒 Senha:",
                type="password",
                placeholder="Digite sua senha",
                key="login_senha"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                btn_login = st.form_submit_button(
                    "🚀 ENTRAR",
                    use_container_width=True
                )
            
            with col_btn2:
                btn_demo = st.form_submit_button(
                    "👁️ DEMO",
                    use_container_width=True
                )
        
        # Processamento do login
        if btn_login:
            if email and senha:
                usuario = AuthNexo.autenticar_usuario(email, senha)
                
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.session_state.tentativas_login = 0
                    
                    # Definir interface baseada no tipo de usuário
                    tipo_usuario = usuario['tipo']
                    if tipo_usuario == 'comercial':
                        st.session_state.interface_atual = 'comercial'
                    elif tipo_usuario == 'logistica':
                        st.session_state.interface_atual = 'logistica'
                    elif tipo_usuario == 'campo':
                        st.session_state.interface_atual = 'campo'
                    elif tipo_usuario == 'boss':
                        st.session_state.interface_atual = 'boss'
                    elif tipo_usuario == 'admin':
                        st.session_state.interface_atual = 'admin'
                    
                    NotificacaoNexo.mostrar_sucesso(f"Bem-vindo, {usuario['nome']}!")
                    st.rerun()
                else:
                    st.session_state.tentativas_login += 1
                    NotificacaoNexo.mostrar_erro("Email ou senha incorretos!")
                    
                    if st.session_state.tentativas_login >= 3:
                        NotificacaoNexo.mostrar_aviso("Muitas tentativas. Aguarde alguns minutos.")
            else:
                NotificacaoNexo.mostrar_aviso("Preencha email e senha!")
        
        # Modo demo
        if btn_demo:
            st.session_state.usuario_logado = {
                'id': 'demo',
                'nome': 'Usuário Demo',
                'email': 'demo@nexo.com',
                'tipo': 'boss',
                'permissoes': ['todas_permissoes']
            }
            st.session_state.interface_atual = 'boss'
            NotificacaoNexo.mostrar_info("Modo demonstração ativado!")
            st.rerun()
        
        # Informações de acesso
        st.markdown("---")
        st.markdown("### 📋 Usuários de Teste")
        
        usuarios_teste = [
            ("comercial@nexo.com", "123", "Comercial"),
            ("logistica@nexo.com", "123", "Logística"),
            ("campo@nexo.com", "123", "Campo"),
            ("boss@nexo.com", "123", "Boss")
        ]
        
        for email, senha, tipo in usuarios_teste:
            st.markdown(f"**{tipo}:** {email} / {senha}")

# ==========================================
# INTERFACE COMERCIAL
# ==========================================

def interface_comercial():
    """Interface do módulo comercial"""
    st.markdown(CSS_NEXO_ULTRA, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
        <div class="nexo-header">
            <div>
                <div class="nexo-logo">NEXO</div>
                <div class="nexo-subtitle">Módulo Comercial</div>
            </div>
            <div style="text-align: right;">
                <strong>{st.session_state.usuario_logado['nome']}</strong><br>
                <small>{datetime.now().strftime('%d/%m/%Y %H:%M')}</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navegação
    abas = ['Dashboard', 'Novo Pedido', 'Gestão de Pedidos', 'Catálogo', 'Orçamentos', 'Clientes']
    
    st.markdown('<div class="nexo-nav">', unsafe_allow_html=True)
    cols = st.columns(len(abas) + 1)
    
    for i, aba in enumerate(abas):
        with cols[i]:
            if st.button(
                aba,
                key=f"nav_comercial_{aba}",
                use_container_width=True
            ):
                st.session_state.aba_comercial = aba
    
    with cols[-1]:
        if st.button("🚪 Sair", key="logout_comercial", use_container_width=True):
            st.session_state.usuario_logado = None
            st.session_state.interface_atual = 'login'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Conteúdo das abas
    aba_atual = st.session_state.aba_comercial
    
    if aba_atual == 'Dashboard':
        dashboard_comercial()
    elif aba_atual == 'Novo Pedido':
        novo_pedido_comercial()
    elif aba_atual == 'Gestão de Pedidos':
        gestao_pedidos_comercial()
    elif aba_atual == 'Catálogo':
        catalogo_comercial()
    elif aba_atual == 'Orçamentos':
        orcamentos_comercial()
    elif aba_atual == 'Clientes':
        clientes_comercial()

def dashboard_comercial():
    """Dashboard do módulo comercial"""
    st.markdown("## 📊 Dashboard Comercial")
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular métricas reais dos pedidos
    pedidos = st.session_state.pedidos
    pedidos_mes = len([p for p in pedidos if datetime.fromisoformat(p['data_criacao']).month == datetime.now().month])
    faturamento_mes = sum([p['valor_total'] for p in pedidos if datetime.fromisoformat(p['data_criacao']).month == datetime.now().month])
    orcamentos_mes = len([p for p in pedidos if p['status'] == StatusPedido.ORCAMENTO.value])
    conversao = (pedidos_mes / max(orcamentos_mes, 1)) * 100 if orcamentos_mes > 0 else 0
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pedidos_mes}</div>
                <div class="metric-label">Pedidos no Mês</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {faturamento_mes:,.2f}</div>
                <div class="metric-label">Faturamento</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{conversao:.1f}%</div>
                <div class="metric-label">Conversão</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ticket_medio = faturamento_mes / max(pedidos_mes, 1) if pedidos_mes > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {ticket_medio:,.2f}</div>
                <div class="metric-label">Ticket Médio</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Pedidos por Status")
        
        if pedidos:
            # Contar pedidos por status
            status_counts = {}
            for pedido in pedidos:
                status = pedido['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Criar gráfico de pizza
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Distribuição de Pedidos por Status",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum pedido cadastrado ainda.")
    
    with col2:
        st.markdown("### 💰 Faturamento por Mês")
        
        if pedidos:
            # Agrupar faturamento por mês
            faturamento_mensal = {}
            for pedido in pedidos:
                mes = datetime.fromisoformat(pedido['data_criacao']).strftime('%Y-%m')
                faturamento_mensal[mes] = faturamento_mensal.get(mes, 0) + pedido['valor_total']
            
            # Criar gráfico de barras
            fig = px.bar(
                x=list(faturamento_mensal.keys()),
                y=list(faturamento_mensal.values()),
                title="Faturamento Mensal",
                labels={'x': 'Mês', 'y': 'Faturamento (R$)'},
                color_discrete_sequence=[CORES_NEXO['laranja_primario']]
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado de faturamento disponível.")
    
    # Tabela de pedidos recentes
    st.markdown("### 📋 Pedidos Recentes")
    
    if pedidos:
        # Mostrar os 5 pedidos mais recentes
        pedidos_recentes = sorted(pedidos, key=lambda x: x['data_criacao'], reverse=True)[:5]
        
        dados_tabela = []
        for pedido in pedidos_recentes:
            dados_tabela.append({
                'Número': pedido['numero'],
                'Cliente': pedido['cliente_nome'],
                'Evento': pedido['evento_nome'],
                'Status': pedido['status'],
                'Valor': f"R$ {pedido['valor_total']:,.2f}",
                'Data': datetime.fromisoformat(pedido['data_criacao']).strftime('%d/%m/%Y')
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pedido cadastrado ainda.")
    
    # Ações rápidas
    st.markdown("### ⚡ Ações Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Novo Pedido", use_container_width=True):
            st.session_state.aba_comercial = 'Novo Pedido'
            st.rerun()
    
    with col2:
        if st.button("📄 Gerar Orçamento", use_container_width=True):
            st.session_state.aba_comercial = 'Orçamentos'
            st.rerun()
    
    with col3:
        if st.button("👥 Ver Clientes", use_container_width=True):
            st.session_state.aba_comercial = 'Clientes'
            st.rerun()
    
    with col4:
        if st.button("📦 Ver Catálogo", use_container_width=True):
            st.session_state.aba_comercial = 'Catálogo'
            st.rerun()

def novo_pedido_comercial():
    """Formulário para novo pedido"""
    st.markdown("## ➕ Novo Pedido")
    
    # Formulário principal
    with st.form("form_novo_pedido", clear_on_submit=False):
        st.markdown("### 👤 Dados do Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_nome = st.text_input(
                "Nome Completo *",
                placeholder="Digite o nome do cliente"
            )
            
            cliente_email = st.text_input(
                "Email *",
                placeholder="cliente@email.com"
            )
        
        with col2:
            cliente_telefone = st.text_input(
                "Telefone *",
                placeholder="(11) 99999-9999"
            )
            
            cliente_documento = st.text_input(
                "CPF/CNPJ *",
                placeholder="000.000.000-00"
            )
        
        st.markdown("### 🎉 Dados do Evento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            evento_nome = st.text_input(
                "Nome do Evento *",
                placeholder="Ex: Casamento João e Maria"
            )
            
            evento_local = st.text_input(
                "Local do Evento *",
                placeholder="Ex: Salão de Festas ABC"
            )
            
            evento_data_inicio = st.date_input(
                "Data de Início *",
                min_value=datetime.now().date()
            )
        
        with col2:
            evento_endereco = st.text_area(
                "Endereço Completo *",
                placeholder="Rua, número, bairro, cidade, CEP"
            )
            
            evento_data_fim = st.date_input(
                "Data de Término *",
                min_value=datetime.now().

