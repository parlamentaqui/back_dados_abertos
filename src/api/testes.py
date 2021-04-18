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

    