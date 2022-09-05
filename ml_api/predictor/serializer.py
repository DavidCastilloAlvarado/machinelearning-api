from rest_framework import serializers
from ml_api.predictor.models import ModelSink


class RegisterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSink
        fields = '__all__'
