import unittest
from app import app
from mongoengine import connect, disconnect
from flask import Flask
import requests_mock

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

  @classmethod
  def setUpClass(cls):
    disconnect()
    connect('prlmntq_db_test', host='mongomock://localhost')

  @classmethod
  def tearDownClass(cls):
    disconnect()
  
  def setUp(self):
    self.app = app
    self.app.testing = True
    self.context = self.app.test_request_context()
    self.context.push()
    self.client = self.app.test_client()
      
  def test_federative_unities(self):
    request = self.client.get('/api/federative_unities')
    self.assertEqual(200 , request.status_code)

  def test_parties_status(self):
    request = self.client.get('/api/parties')
    self.assertEqual(200 , request.status_code)

  def test_get_votes_status(self):
    request = self.client.get('/api/get_votes')
    self.assertEqual(200 , request.status_code)

  def test_get_votes_by_deputy_id_status(self):
    request = self.client.get('/api/get_votes_by_deputy_id/3')
    data_expected = '[]\n'

    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_expenses_status(self):
    request = self.client.get('/api/expenses')
    self.assertEqual(200 , request.status_code)

  def test_expenses_by_id_status(self):
    request = self.client.get('/api/expenses/3')
    self.assertEqual(200 , request.status_code)

  def test_deputies_status(self):
    request = self.client.get('/api/deputies')
    self.assertEqual(200 , request.status_code)

  def test_deputies_by_id_status(self):
    request = self.client.get('/api/deputies/3')
    data_expected = '{}\n'

    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_get_all_propositions_status(self):
    request = self.client.get('/api/get_all_propositions')
    self.assertEqual(200 , request.status_code)

  def test_get_proposition_by_id(self):
    request = self.client.get('/api/get_proposition_by_id/3')
    data_expected = '{}\n'

    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_delet_deputados_status(self):
    data_expected = 'Deputados apagados com sucesso'

    request = self.client.get('/api/remover_deputados')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_update_expenses(self):
    data_expected = 'Done. Use api/expenses to get all expenses in data base.'

    request = self.client.get('/api/update_expenses')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_delete_expenses(self):
    data_expected = 'All expenses in database was deleted! Use api/update_expenses to update database.'

    request = self.client.get('/api/delete_expenses')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_delete_propositions(self):
    data_expected = 'Proposicoes apagadas com sucesso'

    request = self.client.get('/api/delete_propositions')
    self.assertEqual(200 , request.status_code)
    self.assertEqual(data_expected , request.data.decode())

  def test_delete_votesd(self):
    request = self.client.get('/api/get_proposition_by_id/3')
    data_expected = 'All votes in database were deleted! Use api/update_votes to update database.'

    self.assertEqual(200 , request.status_code)
    self.assertNotEqual(data_expected , request.data.decode())
    
  # def test_update_propositions(self):
  #   data_expected = 'Proposições atualizadas com sucesso.'

  #   request = self.client.get('/api/update_propositions')
  #   self.assertEqual(200 , request.status_code)
  #   self.assertNotEqual(data_expected , request.data.decode())

  # def test_update_deputies(self):
  #   data_expected = 'Done. Use /deputies to get all deputies in data base.'

  #   request = self.client.get('/api/atualizar_deputados')
  #   self.assertEqual(200 , request.status_code)
  #   self.assertEqual(data_expected, request.data.decode())

  # def test_update_votes(self):
  #   data_expected = 'Done! Use api/get_votes url to get all votes in database'

  #   request = self.client.get('/api/update_votes')
  #   self.assertEqual(200 , request.status_code)
  #   self.assertEqual(data_expected, request.data.decode())

  def tearDown(self):
    self.context.pop()


if __name__=='__main__':
    unittest.main()
