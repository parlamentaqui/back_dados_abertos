import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Retornar o json dos deputados pra aparecer na home
@api.route('/deputies-home')
def deputados():
    s_list = sorted(Deputy.objects, reverse=True, key=attrgetter('last_activity_date'))
    all_deputies = []
    for deputy in s_list:
        depu_json= deputy.to_json()
        all_deputies.append(depu_json)
    return jsonify(all_deputies[:6])

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
        temp_json = deputy.to_json()
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
        # Variavel auxiliar que ira dizer se o deputado possui ou nao uma UF
        aux = False
        if deputy.federative_unity == None:
            aux = True
        
        if str.lower(deputy.name).find(name_filter) != -1 or name_filter == "":
            if aux or str.lower(deputy.federative_unity) ==  uf_filter or uf_filter == "":
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
        temp_json = deputy.to_json()
        full_json.append(temp_json)

    # Retorna no formato JSON a lista de objetos full_json
    return jsonify(full_json)

@api.route('/deputies/<id>')
def profile(id):
    for profile in Deputy.objects:
      #Adicionar informacoes que estao comentadas
        if int(id) == int(profile.id):
            return profile.to_json()
        
    return {} 
        

@api.route('/federative_unities')
def federative_unities():
    r = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados')
    all_federative_unities_json = r.json()
    custom_federative_unities_json = []
    for federative_unity in all_federative_unities_json:
        federative_unity_temp = {}
        federative_unity_temp["uf"] = federative_unity["sigla"]
        federative_unity_temp["name"] = federative_unity["nome"]
        custom_federative_unities_json.append(federative_unity_temp)
    
    custom_federative_unities_json = sorted(custom_federative_unities_json,key=lambda k: k['name'])
    return jsonify(custom_federative_unities_json)


@api.route('/parties')
def parties():
    parties_list = []
    for deputy in Deputy.objects:
      #Adicionar informacoes que estao comentadas
        parties_list.append(deputy.party)
    used = set()
    unique = [x for x in parties_list if x not in used and (used.add(x) or True)]
    return jsonify(sorted(unique)) 
        

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
        birth_date=datetime.strptime(str(real_json["dataNascimento"]), '%Y-%m-%d') if len(str(real_json["dataNascimento"])) > 5 else None,
        death_date= datetime.strptime(str(real_json["dataFalecimento"]), '%Y-%m-%d') if len(str(real_json["dataFalecimento"])) > 5 else None,
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

    return new_deputy.to_json()

# Rota que popula no DB os dados das votacoes dos deputados
@api.route('/update_votes')
def update_votes():
    #request para api da câmara que retorna todos os votos em projetos em ordem de data
    r = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes?ordem=DESC&ordenarPor=dataHoraRegistro")
    all_votes_json = r.json()

    #para cada voto desse, encontrar os deputados responsáveis, quem votou ou não
    for vote in all_votes_json["dados"]:
        
        vote_uri = vote["uri"] + "/votos"
        r2 = requests.get(vote_uri)
        specific_vote_list = r2.json()["dados"]

        #caso a lista nao seja vazia, verificar e/ou popular esse voto no banco de dados
        if specific_vote_list:
            
            #para cada voto dentro da lista, atualizar o banco 
            for this_vote in specific_vote_list:
                deputy_json = this_vote["deputado_"]
                unique_vote_id = f'{vote["id"]}-{deputy_json["id"]}' #criar um id unico pra esse voto.

                # Verificar se esse voto já foi populado/criado corretamente, caso nao tenha sido, criar um novo.
                need_create_vote = True
                for item in Parlamentary_vote.objects:
                    if item.unique_id in unique_vote_id:
                        need_create_vote = False
                        # print('Não precisa criar o voto do : ' + deputy_json["nome"] + ' para a votação ' + vote["id"])
                        break
                        
                
                #passou da verificação e precisa criar um voto
                if need_create_vote:
                    #pegar o json da proposição desse voto
                    proposition_json = get_proposition_json_by_vote(vote)

                    #definir o datetime correto
                    vote_date = datetime.strptime(str(this_vote["dataRegistroVoto"]), '%Y-%m-%dT%H:%M:%S') if len(this_vote["dataRegistroVoto"]) > 5 else None

                    #lógica se votou de acordo com o partido:
                    voted_accordingly_party = voted_accordingly_party_method(this_vote["tipoVoto"], deputy_json["siglaPartido"], vote["uri"])

                    #Criar o novo voto parlamentar e salvar no banco com o métodos .save() 
                    new_vote = Parlamentary_vote(
                        unique_id = unique_vote_id,
                        id_voting = vote["id"],
                        id_deputy = deputy_json["id"],
                        deputy_name = deputy_json["nome"],
                        party = deputy_json["siglaPartido"],
                        federative_unity = deputy_json["siglaUf"],
                        id_legislature = str(deputy_json["idLegislatura"]),
                        date_time_vote = vote_date,
                        vote = this_vote["tipoVoto"],
                        voted_accordingly = voted_accordingly_party,
                        proposition_id = str(proposition_json["id"]),
                        proposition_description = proposition_json["ementa"],
                        proposition_title = proposition_json["descricaoTipo"],
                        proposition_link = proposition_json["urlInteiroTeor"]
                    ).save()

    return "Done! Use api/get_votes url to get all votes in database"

def voted_accordingly_party_method(vote_type, party, vote_uri):
    orientation_uri = vote_uri + "/orientacoes"
    r = requests.get(orientation_uri)

    orientation_json = r.json()["dados"]

    #para todo json dentro, encontrar o partido desse deputado
    for item in orientation_json:
        deputy_party_lower = party.lower()
        item_party_lower = item["siglaPartidoBloco"].lower()

        if item_party_lower in deputy_party_lower:
            vote_type_lower = vote_type.lower()
            party_vote_type_lower = item["orientacaoVoto"].lower()
            if party_vote_type_lower in vote_type_lower:
                return "Sim" 

    #Essa função vai retornar Sim ou Não 
    return "Não"

def get_proposition_json_by_vote(vote_json):
    #Pegar qual proposição é de acordo com a votação
    r3 = requests.get(vote_json["uri"])
    proposition_vote_json = r3.json()["dados"]

    if proposition_vote_json["proposicoesAfetadas"]:
        #caso tenha uma proposição afetada, pegar o json dessa proposição
        r4 = requests.get(proposition_vote_json["proposicoesAfetadas"][0]["uri"])

        proposition_full_json = r4.json()["dados"]
        return proposition_full_json
    
    #caso nao encontre nenhuma proposição, criar um json temporario com os mesmos nomes do json utilizados na criação de elemntos do banco de dados
    temp_json = {
        'id':None,
        'ementa':None,
        'descricaoTipo':None,
        'urlInteiroTeor':None
    }
    
    return temp_json

@api.route('/delete_votes')
def delete_votes():
    Parlamentary_vote.objects.all().delete()

    return "All votes in database were deleted! Use api/update_votes to update database."

@api.route('/get_votes')
def get_votes():
    #printar todos os valores dos banco de dados
    all_parlamentary_votes = []

    for item in Parlamentary_vote.objects:
        all_parlamentary_votes.append(item.to_json()) 

    return jsonify(all_parlamentary_votes)

@api.route('/update_expenses')
def update_expenses():
    for item in Deputy.objects:
        r = requests.get(f'https://dadosabertos.camara.leg.br/api/v2/deputados/{item.id}/despesas?ordem=ASC&ordenarPor=ano')
        real_json = r.json()["dados"]
        if not real_json: 
            continue


        for expense in real_json:
            new_expenses = Expenses(
                deputy_id =  int(item.id),
                year =  expense["ano"],
                month =  expense["mes"],
                expenses_type =  expense["tipoDespesa"],
                document_type =  expense["tipoDocumento"],
                document_date = datetime.strptime(str( expense["dataDocumento"]), '%Y-%m-%d') if  expense["dataDocumento"] is not None else None,
                document_num =  expense["codDocumento"],
                document_value =  expense["valorDocumento"],
                document_url =  expense["urlDocumento"],
                supplier_name =  expense["nomeFornecedor"],
                supplier_cnpj_cpf =  expense["cnpjCpfFornecedor"],
                liquid_value =  expense["valorLiquido"],
                glosa_value =  expense["valorGlosa"],
                refund_num =  expense["numRessarcimento"],
                batch_cod =  expense["codLote"],
                tranche =  expense["parcela"],
                ).save()
    return "banco de dados atualizado com sucesso"

@api.route('/expenses')
def get_expenses():
    all_expenses = []
    for item in Expenses.objects:
        all_expenses.append(item.to_json())

    return jsonify(all_expenses)

@api.route('/delete_expenses')
def delete_expenses():
    Expenses.objects.all().delete() 

    return "All expenses in database was deleted! Use api/update_expenses to update database."

@api.route('/expenses/<id>')
def expense(id):
    deputy_expenses = []
    for expenses in Expenses.objects:
        if int(id) == int(expenses.deputy_id):
            deputy_expenses.append(expenses.to_json())
        
    return jsonify(deputy_expenses)

@api.route('/get_votes_by_deputy_id/<id>')
def get_votes_by_deputy_id(id):
    deputy_votes = []
    for item in Parlamentary_vote.objects:
        if int(item.id_deputy) == int(id):
            deputy_votes.append(item.to_json())

    return jsonify(deputy_votes)

@api.route('/update_propositions')
def update_propositions():
    # Request para api da câmara que retorna todos as proposições em tramitação nos uíltimos 30 dias por ordem de id 
    r = requests.get("https://dadosabertos.camara.leg.br/api/v2/proposicoes?itens=1000&ordem=ASC&ordenarPor=id")
    all_propositions_r = r.json()

    # Pega todos os id's dessas proposições vindas da requisição e verifica se já existe a Proposicao na classe do DB
    all_propositions_json = []
    for proposition in all_propositions_r["dados"]:
        temp_id = int(proposition["id"])
        if temp_id not in get_all_ids_DB(): 
            r2 = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{temp_id}")
            all_propositions_json.append(r2.json())

    # Popula o banco de dados com as proposições que não existem nele
    for proposition in all_propositions_json:
        # Requisição para pegar informações do autor da proposicao
        r3 = requests.get(proposition["dados"]["uriAutores"])
        author_info_json = r3.json()
        
        # Lista que recebe a uri dos autores e pega o tipo do autor e seu id respectivamente
        r3_json_splited = str(r3.json()["dados"][0]["uri"]).split("/")

        author_info_json_type = r3_json_splited[5]
        author_info_json_id = r3_json_splited[6]

        if r3_json_splited[0] == "orgaos":
            r4 = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{author_info_json_id}")
            # JSON com as informações do órgao autor da proposição
            author_url_r = author_info_json["dados"]["uri"]
            author_type_r = author_info_json["dados"]["tipoOrgao"]
            author_name_r = author_info_json["dados"]["nome"]
        else:   
            # JSON com as informações do deputado autor da proposicao
            author_url_r = author_info_json["dados"][0]["uri"]
            author_type_r = author_info_json["dados"][0]["tipo"]
            author_name_r = author_info_json["dados"][0]["nome"]

        # Requisicao para pegar a sigla do autor
        if author_info_json_type != "orgaos":
            r4 = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{author_info_json_id}")
            author_uf_r = r4.json()["dados"]["ultimoStatus"]["siglaUf"]
        else:
            r4 = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/orgaos/{author_info_json_id}")
            author_uf_r = r4.json()["dados"]["sigla"]

        # Faz uma requisição para buscar o tema da proposição, já esta vem em outra rota através de seu id
        prop_id = proposition["dados"]["id"]
        r5 = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{prop_id}/temas")

        if len(r5.json()["dados"]) <= 0:
            proposition_theme = "Nao encontrado"
        else:
            proposition_theme = r5.json()["dados"][0]["tema"]

        # Ajuste de formato de datas
        apresentation_date = datetime.strptime(str(proposition["dados"]["dataApresentacao"]), '%Y-%m-%dT%H:%M') if len(proposition["dados"]["dataApresentacao"]) > 5 else None
        proposition_date = datetime.strptime(str(proposition["dados"]["statusProposicao"]["dataHora"]), '%Y-%m-%dT%H:%M') if len(proposition["dados"]["statusProposicao"]["dataHora"]) > 5 else None
        
        new_proposition = Proposicao(
            proposicao_id = proposition["dados"]["id"],
            id_deputado_autor = author_info_json_id,
            uri = proposition["dados"]["uri"],
            descricao_tipo = proposition["dados"]["descricaoTipo"],
            ementa = proposition["dados"]["ementa"],
            ementa_detalhada = proposition["dados"]["ementaDetalhada"],
            keywords = proposition["dados"]["keywords"],
            data_apresentacao = apresentation_date,
            urlAutor = author_url_r,
            tipoAutor = author_type_r,
            nome_autor = author_name_r,
            sigla_UF_autor = author_uf_r,
            tema_proposicao = proposition_theme,
            sigla_orgao = proposition["dados"]["statusProposicao"]["siglaOrgao"], # Comeca aqui as informacoes do objeto de status
            data_proposicao = proposition_date, 
            descricao_situacao = proposition["dados"]["statusProposicao"]["descricaoSituacao"],
            despacho = proposition["dados"]["statusProposicao"]["despacho"],
            uri_relator = proposition["dados"]["statusProposicao"]["uriUltimoRelator"],
            sigla_tipo = proposition["dados"]["siglaTipo"],
            cod_tipo = proposition["dados"]["codTipo"],
            numero = proposition["dados"]["numero"],
            ano = proposition["dados"]["ano"]
        ).save()

    return "Proposições atualizadas com sucesso."

def get_all_ids_DB():
    all_ids = []
    for item in Proposicao.objects:
        all_ids.append(int(item.id))
    
    return all_ids

@api.route('/get_all_propositions')
def get_all_proposition():
    propositions = []

    for prop in Proposicao.objects:
        propositions.append(prop.to_json())

    return jsonify(propositions)

@api.route('/get_proposition_by_id/<id>')
def get_proposition_by_id(id):
    for prop in Proposicao.objects:
        if int(prop.id) == int(id):
            return jsonify(prop.to_json())

    return "Erro. Proposicao nao encontrada"

@api.route('/delete_propositions')
def delete_all_propositions():
    Proposicao.objects.all().delete()
    return "Proposicoes apagadas com sucesso"
