import json
from flask import Blueprint, request
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Retornar um json com todos os jsons de deputados ordenados por nome
@api.route('/deputies')
def index():
    full_json = {}
    sorted_list = sorted(Deputy.objects, key=attrgetter('name'))
    cont = 0

    for deputy in sorted_list:
        temp_json = deputy.to_json(deputy)
        full_json[cont] = temp_json
        cont += 1

    return full_json

#Resultado das buscas de acordo com o filtro
@api.route('/resultado', methods=['POST'])
def resultado():
    #recebemos um json do request com {nome, uf e partido}
    requested_json = request.get_json()
    name_filter = requested_json["nome"]
    uf_filter = requested_json["uf"]
    party_filter = requested_json["partido"]

    #criar uam lista vazia com todos os candidatos 
    #adicionar na lista de acordo com os filtros e verificações
    all_deputies = []

    #verificar se o cada filtro não é nulo nem vazio
    if name_filter:
        #colocar em lower case pra não fazer diferença na comparação
        name_string = str.lower(name_filter)
        #para cada item dentro da lista dos deputados do banco de dados (foreach)
        for item in Deputy.objects:
            #deixar as strings em lower case pra poder comparar com o filtro
            item_name = str.lower(item.name)
            if(name_string in item_name) and (item not in all_deputies):
                #caso o filtro bata e já não tenha adicionado esse item na lista, adicionar
                all_deputies.append(item)

    if uf_filter:
        uf_string = str.lower(uf_filter)
        for item in Deputy.objects:
            item_uf = str.lower(item.federative_unity)
            if (uf_string in item_uf) and (item not in all_deputies):
                all_deputies.append(item)

    if party_filter:
        party_string = str.lower(party_filter)
        for item in Deputy.objects:
            item_party = str.lower(item.party)
            if(party_string in item_party) and (item not in all_deputies):
                all_deputies.append(item)

    #ordenar os deputados por nome
    sorted_list = sorted(all_deputies, key=attrgetter('name'))

    #criar um json com todos os deputados encontrados e ordenados
    full_json = {}
    cont = 0
    for deputy in sorted_list:
        temp_json = deputy.to_json(deputy)
        full_json[cont] = temp_json
        cont += 1

    return full_json
