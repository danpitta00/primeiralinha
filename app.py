"""
Dashboard Primeira Linha Eventos - Versão Simplificada
Funciona 100% no Render.com
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# URL da planilha Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H07FB3X_tkSLSoHx-F2kyDmNQIGR4EyyTjnF-u19G3c/export?format=csv&gid=0"

def clean_currency(value ):
    """Limpa valores monetários"""
    if pd.isna(value) or value == '':
        return 0.0
    if isinstance(value, str):
        value = re.sub(r'[^\d,.]', '', str(value))
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return 0.0

def load_data():
    """Carrega dados da planilha"""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Renomeia colunas
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
        
        # Limpa valores
        if 'valor' in df.columns:
            df['valor'] = df['valor'].apply(clean_currency)
        if 'custos' in df.columns:
            df['custos'] = df['custos'].apply(clean_currency)
        
        # Remove linhas vazias
        df = df.dropna(subset=['cliente'], how='all')
        
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

@app.route('/')
def dashboard():
    """Dashboard principal"""
    try:
        df = load_data()
        
        if df.empty:
            return "Erro ao carregar dados da planilha"
        
        # Calcula KPIs
        total_receita = df['valor'].sum()
        total_custos = df['custos'].sum()
        lucro_bruto = total_receita - total_custos
        margem_lucro = (lucro_bruto / total_receita * 100) if total_receita > 0 else 0
        total_pedidos = len(df)
        ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else 0
        
        # Pedidos pagos/pendentes
        pedidos_pagos = len(df[df['data_pagamento'].notna()])
        pedidos_pendentes = total_pedidos - pedidos_pagos
        taxa_inadimplencia = (pedidos_pendentes / total_pedidos * 100) if total_pedidos > 0 else 0
        
        # Top produtos
        top_produtos = df.groupby('produto_servico')['valor'].sum().nlargest(5)
        
        # Top clientes
        top_clientes = df.groupby('cliente')['valor'].sum().nlargest(5)
        
        # Receita por categoria
        receita_categoria = df.groupby('categoria')['valor'].sum()
        
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Primeira Linha Eventos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100% ); }
        .metric-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .metric-card.green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .metric-card.blue { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .metric-card.purple { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div class="flex items-center">
                    <div class="text-3xl mr-4">🎪</div>
                    <div>
                        <h1 class="text-3xl font-bold">Primeira Linha Eventos</h1>
                        <p class="text-blue-100">Dashboard Executivo v2.0</p>
                    </div>
                </div>
                <div class="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                    Atualizado: {{ timestamp }}
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- KPIs Principais -->
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <i class="fas fa-chart-line mr-3 text-blue-600"></i>
                Métricas Principais
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="metric-card green text-white rounded-xl p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white text-opacity-80 text-sm">Receita Total</p>
                            <p class="text-3xl font-bold">R$ {{ "%.2f"|format(total_receita) }}</p>
                            <p class="text-white text-opacity-80 text-xs mt-1">
                                Ticket médio: R$ {{ "%.2f"|format(ticket_medio) }}
                            </p>
                        </div>
                        <i class="fas fa-dollar-sign text-4xl text-white text-opacity-50"></i>
                    </div>
                </div>

                <div class="metric-card blue text-white rounded-xl p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white text-opacity-80 text-sm">Lucro Bruto</p>
                            <p class="text-3xl font-bold">R$ {{ "%.2f"|format(lucro_bruto) }}</p>
                            <p class="text-white text-opacity-80 text-xs mt-1">
                                Margem: {{ "%.1f"|format(margem_lucro) }}%
                            </p>
                        </div>
                        <i class="fas fa-chart-line text-4xl text-white text-opacity-50"></i>
                    </div>
                </div>

                <div class="metric-card purple text-white rounded-xl p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white text-opacity-80 text-sm">Total de Pedidos</p>
                            <p class="text-3xl font-bold">{{ total_pedidos }}</p>
                            <p class="text-white text-opacity-80 text-xs mt-1">
                                {{ pedidos_pagos }} pagos, {{ pedidos_pendentes }} pendentes
                            </p>
                        </div>
                        <i class="fas fa-box text-4xl text-white text-opacity-50"></i>
                    </div>
                </div>

                <div class="metric-card text-white rounded-xl p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white text-opacity-80 text-sm">Taxa de Inadimplência</p>
                            <p class="text-3xl font-bold">{{ "%.1f"|format(taxa_inadimplencia) }}%</p>
                            <p class="text-white text-opacity-80 text-xs mt-1">Meta: < 15%</p>
                        </div>
                        <i class="fas fa-exclamation-triangle text-4xl text-white text-opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Receita por Categoria -->
            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <i class="fas fa-chart-pie mr-3 text-purple-600"></i>
                    Receita por Categoria
                </h3>
                <canvas id="categoriaChart" width="400" height="200"></canvas>
            </div>

            <!-- Top Produtos -->
            <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
                <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <i class="fas fa-trophy mr-3 text-yellow-600"></i>
                    Top Produtos/Serviços
                </h3>
                <div class="space-y-3">
                    {% for produto, valor in top_produtos_list %}
                    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div class="flex items-center">
                            <div class="w-8 h-8 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                                {{ loop.index }}
                            </div>
                            <p class="font-medium text-sm">{{ produto }}</p>
                        </div>
                        <p class="font-semibold text-green-600">R$ {{ "%.2f"|format(valor) }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Top Clientes -->
        <div class="bg-white rounded-xl shadow-lg p-6 card-hover">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <i class="fas fa-users mr-3 text-blue-600"></i>
                Top Clientes
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {% for cliente, valor in top_clientes_list %}
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center">
                        <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                            {{ loop.index }}
                        </div>
                        <p class="font-medium text-sm">{{ cliente }}</p>
                    </div>
                    <p class="font-semibold text-blue-600">R$ {{ "%.2f"|format(valor) }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </main>

    <script>
        // Gráfico de categoria
        const ctx = document.getElementById('categoriaChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: {{ categoria_labels|safe }},
                datasets: [{
                    data: {{ categoria_values|safe }},
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    </script>
</body>
</html>
        """
        
        return render_template_string(html_template,
            timestamp=datetime.now().strftime('%d/%m/%Y %H:%M'),
            total_receita=total_receita,
            total_custos=total_custos,
            lucro_bruto=lucro_bruto,
            margem_lucro=margem_lucro,
            total_pedidos=total_pedidos,
            ticket_medio=ticket_medio,
            pedidos_pagos=pedidos_pagos,
            pedidos_pendentes=pedidos_pendentes,
            taxa_inadimplencia=taxa_inadimplencia,
            top_produtos_list=list(top_produtos.items()),
            top_clientes_list=list(top_clientes.items()),
            categoria_labels=list(receita_categoria.index),
            categoria_values=list(receita_categoria.values)
        )
        
    except Exception as e:
        return f"Erro: {str(e)}"

@app.route('/api/health')
def health():
    """Status da aplicação"""
    return jsonify({
        'status': 'healthy',
        'message': 'Dashboard Primeira Linha Eventos v2.0 Simplificado',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
