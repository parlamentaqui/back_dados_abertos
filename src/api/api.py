import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import *
from operator import attrgetter

api = Blueprint('api', __name__, url_prefix='/api')

#Getters
@api.route('/deputies-home')
def deputies_home():
    full_json = []
    sorted_list = sorted(Deputy.objects, reverse = True, key = lambda dep: datetime.strptime(str(dep["last_activity_date"]), "%Y-%m-%d %H:%M:%S") if len(str(dep["last_activity_date"])) > 5 else datetime.strptime("1999-12-12", "%Y-%m-%d"))

    for deputy in sorted_list[0:6]:
        full_json.append(deputy.to_json())

    return jsonify(full_json)

@api.route('/deputies')
def index():
    full_json = []
    sorted_list = sorted(Deputy.objects, reverse = True, key = lambda dep: datetime.strptime(str(dep["last_activity_date"]), "%Y-%m-%d %H:%M:%S") if len(str(dep["last_activity_date"])) > 5 else datetime.strptime("1999-12-12", "%Y-%m-%d"))

    for deputy in sorted_list:
        full_json.append(deputy.to_json())

    return jsonify(full_json)

@api.route('/resultado', methods=['POST'])
def resultado():
    #json de request {nome, uf e partido}
    requested_json = request.get_json()
    name_filter = str.lower(requested_json["nome"])
    uf_filter = str.lower(requested_json["uf"])
    party_filter = str.lower(requested_json["partido"])

    all_deputies = list(Deputy.objects)
 
    for deputy in Deputy.objects:
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

    sorted_list = sorted(all_deputies, key=attrgetter('name'))

    full_json = []
    for deputy in sorted_list:
        full_json.append(deputy.to_json())

    return jsonify(full_json)

@api.route('/deputies/<id>')
def profile(id):
    deputy = Deputy.objects(id=id).first()
    if deputy:
        return deputy.to_json()

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
        parties_list.append(deputy.party)
    used = set()
    unique = [x for x in parties_list if x not in used and (used.add(x) or True)]
    return jsonify(sorted(unique)) 

@api.route('/get_votes')
def get_votes():
    #printar todos os valores dos banco de dados
    all_parlamentary_votes = []

    for item in Parlamentary_vote.objects:
        all_parlamentary_votes.append(item.to_json()) 

    return jsonify(all_parlamentary_votes)

@api.route('/expenses')
def get_expenses():
    all_expenses = []
    for item in Expenses.objects:
        all_expenses.append(item.to_json())

    return jsonify(all_expenses)

@api.route('/expenses/<id>')
def expense(id):
    deputy_expenses = []
    expense = Expenses.objects(deputy_id=id).all()
    
    for item in expense:
        deputy_expenses.append(item.to_json())
        
    return jsonify(deputy_expenses)

@api.route('/filtered_expenses/<id>', methods=['POST'])
def filtered_expenses(id):
    #recebemos um json do request com { razao_social e tipo_gasto }
    requested_json = request.get_json()
    supplier_name = str.lower(requested_json["razao_social"])
    expenses_type = str.lower(requested_json["tipo_gasto"])

    # Cria uma lista vazia e preenche com os objetos salvos de Deputy
    all_deputy_expenses = Expenses.objects(deputy_id=id).all()
    temp_list = []
    
    # Filtra os resultados da pesquisa
    for expense in all_deputy_expenses:
        if len(supplier_name) > 0:
            #filtro pelo nome
            if len(expenses_type) > 0:
                #filtro pelo nome e pelo tipo
                if str.lower(expense.expenses_type).find(expenses_type) != -1 and str.lower(expense.supplier_name).find(supplier_name) != -1:
                    #encontrou o tipo
                    temp_list.append(expense)
                    continue
                else:
                    #filtrando pelo tipo e nao encontrou nada
                    continue 
            else:
                #filtro somente pelo nome
                if str.lower(expense.supplier_name).find(supplier_name) != -1:
                    temp_list.append(expense)
                    continue
                else:
                    continue
        elif len(expenses_type) > 0:
            #filtro somente pelo tipo
            if str.lower(expense.expenses_type).find(expenses_type) != -1:
                #encontrou o tipo
                temp_list.append(expense)
                continue
            else:
                #nao encontrou nada
                continue 
        else:
            #nenhum filtro
            temp_list.append(expense)
            continue 

    full_json = []
    for expense in temp_list:
        full_json.append(expense.to_json())

    return jsonify(full_json)

@api.route('/get_votes_by_deputy_id/<id>')
def get_votes_by_deputy_id(id):
    deputy_votes = Parlamentary_vote.objects(id_deputy=id).all()
    json_list = []
    for item in deputy_votes:
        if int(item.id_deputy) == int(id):
            json_list.append(item.to_json())

    return jsonify(json_list)

@api.route('/get_all_propositions')
def get_all_proposition():
    propositions = []

    for prop in Proposicao.objects:
        propositions.append(prop.to_json())

    return jsonify(propositions)

@api.route('/get_proposition_by_id/<id>')
def get_proposition_by_id(id):
    proposition = Proposicao.objects(proposicao_id=id).first()

    if proposition:
        return proposition.to_json()

    return {}


#ROTAS DB - DEPUTADOS
@api.route('/remover_deputados')
def apagar_deputados():
    Deputy.objects.all().delete()
    return "Deputados apagados com sucesso"

@api.route('/atualizar_deputados')
def atualizar_deputados():
    r = requests.get(f'https://dadosabertos.camara.leg.br/arquivos/deputados/json/deputados.json')
    all_deputies_basic_json = r.json()
    filtered_list = filter(lambda deputado : deputado["idLegislaturaFinal"] == 56, all_deputies_basic_json["dados"])

    all_deputies = []
    for item in filtered_list:
        create_deputy(item)  

    return "Done. Use /deputies to get all deputies in data base."

def create_deputy(deputy_json):
    #Criar uma nova requisição desse deputado para pegar as informações específicas
    real_json = requests.get(deputy_json["uri"]).json()["dados"]

    deputy = Deputy.objects(id=real_json["id"]).first()
    
    if deputy:
        deputy.office_number = real_json["ultimoStatus"]["gabinete"]["sala"]
        deputy.office_name = real_json["ultimoStatus"]["gabinete"]["nome"]
        deputy.office_premise = real_json["ultimoStatus"]["gabinete"]["predio"]
        deputy.office_floor = real_json["ultimoStatus"]["gabinete"]["andar"]
        deputy.office_phone = real_json["ultimoStatus"]["gabinete"]["telefone"]
        deputy.office_email = real_json["ultimoStatus"]["gabinete"]["email"]
        deputy.save()
        return
    else:
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
            office_number = real_json["ultimoStatus"]["gabinete"]["sala"],
            office_name = real_json["ultimoStatus"]["gabinete"]["nome"],
            office_premise = real_json["ultimoStatus"]["gabinete"]["predio"],
            office_floor = real_json["ultimoStatus"]["gabinete"]["andar"],
            office_phone = real_json["ultimoStatus"]["gabinete"]["telefone"],
            office_email = real_json["ultimoStatus"]["gabinete"]["email"]
            ).save()


#ROTAS DB - VOTOS
@api.route('/update_votes')
def update_votes():
    #request para api da câmara que retorna todos os votos em projetos em ordem de data
    r = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes?ordem=DESC&ordenarPor=dataHoraRegistro")
    all_votes_json = r.json()

    for vote in all_votes_json["dados"]:
        
        vote_uri = vote["uri"] + "/votos"
        r2 = requests.get(vote_uri)
        specific_vote_list = r2.json()["dados"]

        if specific_vote_list:
            
            proposition_json = get_proposition_json_by_vote(vote)
            
            for this_vote in specific_vote_list:
                deputy_json = this_vote["deputado_"]
                unique_vote_id = f'{vote["id"]}-{deputy_json["id"]}' #criar um id unico pra esse voto.

                need_create_vote = True
                vote_db = Parlamentary_vote.objects(unique_id=unique_vote_id).first()
                
                if vote_db or this_vote is None:
                    need_create_vote = False

                if need_create_vote:
                    vote_date = datetime.strptime(str(this_vote["dataRegistroVoto"]), '%Y-%m-%dT%H:%M:%S') if len(this_vote["dataRegistroVoto"]) > 5 else None

                    voted_accordingly_party = voted_accordingly_party_method(this_vote["tipoVoto"], deputy_json["siglaPartido"], vote["uri"])

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


#ROTAS DB - DESPESAS
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
    return "Done. Use api/expenses to get all expenses in data base."

@api.route('/delete_expenses')
def delete_expenses():
    Expenses.objects.all().delete() 
    return "All expenses in database was deleted! Use api/update_expenses to update database."


#ROTAS DB - PROPOSIÇÕES
@api.route('/update_propositions')
def update_propositions():
    # Request para api da câmara que retorna todos as proposições em tramitação nos uíltimos 30 dias por ordem de id 
    # Pagina maxima 5623

    all_propositions_json = []
    for index in range(1, 5624):
        r = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataInicio=2010-01-01&dataFim=2021-05-05&itens=100&pagina={index}&ordem=DESC&ordenarPor=ano")
        if not r:
            continue
        print(index)
        all_propositions_json.append(r.json()["dados"])
    
    # all_propositions_r = r.json()
    return jsonify(all_propositions_json)

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

@api.route('/delete_propositions')
def delete_all_propositions():
    Proposicao.objects.all().delete()
    return "Proposicoes apagadas com sucesso"


#CURIOSIDADES
@api.route('/get_curiosities/<id>')
def get_curiosities(id):
    curiosity_json = {
        "curiosity":""
    }

    # Curiosidade É O ALINHAMENTO, então remover o gov_align e fazer se o alinhamento tem uma porcentagem interessante (ver is_deputy_allign)
    
    curiosity = None
    deputy = Deputy.objects(id=id).first()

    if deputy:

        if oldest_deputy_rank(deputy):
            curiosity = oldest_deputy_rank(deputy)

        elif deputy_related_expense(deputy):
            curiosity = deputy_related_expense(deputy)

        elif is_deputy_allign(deputy.id):
            curiosity = is_deputy_allign(deputy.id)

        elif calculate_government_alignment(deputy):
            curiosity = calculate_government_alignment(deputy)

        elif deputy_term_of_office(deputy):
            curiosity = deputy_term_of_office(deputy)
        
        else:
            curiosity = deputy_expense_percent(deputy)
             
    if not curiosity:
        return {}

    curiosity_json["curiosity"] = curiosity

    return curiosity_json

def oldest_deputy_rank(deputy):
    s_list = sorted(Deputy.objects, reverse=False, key=attrgetter('initial_legislature_year'))
    cont = 0
    for item in s_list:
        cont = cont + 1
        if int(deputy.id) == int(item.id):
            break
    
    if cont > 50:
        return None

    # Foi omitido a qtd de deputados aqui pq o projeto está tratando dos deputados com legislatura atual
    return f"{cont}º parlamentar com mais tempo em exercício atualmente : {int(datetime.now().year - deputy.initial_legislature_year)} anos."
    

def deputy_related_expense(deputy):
    deputy_total_expense = calculate_deputy_total_expense(deputy)

    all_deputies_total_expenses = []
    for item in Deputy.objects:
        all_deputies_total_expenses.append(calculate_deputy_total_expense(item))
    
    average = 0
    for item in all_deputies_total_expenses:
        average = average + item
    
    average = int(average / len(all_deputies_total_expenses))
    expense_percent = ((deputy_total_expense / average) * 100.0) - 100.0
    expense_percent_string = float('{0:.3g}'.format(expense_percent))
    if expense_percent > 0 and abs(expense_percent) > 10:
        return f"Gastou {expense_percent_string}% a mais que seus colegas parlamentares."
    elif expense_percent < 0 and abs(expense_percent) > 20:
        f"Gastou {abs(expense_percent_string)}% a menos que seus colegas parlamentares."
    else:
        return None

def is_deputy_allign(id):
    all_votes_list = list(Parlamentary_vote.objects(id_deputy=id).all())
    if not all_votes_list:
        return None
    
    total_votes = 0
    accordingly_vote = 0

    for item in all_votes_list:
        total_votes = total_votes + 1
        if item.voted_accordingly in "Sim":
            accordingly_vote = accordingly_vote + 1

    percent = (accordingly_vote / total_votes) * 100.0
    if percent > 85 or percent < 60:
        return  f"O deputado é {'{0:.3g}'.format(percent)}% alinhado com seu partido."

    return None

def deputy_term_of_office(deputy):
    years_in_office = int(datetime.now().year - deputy.initial_legislature_year)
    if years_in_office < 8:
        return None

    return f"O deputado está em exercício há {years_in_office} anos."

def deputy_expense_percent(deputy):
    deputy_expenses = []
    total = 0
    for expenses in Expenses.objects:
        if int(deputy.id) == int(expenses.deputy_id):
            deputy_expenses.append(expenses)
            total = total + expenses.document_value
   
    exp_list = sorted(deputy_expenses, reverse=True, key=attrgetter('document_value'))
    if not exp_list:
        return "Esse deputado não declarou nenhuma despesa."

    greater_expense = exp_list[0]
    num = (greater_expense.document_value / total) * 100
    category = str(greater_expense.expenses_type.lower())
    category = category.replace(".","")
    return f"A categoria '{category}' ocupou {'{0:.3g}'.format(num)}% dos seus gastos"

def calculate_deputy_total_expense(deputy):
    deputy_expenses =  Expenses.objects(deputy_id=deputy.id)
    deputy_total_expense = 0
    for item in deputy_expenses:
        deputy_total_expense = deputy_total_expense + item.document_value

    return deputy_total_expense

def calculate_government_alignment(deputy):

    all_votes_by_deputy = list(Parlamentary_vote.objects(id_deputy=deputy.id).all())
    all_votes_by_gov_deputy = list(Parlamentary_vote.objects(id_deputy=160674).all())  # Votos do deputado líder do governo na Câmara (Hugo Motta)
         
    if not all_votes_by_deputy:
        return None
    
    total_votes = 0
    accordingly_vote = 0

    for a,b in zip(all_votes_by_deputy, all_votes_by_gov_deputy):
        total_votes = total_votes + 1
        if a.vote == b.vote:
            accordingly_vote = accordingly_vote + 1

    print(total_votes)
    print(accordingly_vote)

    percent = (accordingly_vote / total_votes) * 100.0
    if percent > 90 or percent < 35:
        return  f"O deputado é {'{0:.3g}'.format(percent)}% alinhado com o governo."

    return None

@api.route('/expenses_by_type/<id>')
def expenses_by_type(id):
    list_expenses_type = []
    json = {}
    for expenses in Expenses.objects:
        if str(expenses.expenses_type) not in list_expenses_type:
            list_expenses_type.append(str(expenses.expenses_type))
            json[str(expenses.expenses_type)] = 0

    deputy_expenses = Expenses.objects(deputy_id=id).all()
    
    if not deputy_expenses:
        return {}
    
    for item in deputy_expenses:
        temp = json[str(item.expenses_type)]
        temp = temp + item.document_value
        json[str(item.expenses_type)] = temp

    final_json = {}
    final_json["manuntencao"] = json["MANUTEN\u00c7\u00c3O DE ESCRIT\u00d3RIO DE APOIO \u00c0 ATIVIDADE PARLAMENTAR"]
    final_json["consultorias"] = json["CONSULTORIAS, PESQUISAS E TRABALHOS T\u00c9CNICOS."]
    final_json["assinatura"] = json["ASSINATURA DE PUBLICA\u00c7\u00d5ES"]
    final_json["divulgacao"] = json["DIVULGA\u00c7\u00c3O DA ATIVIDADE PARLAMENTAR."]
    final_json["fornecimento"] = json["FORNECIMENTO DE ALIMENTA\u00c7\u00c3O DO PARLAMENTAR"]
    final_json["hospedagem"] = json["HOSPEDAGEM ,EXCETO DO PARLAMENTAR NO DISTRITO FEDERAL."]
    final_json["loc_aeronaves"] = json["LOCA\u00c7\u00c3O OU FRETAMENTO DE AERONAVES"]
    final_json["loc_embarcacoes"] = json["LOCA\u00c7\u00c3O OU FRETAMENTO DE EMBARCA\u00c7\u00d5ES"]
    final_json["loc_veiculos"] = json["LOCA\u00c7\u00c3O OU FRETAMENTO DE VE\u00cdCULOS AUTOMOTORES"]
    final_json["passagem_reembolso"] = json["PASSAGEM A\u00c9REA - REEMBOLSO"]
    final_json["passagem_rpa"] = json["PASSAGEM A\u00c9REA - RPA"]
    final_json["servicos_seguranca"] = json["SERVI\u00c7O DE SEGURAN\u00c7A PRESTADO POR EMPRESA ESPECIALIZADA."]
    final_json["servico_estacionamento"] = json["SERVI\u00c7O DE T\u00c1XI, PED\u00c1GIO E ESTACIONAMENTO"]
    final_json["servicos_postais"] = json["SERVI\u00c7OS POSTAIS"]
    final_json["telefonia"] = json["TELEFONIA"]

    return final_json

@api.route('/get_total_expenses/<id>')
def get_total_expenses(id):
    total = 0
    for expenses in Expenses.objects:
        if int(id) == int(expenses.deputy_id):
            total = total + expenses.document_value
   
    return jsonify(total)
