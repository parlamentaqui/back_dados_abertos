import json
from flask import Blueprint
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Retornar um json com todos os jsons de deputados
@api.route('/deputies')
def index():
    full_json = {}
    cont = 0
    for deputy in Deputy.objects:
        temp_json = deputy.to_json(deputy)
        full_json[cont] = temp_json
        cont += 1

    return full_json

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
        