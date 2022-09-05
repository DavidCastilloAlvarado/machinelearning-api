from rest_framework import serializers
from predictor.models import ModelSink


class RegisterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelSink
        fields = '__all__'
        read_only_fields = 'id',


class RegisterModelSerializerRequest(serializers.Serializer):
    ordering = serializers.ChoiceField(["version", "-version"], required=False)
