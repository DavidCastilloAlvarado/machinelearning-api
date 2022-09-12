from django.test import TestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory
from ml_api.predictor.views import RegisterModelApiView
from ml_api.users.models import User
from ml_api.users.tests.factories import UserFactory
from rest_framework.test import APIClient
from ml_api.predictor.tests.test_register import INPUT_DATA as INPUT_MODEL_DATA
import os
# Create your tests here.

X_INPUT = {
    "age": 41,
    "sex": "M",
    "chestPainType": "ATA",
    "restingBP": 140,
    "cholesterol": 289,
    "fastingBS": 0,
    "restingECG": "Normal",
    "maxHR": 123,
    "exerciseAngina": "N",
    "oldpeak": 1.5,
    "sTSlope": "Flat",
}


class Prediction(TestCase):
    x_input = X_INPUT

    def test_prediction(self,):
        """
        Test a single sample after save a model in the database

        """
        os.system("cp ./ml_api/predictor/tests/resources/**.joblib ./")
        client = APIClient()
        user = UserFactory(username='david')
        client.force_authenticate(user=user)
        # save the model
        response = client.post('/api/ml/model/register/', INPUT_MODEL_DATA, format='json')
        assert response.status_code == 201
        assert type(response.data.get('id')) == int

        id_model = response.data.get('id')
        # create prediction
        response = client.post(f'/api/ml/model/heart-failure/predict/?id={id_model}', self.x_input, format='json')
        assert response.status_code == 200

    def test_multi_prediction(self,):
        """
        Test a multi samples at the same time after save a model in the database

        """
        os.system("cp ./ml_api/predictor/tests/resources/**.joblib ./")
        client = APIClient()
        user = UserFactory(username='david')
        client.force_authenticate(user=user)
        # save the model
        response = client.post('/api/ml/model/register/', INPUT_MODEL_DATA, format='json')
        assert response.status_code == 201
        assert type(response.data.get('id')) == int

        id_model = response.data.get('id')
        assert id_model == 1
        # create prediction
        response = client.post(
            f'/api/ml/model/heart-failure/predict/?id={id_model}&many=true', [self.x_input, self.x_input, self.x_input], format='json')
        assert response.status_code == 200
