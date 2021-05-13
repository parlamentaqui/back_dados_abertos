import unittest
from flask import url_for
import requests_mock
from app import app


class EtlTests(unittest.TestCase):

  def setUp(self):
    self.app = app
    self.app.testing = True
    self.context = self.app.test_request_context()
    self.context.push()
    self.client = self.app.test_client()

  def test_index_status(self):
    request = self.client.get(url_for('/'))
    self.assertEqual(200 , request.status_code)
      
  def test_index(self):
    request = self.client.get(url_for('/'))
    self.assertEqual('ETL Camara' , request.data.decode())
      
  @requests_mock.Mocker()
  def test_deputies_only(self, request_mock):
    url = 'https://dadosabertos.camara.leg.br/api/v2/deputados/204554'
    data = {
      "cpf": "36607606504",
      "dataFalecimento": null,
      "dataNascimento": "1965-02-13",
      "escolaridade": "Superior Incompleto",
      "id": 204554,
      "municipioNascimento": "Salvador",
      "nomeCivil": "JOSE ABILIO SILVA DE SANTANA",
      "redeSocial": [],
      "sexo": "M",
      "ufNascimento": "BA",
      "ultimoStatus": {
          "condicaoEleitoral": "Titular",
          "data": "2019-02-01T11:45",
          "descricaoStatus": null,
          "email": "dep.abiliosantana@camara.leg.br",
          "gabinete": {
              "andar": "5",
              "email": "dep.abiliosantana@camara.leg.br",
              "nome": "531",
              "predio": "4",
              "sala": "531",
              "telefone": "3215-5531"
          },
          "id": 204554,
          "idLegislatura": 56,
          "nome": "Abilio Santana",
          "nomeEleitoral": "Abilio Santana",
          "siglaPartido": "PL",
          "siglaUf": "BA",
          "situacao": "Exercicio",
          "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/204554",
          "uriPartido": "https://dadosabertos.camara.leg.br/api/v2/partidos/37906",
          "urlFoto": "https://www.camara.leg.br/internet/deputado/bandep/204554.jpg"
      },
      "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/204554",
      "urlWebsite": null
    }
    
    self.assertEqual(self.app.ver_deputado('204554'), return_json)
    self.assertEqual('JOSE ABILIO SILVA DE SANTANA', return_json['nomeCivil'])
    self.assertNotEqual('Joao da Silva', return_json['nomeCivil'])

    request_mock.get(url, json=data)
    request_mock.status_code(200)

    request = self.client.get(url_for('api.federative_unities'))

    self.assertEqual(200 , request.status_code)
    self.assertEqual(response , request.data.decode())

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

    request = self.client.get(url_for('api.federative_unities'))

    self.assertEqual(200 , request.status_code)
    self.assertEqual(response , request.data.decode())

  def test_parties_status(self):
    request = self.client.get(url_for('api.parties'))
    self.assertEqual(200 , request.status_code)

  def test_get_votes_status(self):
    request = self.client.get(url_for('api.get_votes'))
    self.assertEqual(200 , request.status_code)

  def test_expenses_status(self):
    request = self.client.get(url_for('api.expenses'))
    self.assertEqual(200 , request.status_code)

  def test_get_all_propositions_status(self):
    request = self.client.get(url_for('api.get_all_propositions'))
    self.assertEqual(200 , request.status_code)

  def test_delet_deputados_status(self):
    data_expected = 'Deputados apagados com sucesso'

    request = self.client.get(url_for('api.remover_deputados'))
    self.assertNotEqual(data_expected , request.data.decode())

  def tearDown(self):
      self.context.pop()

  @requests_mock.Mocker()
  def test_atualizar_deputados(self, request_mock):
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
    request = self.client.get(url_for('api.atualizar_deputados'))
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected, request.data.decode())

if __name__=='__main__':
    unittest.main()
