from django.test import TestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from ml_api.predictor.views import RegisterModelApiView
from ml_api.users.models import User
from ml_api.users.tests.factories import UserFactory
from rest_framework.test import APIClient
# Create your tests here.

INPUT_DATA = {"name": "LightGBM classifier",
              "description": "Test model as a probe of concept of machine learning ops module",
              "algorithm": "lgbmc",
              "status": "dev",
              "version": "0.1.4",
              "url": "https://storage.cloud.google.com/ml-api-storage/models/lgbmc/11-09-22/3e7caa669f6b9a2e6b81b3e9bc654806.joblib",
              "url_encoder": "https://storage.cloud.google.com/ml-api-storage/models/lgbmc/11-09-22/1dc3167d855607095c35f0459fc0bf5a.joblib",
              "sample_input": {"Age": 56, "Sex": "M",
                               "ChestPainType": "ASY",
                               "RestingBP": 130,
                               "Cholesterol": 0, "FastingBS": 0,
                               "RestingECG": "Normal", "MaxHR": 120,
                               "ExerciseAngina": "N", "Oldpeak": 0.0,
                               "ST_Slope": "Flat"},
              "sample_output": {"output": 0.9612178468946518},
              "metrics": [{"accuracy_score": 0.8732}]}


class RegisterModel(TestCase):
    input_data = INPUT_DATA

    def test_registration(self,):
        """
        Register a model in the database with the values created above.
        """

        client = APIClient()
        user = UserFactory(username='david')
        client.force_authenticate(user=user)
        response = client.post('/api/ml/model/register/', self.input_data, format='json')
        assert response.status_code == 201

    def test_duplicate_keys(self,):
        """
        Register two models with the same key primaries and trigger an error 
        """
        client = APIClient()
        user = UserFactory(username='david')
        client.force_authenticate(user=user)
        response = client.post('/api/ml/model/register/', self.input_data, format='json')
        assert response.status_code == 201
        response = client.post('/api/ml/model/register/', self.input_data, format='json')
        assert response.status_code != 201
