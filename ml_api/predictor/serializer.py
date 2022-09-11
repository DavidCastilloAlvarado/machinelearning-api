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


class PerformPredictionSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.JSONField())


class PerformPredictionIdModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        model = ModelSink

    def validate(self, attrs):
        if not self.Meta.model.objects.filter(id=attrs['id']).exists():
            raise serializers.ValidationError("model id doesn\'t exists")
        model = self.Meta.model.objects.get(id=attrs['id'])
        model = RegisterModelSerializer(model)
        attrs['id'] = model.data
        return attrs
