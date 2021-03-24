import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

# Rota que retorna um deputado em específico usando um id
@api.route('/deputado_especifico/<id>')
def ver_deputado(id):
    r = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id}")

    json_deputy = r.json()

    return json_deputy["dados"]

# Rota que retorna um json com todos os jsons de deputados ordenados por nome
@api.route('/deputies')
def index():
    full_json = []
    sorted_list = sorted(Deputy.objects, key=attrgetter('name'))

    for deputy in sorted_list:
        temp_json = deputy.to_json(deputy)
        full_json.append(temp_json)

    return jsonify(full_json)

# Rota que retorna o resultado de uma busca de acordo com os filtros no corpo da requsisçao POST
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

# Rota para apagar os todos os deputados do DB (USAR SOMENTE PARA TESTES) 
@api.route('/remover_deputados')
def apagar_deputados():
    Deputy.objects.all().delete()
    return "Deputados apagados com sucesso"


# Rota que popula no DB os dados dos deputados registrados nos dados abertos da câmara
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

    #2-criar uma lógica que popule corretamente as redes sociais 
    #3-verificar se o deputado já existe para não atualizar desnecessariamente 

    # Lógica que popula corretamente o ano inicial e final da legislatura
    request_initial_legistaure = requests.get(f'https://dadosabertos.camara.leg.br/api/v2/legislaturas/{deputy_json["idLegislaturaInicial"]}')
    initial_legislature_json = request_initial_legistaure.json()["dados"]

    request_final_legistaure = requests.get(f'https://dadosabertos.camara.leg.br/api/v2/legislaturas/{deputy_json["idLegislaturaFinal"]}')
    final_legislature_json = request_final_legistaure.json()["dados"]
   
    # Aqui se cria uma variavel que ira definir o ultimo status do deputado
    real_last_activity_date = real_json["ultimoStatus"]["data"]
    last_activity_date = str(real_last_activity_date)

    # Lógica para verificar se a informação de ultimo status está vazia ou não e corrigi-la para o formato correto
    if real_last_activity_date is None:
        last_activity_date = None

    elif len(real_last_activity_date) < 8:
        real_last_activity_date = None
        last_activity_date = None

    else:
        last_activity_date = last_activity_date[0:10]
        last_activity_date = datetime.strptime(last_activity_date, '%Y-%m-%d')

    # Popular a nova classe de acordo com as infos recebidas do objeto deputy_json
    new_deputy = Deputy(
        birth_date=datetime.strptime(str(real_json["dataNascimento"]), '%Y-%m-%d') if real_json["dataNascimento"] is not None else None,
        death_date= datetime.strptime(str(real_json["dataFalecimento"]), '%Y-%m-%d') if real_json["dataFalecimento"] is not None else None,
        email=real_json["ultimoStatus"]["email"],
        facebook_username=None,
        federative_unity=real_json["ufNascimento"],
        final_legislature_id=deputy_json["idLegislaturaFinal"],
        final_legislature_year=datetime.strptime(str(final_legislature_json["dataFim"]), '%Y-%m-%d').year,
        full_name=real_json["nomeCivil"],
        id=real_json["id"], 
        instagram_username=None,  
        initial_legislature_id=deputy_json["idLegislaturaInicial"],
        initial_legislature_year=datetime.strptime(str(initial_legislature_json["dataInicio"]), '%Y-%m-%d').year,
        last_activity_date=last_activity_date,
        name=real_json["ultimoStatus"]["nomeEleitoral"],
        party=real_json["ultimoStatus"]["siglaPartido"],
        photo_url=real_json["ultimoStatus"]["urlFoto"],
        sex=real_json["sexo"],
        twitter_username=None,
        ).save()

    return new_deputy.to_json(new_deputy)