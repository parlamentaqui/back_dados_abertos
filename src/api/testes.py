import unittest
import requests
import mock
from api import *


class EndpointGETTestCase(unittest.TestCase):

  def setUp(self):
    self.client = mock.Mock(spec=requests)
    self.data = EndpointGETTestCase(self.client)

  def test_status_server_deputies(self):
    self.client.get.return_value = mock.Mock(status_code=200)

    response = self.data.deputados()

    self.assertEqual(200, response.status_code)

  def test_deputado_especifico(self):
    return_json = {
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
          "nome": "Abílio Santana",
          "nomeEleitoral": "Abílio Santana",
          "siglaPartido": "PL",
          "siglaUf": "BA",
          "situacao": "Exercício",
          "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/204554",
          "uriPartido": "https://dadosabertos.camara.leg.br/api/v2/partidos/37906",
          "urlFoto": "https://www.camara.leg.br/internet/deputado/bandep/204554.jpg"
      },
      "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/204554",
      "urlWebsite": null
    }

    mock_response = mock.Mock(status_code=200)
    mock_response.json.ver_deputado = return_json
    self.client.get.ver_deputado = mock_response

    response = self.data.ver_deputado(204554)

    content = response.json()

    self.assertEqual('JOSE ABILIO SILVA DE SANTANA', content['nomeCivil'])
    self.assertNotEqual('Joao da Silva', content['nomeCivil'])

  def test_federative_unities(self):
    return_json = {
        "name": "Acre",
        "uf": "AC"
    }

    mock_response = mock.Mock(status_code=200)
    mock_response.json.federative_unities = return_json
    self.client.get.federative_unities = mock_response

    response = self.data.federative_unities()

    content = response.json()

    self.assertEqual('Acre', content['name'])
    self.assertEqual('AC', content['uf'])
