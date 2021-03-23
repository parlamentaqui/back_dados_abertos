import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Retornar um json com todos os jsons de deputados ordenados por nome
@api.route('/deputies')
def index():
    full_json = []
    sorted_list = sorted(Deputy.objects, key=attrgetter('name'))

    for deputy in sorted_list:
        temp_json = deputy.to_json(deputy)
        full_json.append(temp_json)

    return jsonify(full_json)

#Resultado das buscas de acordo com o filtro
@api.route('/resultado', methods=['POST'])
def resultado():
    #recebemos um json do request com {nome, uf e partido}
    requested_json = request.get_json()
    name_filter = str.lower(requested_json["nome"])
    uf_filter = str.lower(requested_json["uf"])
    party_filter = str.lower(requested_json["partido"])

    # Cria uma lista vazia e preenche com os objetos salvos de Deputy
    all_deputies = []
    for item in Deputy.objects:
        all_deputies.append(item)
 

    # Filtra os resultados da pesquisa
    for deputy in Deputy.objects:
        if str.lower(deputy.name).find(name_filter) != -1 or name_filter == "":
            if str.lower(deputy.federative_unity) ==  uf_filter or uf_filter == "":
                if str.lower(deputy.party) == party_filter or party_filter == "":
                    continue
                else:
                    all_deputies.remove(deputy)
            else:
                all_deputies.remove(deputy)
        else:
            all_deputies.remove(deputy)

    # Ordena os deputados por nome
    sorted_list = sorted(all_deputies, key=attrgetter('name'))

    # Cria um json com todos os deputados encontrados e já ordenados
    full_json = []

    for deputy in sorted_list:
        temp_json = deputy.to_json(deputy)
        full_json.append(temp_json)

    # Retorna no formato JSON a lista de objetos full_json
    return jsonify(full_json)


@api.route('/atualizar_deputados')
def atualizar_deputados():
    r = requests.get(f'https://dadosabertos.camara.leg.br/arquivos/deputados/json/deputados.json')
    all_deputies_basic_json = r.json()
    filtered_list = filter(lambda deputado : deputado["idLegislaturaFinal"] == 56, all_deputies_basic_json["dados"])

    #criar uma lista com todos os deputados
    all_deputies = []

    #Iterar por todos os deputados que se encontram no basic json
    for item in filtered_list:
        all_deputies.append(create_deputy(item))

    return jsonify(all_deputies)


def create_deputy(deputy_json):
    #Criar uma nova requisição desse deputado para pegar as informações específicas
    request_full_deputy_info = requests.get(deputy_json["uri"])
    real_json = request_full_deputy_info.json()["dados"]

    #1-verificar o None da data de nascimento e ultima atualização (verificar ternários do método)
    #2-criar uma lógica que popule corretamente as redes sociais 
    #3-verificar se o deputado já existe para não atualizar desnecessariamente (essa lógica so pode ser usada depois de consertar as issues acima)

    #criar uma lógica que popule corretamente o ano inicial e final da legislatura
    request_initial_legistaure = requests.get(f'https://dadosabertos.camara.leg.br/api/v2/legislaturas/{deputy_json["idLegislaturaInicial"]}')
    initial_legislature_json = request_initial_legistaure.json()["dados"]

    request_final_legistaure = requests.get(f'https://dadosabertos.camara.leg.br/api/v2/legislaturas/{deputy_json["idLegislaturaFinal"]}')
    final_legislature_json = request_final_legistaure.json()["dados"]

    #Calucular as substrings do last_activity_date
    real_last_activity_date = str(real_json["ultimoStatus"]["data"])
    real_last_activity_date = real_last_activity_date[0:10]

    #popular a nova classe de acordo com as infos
    new_deputy = Deputy(
        id=real_json["id"], 
        name=real_json["ultimoStatus"]["nomeEleitoral"],
        photo_url=real_json["ultimoStatus"]["urlFoto"],
        initial_legislature_id=deputy_json["idLegislaturaInicial"],
        final_legislature_id=deputy_json["idLegislaturaFinal"],
        initial_legislature_year=datetime.strptime(str(initial_legislature_json["dataInicio"]), '%Y-%m-%d').year,
        final_legislature_year=datetime.strptime(str(final_legislature_json["dataFim"]), '%Y-%m-%d').year,
        last_activity_date=datetime.strptime(real_last_activity_date, '%Y-%m-%d') if len(real_last_activity_date) is "None" else None,
        full_name=real_json["nomeCivil"],
        sex=real_json["sexo"],
        email=real_json["ultimoStatus"]["email"],
        birth_date=datetime.strptime(str(real_json["dataNascimento"]), '%Y-%m-%d') if len(str(real_json["dataNascimento"])) is "None" else None,
        death_date= datetime.strptime(str(real_json["dataFalecimento"]), '%Y-%m-%d') if len(str(real_json["dataFalecimento"])) is "None" else None,
        federative_unity=real_json["ufNascimento"],
        party=real_json["ultimoStatus"]["siglaPartido"],
        instagram_username=None,  
        twitter_username=None,
        facebook_username=None
        ).save()

    return new_deputy.to_json(new_deputy)