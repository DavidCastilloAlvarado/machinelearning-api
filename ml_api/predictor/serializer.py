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


class PerformPredictionOutputSerializer(serializers.Serializer):
    prob = serializers.FloatField()


class PerformPredictionHeartFailureSerializer(serializers.Serializer):
    # data = serializers.JSONField()
    Age = serializers.IntegerField()
    Sex = serializers.CharField()
    ChestPainType = serializers.CharField()
    RestingBP = serializers.FloatField()
    Cholesterol = serializers.FloatField()
    FastingBS = serializers.FloatField()
    RestingECG = serializers.CharField()
    MaxHR = serializers.FloatField()
    ExerciseAngina = serializers.CharField()
    Oldpeak = serializers.FloatField()
    ST_Slope = serializers.CharField()


class PerformPredictionIdModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    many = serializers.BooleanField(default=False)

    class Meta:
        model = ModelSink

    def validate(self, attrs):
        if not self.Meta.model.objects.filter(id=attrs['id']).exists():
            raise serializers.ValidationError("model id doesn\'t exists")
        model = self.Meta.model.objects.get(id=attrs['id'])
        model = RegisterModelSerializer(model)
        attrs['id'] = model.data
        return attrs
