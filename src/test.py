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

if __name__=='__main__':
    unittest.main()
