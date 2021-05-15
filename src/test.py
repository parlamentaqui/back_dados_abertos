
import unittest
from app import app
from mongoengine import connect
from flask import Flask
import requests_mock
import os

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
PORT = os.getenv('PORT')

class AppTests(unittest.TestCase):

  def setUp(self):
    self.app = app
    self.app.testing = True
    self.context = self.app.test_request_context()
    self.context.push()
    self.client = self.app.test_client()

  def test_index_status(self):
    request = self.client.get('/')
    self.assertEqual(200 , request.status_code)

  def test_index(self):
    request = self.client.get('/')
    self.assertEqual('ETL Camara' , request.data.decode())
    self.assertGreaterEqual(len(request.data.decode()),2)

  def test_fake_status(self):
    request = self.client.get('/not_exist')
    self.assertEqual(404 , request.status_code)

  def tearDown(self):
    self.context.pop()


class EtlTests(unittest.TestCase):
  
  connect(DB_NAME, host=f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource=admin')

  def setUp(self):
    self.app = app
    self.app.testing = True
    self.context = self.app.test_request_context()
    self.context.push()
    self.client = self.app.test_client()
      
  @requests_mock.Mocker()
  def test_federative_unities(self, request_mock):
    url =  'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
    data = [
    {
        "id": 27,
        "sigla": "AL",
        "nome": "Alagoas",
        "regiao": {
            "id": 2,
            "sigla": "NE",
            "nome": "Nordeste"
        }
    },
    {
        "id": 12,
        "sigla": "AC",
        "nome": "Acre",
        "regiao": {
            "id": 1,
            "sigla": "N",
            "nome": "Norte"
        }
    }]
    
    response = [
      {
          "name": "Acre",
          "uf": "AC"
      },
      {
          "name": "Alagoas",
          "uf": "AL"
      }
    ]

    request_mock.get(url, json=data)
    request_mock.status_code(200)

    request = self.client.get('/api/federative_unities')

    self.assertEqual(200 , request.status_code)
    self.assertEqual(response , request.data.decode())

  def test_parties_status(self):
    request = self.client.get('/api/parties')
    self.assertEqual(200 , request.status_code)

  def test_get_votes_status(self):
    request = self.client.get('/api/get_votes')
    self.assertEqual(200 , request.status_code)

  def test_expenses_status(self):
    request = self.client.get('/api/expenses')
    self.assertEqual(200 , request.status_code)

  def test_get_all_propositions_status(self):
    request = self.client.get('/api/get_all_propositions')
    self.assertEqual(200 , request.status_code)

  def test_delet_deputados_status(self):
    data_expected = 'Deputados apagados com sucesso'

    request = self.client.get('/api/remover_deputados')
    self.assertEqual(200 , request.status_code)
    self.assertNotEqual(data_expected , request.data.decode())

  def tearDown(self):
      self.context.pop()

  @requests_mock.Mocker()
  def test_update_deputies(self, request_mock):
    url = 'https://dadosabertos.camara.leg.br/arquivos/deputados/json/deputados.json'
    data = {
      "dados": [
        {
          "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/2",
          "nome": "LOPES GAMA",
          "idLegislaturaInicial": 1,
          "idLegislaturaFinal": 2,
          "nomeCivil": "Caetano Maria Lopes Gama",
          "siglaSexo": "M",
          "urlRedeSocial": [],
          "urlWebsite": [],
          "dataNascimento": "1795-08-05",
          "dataFalecimento": "1864-06-21",
          "ufNascimento": "PE",
          "municipioNascimento": "Recife"
        }
      ]
    }

    data_expected = 'Done. Use /deputies to get all deputies in data base.'

    request_mock.get(url, json=data)
    request = self.client.get('/api/atualizar_deputados')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected, request.data.decode())

  @requests_mock.Mocker()
  def test_update_votes(self, request_mock):
    url = 'https://dadosabertos.camara.leg.br/api/v2/votacoes?ordem=DESC&ordenarPor=dataHoraRegistro'
    data = {
    "dados": [
        {
            "id": "2250723-31",
            "uri": "https://dadosabertos.camara.leg.br/api/v2/votacoes/2250723-31",
            "data": "2021-05-13",
            "dataHoraRegistro": "2021-05-13T16:10:19",
            "siglaOrgao": "SECAP(SGM)",
            "uriOrgao": "https://dadosabertos.camara.leg.br/api/v2/orgaos/100001",
            "uriEvento": null,
            "proposicaoObjeto": null,
            "uriProposicaoObjeto": null,
            "descricao": "Realizar o encaminhamento do PL-2228/2020 à CSSF (tramitação simultânea), em razão da aprovação de requerimento de urgência.",
            "aprovacao": 1
        },
        {
            "id": "2250723-30",
            "uri": "https://dadosabertos.camara.leg.br/api/v2/votacoes/2250723-30",
            "data": "2021-05-13",
            "dataHoraRegistro": "2021-05-13T16:10:14",
            "siglaOrgao": "SECAP(SGM)",
            "uriOrgao": "https://dadosabertos.camara.leg.br/api/v2/orgaos/100001",
            "uriEvento": null,
            "proposicaoObjeto": null,
            "uriProposicaoObjeto": null,
            "descricao": "Realizar o encaminhamento do PL-2228/2020 à CFT (tramitação simultânea), em razão da aprovação de requerimento de urgência.",
            "aprovacao": 1
        }
      ]
    }

    data_expected = 'Done! Use api/get_votes url to get all votes in database'

    request_mock.get(url, json=data)
    request = self.client.get('/api/update_votes')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected, request.data.decode())

  def tearDown(self):
    self.context.pop()


if __name__=='__main__':
    unittest.main()
