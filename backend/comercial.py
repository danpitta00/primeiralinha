"""
BACKEND MÓDULO COMERCIAL - PRIMEIRA LINHA EVENTOS
Gerador de orçamentos + Sistema de pedidos
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

app = Flask(__name__)
CORS(app)

# Inicializar banco
def init_db():
    conn = sqlite3.connect('comercial.db')
    cursor = conn.cursor()
    
    # Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            endereco TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco_base REAL NOT NULL,
            unidade TEXT DEFAULT 'unidade'
        )
    ''')
    
    # Orçamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orcamento TEXT UNIQUE NOT NULL,
            nome_cliente TEXT,
            email_cliente TEXT,
            telefone_cliente TEXT,
            evento_descricao TEXT,
            local_evento TEXT,
            data_evento DATE,
            data_entrega DATE,
            data_recolhimento DATE,
            valor_total REAL,
            observacoes TEXT,
            valido_ate DATE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Itens orçamento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamento_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            preco_total REAL NOT NULL,
            FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id)
        )
    ''')
    
    # Pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido TEXT UNIQUE NOT NULL,
            orcamento_id INTEGER,
            nome_cliente TEXT NOT NULL,
            evento_descricao TEXT,
            local_evento TEXT NOT NULL,
            data_entrega DATE NOT NULL,
            data_recolhimento DATE NOT NULL,
            valor_total REAL NOT NULL,
            custos_pedido REAL DEFAULT 0,
            observacoes TEXT,
            status TEXT DEFAULT 'registrado',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# CLIENTES
@app.route('/api/clientes', methods=['GET', 'POST'])
def gerenciar_clientes():
    if request.method == 'GET':
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes ORDER BY nome')
        clientes = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': c[0], 'nome': c[1], 'email': c[2], 
            'telefone': c[3], 'endereco': c[4]
        } for c in clientes])
    
    elif request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nome, email, telefone, endereco)
            VALUES (?, ?, ?, ?)
        ''', (data.get('nome'), data.get('email'), data.get('telefone'), data.get('endereco')))
        
        cliente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'id': cliente_id, 'mensagem': 'Cliente cadastrado'}), 201

# PRODUTOS
@app.route('/api/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'GET':
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos ORDER BY categoria, nome')
        produtos = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': p[0], 'nome': p[1], 'categoria': p[2], 
            'preco_base': p[3], 'unidade': p[4]
        } for p in produtos])
    
    elif request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO produtos (nome, categoria, preco_base, unidade)
            VALUES (?, ?, ?, ?)
        ''', (data.get('nome'), data.get('categoria'), data.get('preco_base'), data.get('unidade', 'unidade')))
        
        produto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'id': produto_id, 'mensagem': 'Produto cadastrado'}), 201

# ORÇAMENTOS
@app.route('/api/orcamentos', methods=['GET', 'POST'])
def gerenciar_orcamentos():
    if request.method == 'GET':
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orcamentos ORDER BY criado_em DESC')
        orcamentos = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': o[0], 'numero_orcamento': o[1], 'nome_cliente': o[2],
            'evento_descricao': o[4], 'valor_total': o[9], 'valido_ate': o[11]
        } for o in orcamentos])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Gerar número
        numero_orcamento = f"ORC{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
        valido_ate = (datetime.now() + timedelta(days=10)).date()
        
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        
        # Inserir orçamento
        cursor.execute('''
            INSERT INTO orcamentos (
                numero_orcamento, nome_cliente, email_cliente, telefone_cliente,
                evento_descricao, local_evento, data_evento, data_entrega, 
                data_recolhimento, valor_total, observacoes, valido_ate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            numero_orcamento, data.get('nome_cliente'), data.get('email_cliente'),
            data.get('telefone_cliente'), data.get('evento_descricao'), data.get('local_evento'),
            data.get('data_evento'), data.get('data_entrega'), data.get('data_recolhimento'),
            data.get('valor_total'), data.get('observacoes'), valido_ate
        ))
        
        orcamento_id = cursor.lastrowid
        
        # Inserir itens
        for item in data.get('itens', []):
            cursor.execute('''
                INSERT INTO orcamento_itens (orcamento_id, produto_nome, quantidade, preco_unitario, preco_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (orcamento_id, item['produto_nome'], item['quantidade'], item['preco_unitario'], item['preco_total']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'id': orcamento_id, 'numero_orcamento': numero_orcamento}), 201

# PDF ORÇAMENTO
@app.route('/api/orcamentos/<int:orcamento_id>/pdf', methods=['GET'])
def gerar_pdf_orcamento(orcamento_id):
    conn = sqlite3.connect('comercial.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orcamentos WHERE id = ?', (orcamento_id,))
    orcamento = cursor.fetchone()
    
    cursor.execute('SELECT * FROM orcamento_itens WHERE orcamento_id = ?', (orcamento_id,))
    itens = cursor.fetchall()
    
    conn.close()
    
    if not orcamento:
        return jsonify({'erro': 'Orçamento não encontrado'}), 404
    
    # Criar PDF
    filename = f"orcamento_{orcamento[1]}.pdf"
    filepath = f"/tmp/{filename}"
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Cabeçalho azul
    c.setFillColor(HexColor('#1E3A8A'))
    c.rect(0, height - 80, width, 80, fill=1)
    
    # Logo e título
    c.setFillColor(HexColor('#D4AF37'))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "PRIMEIRA LINHA EVENTOS")
    
    # CNPJ
    c.setFillColor('white')
    c.setFont("Helvetica", 10)
    c.drawString(width - 200, height - 30, "CNPJ: 31.912.825/0001-06")
    c.drawString(width - 200, height - 45, "Inscrição Estadual: 07.885.269/001-70")
    
    # Conteúdo
    y = height - 120
    c.setFillColor('black')
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"ORÇAMENTO Nº {orcamento[1]}")
    
    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Cliente: {orcamento[2] or 'A definir'}")
    y -= 20
    c.drawString(50, y, f"Evento: {orcamento[4] or 'A definir'}")
    y -= 20
    c.drawString(50, y, f"Local: {orcamento[5] or 'A definir'}")
    y -= 20
    c.drawString(50, y, f"Data: {orcamento[6] or 'A definir'}")
    
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "ITENS:")
    
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qtd")
    c.drawString(300, y, "Valor Unit.")
    c.drawString(400, y, "Total")
    
    y -= 20
    c.setFont("Helvetica", 10)
    
    for item in itens:
        c.drawString(50, y, item[2])  # produto_nome
        c.drawString(250, y, str(item[3]))  # quantidade
        c.drawString(300, y, f"R$ {item[4]:.2f}")  # preco_unitario
        c.drawString(400, y, f"R$ {item[5]:.2f}")  # preco_total
        y -= 15
    
    # Total
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(300, y, f"TOTAL: R$ {orcamento[9]:.2f}")
    
    # Pagamento
    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "PIX: primeiralinhaeventos@gmail.com")
    y -= 20
    c.drawString(50, y, f"Válido até: {orcamento[11]}")
    
    # Rodapé
    c.setFillColor(HexColor('#1E3A8A'))
    c.rect(0, 0, width, 60, fill=1)
    
    c.setFillColor('white')
    c.setFont("Helvetica", 9)
    c.drawString(50, 35, "Endereço: Saan quadra 02 nº 275/265 - Brasília/DF")
    c.drawString(50, 25, "Telefone: (61) 991334258 | primeiralinhaeventos@gmail.com")
    c.drawString(50, 15, "Instagram: @eventosprimeiralinha1")
    
    c.save()
    
    return send_file(filepath, as_attachment=True, download_name=filename)

# PEDIDOS
@app.route('/api/pedidos', methods=['GET', 'POST'])
def gerenciar_pedidos():
    if request.method == 'GET':
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pedidos ORDER BY criado_em DESC')
        pedidos = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': p[0], 'numero_pedido': p[1], 'nome_cliente': p[3],
            'local_evento': p[5], 'data_entrega': p[6], 'valor_total': p[8], 'status': p[11]
        } for p in pedidos])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        numero_pedido = f"PED{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:4].upper()}"
        
        conn = sqlite3.connect('comercial.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pedidos (
                numero_pedido, orcamento_id, nome_cliente, evento_descricao,
                local_evento, data_entrega, data_recolhimento, valor_total,
                custos_pedido, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            numero_pedido, data.get('orcamento_id'), data.get('nome_cliente'),
            data.get('evento_descricao'), data.get('local_evento'), data.get('data_entrega'),
            data.get('data_recolhimento'), data.get('valor_total'), data.get('custos_pedido', 0),
            data.get('observacoes')
        ))
        
        pedido_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'id': pedido_id, 'numero_pedido': numero_pedido}), 201

if __name__ == '__main__':
    init_db()
    print("🚀 Backend Comercial iniciado!")
    app.run(debug=True, host='0.0.0.0', port=5000)
