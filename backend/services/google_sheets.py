import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class GoogleSheetsService:
    def __init__(self):
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1H07FB3X_tkSLSoHx-F2kyDmNQIGR4EyyTjnF-u19G3c/export?format=csv&gid=0"
        self.data = None
        self.last_update = None
        
    def fetch_data(self ):
        """Busca dados da planilha do Google Sheets"""
        try:
            # Lê dados da planilha
            df = pd.read_csv(self.sheet_url)
            
            # Limpa e padroniza os dados
            df = self._clean_data(df)
            
            self.data = df
            self.last_update = datetime.now()
            return df
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None
    
    def _clean_data(self, df):
        """Limpa e padroniza os dados"""
        # Renomeia colunas para padrão
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
        
        # Renomeia colunas se existirem
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Limpa valores monetários
        if 'valor' in df.columns:
            df['valor'] = df['valor'].apply(self._clean_currency)
        if 'custos' in df.columns:
            df['custos'] = df['custos'].apply(self._clean_currency)
        
        # Limpa diárias de equipe
        if 'diarias_equipe' in df.columns:
            df['diarias_equipe'] = df['diarias_equipe'].apply(self._clean_numeric)
        
        # Converte datas
        date_columns = ['data_entrega', 'data_recolhimento', 'data_pagamento']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%d/%m', errors='coerce')
                # Assume ano atual se não especificado
                current_year = datetime.now().year
                df[col] = df[col].apply(lambda x: x.replace(year=current_year) if pd.notna(x) else x)
        
        # Remove linhas vazias
        df = df.dropna(subset=['cliente'], how='all')
        
        return df
    
    def _clean_currency(self, value):
        """Limpa valores monetários"""
        if pd.isna(value) or value == '':
            return 0.0
        
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto vírgula e ponto
            value = re.sub(r'[^\d,.]', '', str(value))
            # Substitui vírgula por ponto
            value = value.replace(',', '.')
            
        try:
            return float(value)
        except:
            return 0.0
    
    def _clean_numeric(self, value):
        """Limpa valores numéricos"""
        if pd.isna(value) or value == '':
            return 0
        
        if isinstance(value, str):
            # Extrai apenas números
            numbers = re.findall(r'\d+', str(value))
            if numbers:
                return int(numbers[0])
        
        try:
            return int(float(value))
        except:
            return 0
    
    def get_kpis(self):
        """Calcula KPIs principais"""
        if self.data is None:
            self.fetch_data()
        
        df = self.data
        
        # KPIs básicos
        total_receita = df['valor'].sum()
        total_custos = df['custos'].sum()
        lucro_bruto = total_receita - total_custos
        margem_lucro = (lucro_bruto / total_receita * 100) if total_receita > 0 else 0
        total_pedidos = len(df)
        ticket_medio = total_receita / total_pedidos if total_pedidos > 0 else 0
        
        # KPIs avançados
        pedidos_pagos = df[df['data_pagamento'].notna()]
        pedidos_pendentes = df[df['data_pagamento'].isna()]
        taxa_inadimplencia = len(pedidos_pendentes) / total_pedidos * 100 if total_pedidos > 0 else 0
        
        # Análise por categoria
        receita_por_categoria = df.groupby('categoria')['valor'].sum().to_dict()
        margem_por_categoria = df.groupby('categoria').apply(
            lambda x: (x['valor'].sum() - x['custos'].sum()) / x['valor'].sum() * 100 if x['valor'].sum() > 0 else 0
        ).to_dict()
        
        return {
            'financeiro': {
                'total_receita': total_receita,
                'total_custos': total_custos,
                'lucro_bruto': lucro_bruto,
                'margem_lucro': margem_lucro,
                'ticket_medio': ticket_medio
            },
            'operacional': {
                'total_pedidos': total_pedidos,
                'pedidos_pagos': len(pedidos_pagos),
                'pedidos_pendentes': len(pedidos_pendentes),
                'taxa_inadimplencia': taxa_inadimplencia
            },
            'categorias': {
                'receita_por_categoria': receita_por_categoria,
                'margem_por_categoria': margem_por_categoria
            }
        }
