import json
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

#Pegar as duas noticias mais recentes do nosso banco de dados
@api.route('/news')
def news():
    all_news = News.objects
    
    #Ordenar a lista de acordo com a data.
    sorted_list = sorted(all_news, key=attrgetter('update_date'))
    news_1 = sorted_list[0].to_json(sorted_list[0])
    news_2 = sorted_list[1].to_json(sorted_list[1])
    json_full = {
        'news_01':news_1,
        'news_02':news_2
    }

    return json_full

@api.route('/<id>')
def profile(id):
    profile_json = {}
    
    for profile in Deputy.objects:
      #Adicionar informacoes que estao comentadas
        if int(id) == int(profile.id):
            
            profile_json["photo_url"] = profile.name
            #Informacoes Pessoais
            profile_json["full_name"] = profile.full_name
            profile_json["party"] = profile.party
            profile_json["federative_unity"] = profile.federative_unity
            # profile_json["age"] = profile.age
            profile_json["birth_date"] = profile.birth_date
            #Informacoes do Gabinete
            # profile_json["room_number"] = profile.room_number
            # profile_json["floor"] = profile.floor
            # profile_json["building"] = profile.building
            # profile_json["telephone"] = profile.telephone
            # profile_json["email"] = profile.email
            #Redes Sociais
            profile_json["facebook_username"] = profile.facebook_username
            profile_json["twitter_username"] = profile.twitter_username
            profile_json["instagram_username"] = profile.instagram_username
            
            return profile_json
        
    return {} 
        
