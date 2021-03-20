import json
from flask import Blueprint
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Retornar o json dos deputados pra aparecer na home
@api.route('/deputies')
def deputados():
    s_list = sorted(Deputy.objects, reverse=True, key=attrgetter('last_activity_date'))
    all_deputies = {}
    cont = 0
    for deputy in s_list:
        depu_json= {}
        depu_json["name"] = deputy.name
        depu_json["photo_url"] = deputy.photo_url
        depu_json["party"] = deputy.party
        depu_json["federative_unity"] = deputy.federative_unity
        all_deputies[cont] = depu_json
        cont += 1

    return all_deputies

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
