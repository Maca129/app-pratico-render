#!/usr/bin/env python3
"""
Script para popular o banco de dados com o conteúdo programático oficial
do edital da DPC para Praticante de Prático
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.models.study import EditalItem, EditalProgress
from src.main import app

def create_edital_content():
    """Criar conteúdo programático do edital da DPC"""
    
    with app.app_context():
        # Limpar dados existentes do edital
        EditalProgress.query.delete()
        EditalItem.query.delete()
        db.session.commit()
        
        # Conteúdo programático baseado no edital oficial da DPC
        edital_content = [
            {
                "group_id": 1,
                "group_name": "MANOBRABILIDADE DO NAVIO",
                "items": [
                    "Comportamento do casco e leme(s) interagindo com sistema(s) propulsor(es)",
                    "Compreensão das causas que levam ao movimento do navio",
                    "Capacidade de executar manobras",
                    "Cálculos matemáticos inerentes ao assunto",
                    "Resistências do Navio - Resistência friccional",
                    "Resistências do Navio - Resistência a ondas",
                    "Forças que afetam o navio (Forces Affecting the Ship)"
                ]
            },
            {
                "group_id": 2,
                "group_name": "PROPULSÃO DO NAVIO E PROPULSORES",
                "items": [
                    "Definição de propulsão",
                    "Tipos de propulsores",
                    "Características dos propulsores",
                    "Eficiência propulsiva",
                    "Interação casco-propulsor",
                    "Sistemas de propulsão alternativos",
                    "Manutenção de sistemas propulsivos"
                ]
            },
            {
                "group_id": 3,
                "group_name": "SUPERFÍCIES DE CONTROLE",
                "items": [
                    "Lemes convencionais",
                    "Lemes especiais",
                    "Sistemas de controle direcional",
                    "Bow thrusters (propulsores de proa)",
                    "Stern thrusters (propulsores de popa)",
                    "Sistemas de posicionamento dinâmico",
                    "Controle de estabilidade"
                ]
            },
            {
                "group_id": 4,
                "group_name": "NAVEGAÇÃO E MANOBRAS PORTUÁRIAS",
                "items": [
                    "Técnicas de atracação",
                    "Técnicas de desatracação",
                    "Manobras em espaços confinados",
                    "Uso de rebocadores",
                    "Procedimentos de segurança portuária",
                    "Comunicação VHF",
                    "Coordenação com autoridades portuárias"
                ]
            },
            {
                "group_id": 5,
                "group_name": "FATORES AMBIENTAIS",
                "items": [
                    "Influência do vento nas manobras",
                    "Influência da corrente",
                    "Efeitos das marés",
                    "Condições de visibilidade",
                    "Estados do mar",
                    "Efeito de águas rasas",
                    "Interação entre navios"
                ]
            },
            {
                "group_id": 6,
                "group_name": "REGULAMENTAÇÃO E NORMAS",
                "items": [
                    "NORMAM-12/DPC - Serviço de Praticagem",
                    "Regulamento Internacional para Evitar Abalroamentos no Mar (RIPEAM)",
                    "Convenção SOLAS",
                    "Código ISM",
                    "Regulamentação da Autoridade Marítima",
                    "Normas de segurança portuária",
                    "Procedimentos de emergência"
                ]
            },
            {
                "group_id": 7,
                "group_name": "EQUIPAMENTOS E INSTRUMENTOS",
                "items": [
                    "Sistemas de navegação eletrônica",
                    "Radar e ARPA",
                    "GPS e sistemas de posicionamento",
                    "AIS (Sistema de Identificação Automática)",
                    "Equipamentos de comunicação",
                    "Instrumentos de medição",
                    "Sistemas de alarme e monitoramento"
                ]
            },
            {
                "group_id": 8,
                "group_name": "TIPOS DE EMBARCAÇÕES",
                "items": [
                    "Navios de carga geral",
                    "Navios porta-contêineres",
                    "Navios tanque",
                    "Navios de passageiros",
                    "Navios especializados",
                    "Características de manobrabilidade por tipo",
                    "Limitações operacionais específicas"
                ]
            }
        ]
        
        # Inserir dados no banco
        for group_data in edital_content:
            group_name = group_data["group_name"]
            
            for i, item_description in enumerate(group_data["items"], 1):
                edital_item = EditalItem(
                    section=group_name,
                    subsection=None,
                    content=item_description,
                    order_index=i
                )
                db.session.add(edital_item)
        
        db.session.commit()
        print(f"✅ Conteúdo programático criado com sucesso!")
        print(f"📚 Total de grupos: {len(edital_content)}")
        
        # Contar total de itens
        total_items = sum(len(group["items"]) for group in edital_content)
        print(f"📋 Total de itens: {total_items}")

if __name__ == "__main__":
    create_edital_content()

