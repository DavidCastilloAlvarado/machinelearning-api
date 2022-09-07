from rest_framework import serializers
from predictor.models import ModelSink, PredictionsHistory


class RegisterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSink
        fields = '__all__'
        read_only_fields = 'id',


class PredictionsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionsHistory
        fields = '__all__'
        read_only_fields = 'id',


class PredictionsHistorySerializerRequest(serializers.Serializer):
    ordering = serializers.ChoiceField(["created_at", "-created_at"], required=False)


class RegisterModelSerializerRequest(serializers.Serializer):
    ordering = serializers.ChoiceField(["version", "-version"], required=False)
