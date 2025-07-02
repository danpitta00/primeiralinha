from flask import Blueprint, jsonify, request
from services.google_sheets import GoogleSheetsService
import sys
import os

analytics_bp = Blueprint('analytics', __name__)
sheets_service = GoogleSheetsService()

@analytics_bp.route('/kpis', methods=['GET'])
def get_kpis():
    """Retorna KPIs principais do negócio"""
    try:
        kpis = sheets_service.get_kpis()
        return jsonify({
            'success': True,
            'data': kpis,
            'last_update': sheets_service.last_update.isoformat() if sheets_service.last_update else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/evolucao-temporal', methods=['GET'])
def get_evolucao_temporal():
    """Retorna evolução temporal das métricas"""
    try:
        evolucao = sheets_service.get_evolucao_temporal()
        return jsonify({
            'success': True,
            'data': evolucao
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/top-produtos', methods=['GET'])
def get_top_produtos():
    """Retorna top produtos por receita"""
    try:
        limit = request.args.get('limit', 10, type=int)
        produtos = sheets_service.get_top_produtos(limit)
        return jsonify({
            'success': True,
            'data': produtos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/top-clientes', methods=['GET'])
def get_top_clientes():
    """Retorna top clientes por receita"""
    try:
        limit = request.args.get('limit', 10, type=int)
        clientes = sheets_service.get_top_clientes(limit)
        return jsonify({
            'success': True,
            'data': clientes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/alertas', methods=['GET'])
def get_alertas():
    """Retorna alertas importantes"""
    try:
        alertas = sheets_service.get_alertas()
        return jsonify({
            'success': True,
            'data': alertas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/previsoes', methods=['GET'])
def get_previsoes():
    """Retorna previsões baseadas em dados históricos"""
    try:
        previsoes = sheets_service.get_previsoes()
        return jsonify({
            'success': True,
            'data': previsoes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/dashboard-executivo', methods=['GET'])
def get_dashboard_executivo():
    """Retorna dados completos para dashboard executivo"""
    try:
        # Busca todos os dados necessários
        kpis = sheets_service.get_kpis()
        alertas = sheets_service.get_alertas()
        top_produtos = sheets_service.get_top_produtos(5)
        top_clientes = sheets_service.get_top_clientes(5)
        previsoes = sheets_service.get_previsoes()
        
        # Calcula crescimento mensal
        evolucao = sheets_service.get_evolucao_temporal()
        crescimento_mensal = 0
        if len(evolucao) >= 2:
            ultimo_mes = evolucao[-1]['valor']
            penultimo_mes = evolucao[-2]['valor']
            if penultimo_mes > 0:
                crescimento_mensal = ((ultimo_mes - penultimo_mes) / penultimo_mes) * 100
        
        return jsonify({
            'success': True,
            'data': {
                'kpis': kpis,
                'alertas': alertas,
                'top_produtos': top_produtos,
                'top_clientes': top_clientes,
                'previsoes': previsoes,
                'crescimento_mensal': crescimento_mensal,
                'last_update': sheets_service.last_update.isoformat() if sheets_service.last_update else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    """Força atualização dos dados"""
    try:
        sheets_service.fetch_data()
        return jsonify({
            'success': True,
            'message': 'Dados atualizados com sucesso',
            'last_update': sheets_service.last_update.isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
