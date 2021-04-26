import mock
import unittest
import requests
import requests_mock
from "../app" import app


class EndpointGETTestCase(unittest.TestCase):

  def setUp(self):
    self.app = app()
    
  @requests_mock.Mocker()
  def test_deputies_only(self, request_mock):
    url = 'http://0.0.0.0:8004/api/deputado_especifico/204554'
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

    request_mock.get(url, json=data)
    request_mock.status_code(200)
    
    self.assertEqual(self.app.ver_deputado('204554'), return_json)
    self.assertEqual('JOSE ABILIO SILVA DE SANTANA', return_json['nomeCivil'])
    self.assertNotEqual('Joao da Silva', return_json['nomeCivil'])


  @requests_mock.Mocker()
  def test_federative_unities(self, request_mock):
    url =  'federative_unities'
    return_json = [
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

    self.assertEqual(self.app.federative_unities(), return_json)

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
