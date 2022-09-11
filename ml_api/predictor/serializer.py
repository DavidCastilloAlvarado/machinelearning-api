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
    age = serializers.IntegerField()
    sex = serializers.CharField()
    chestPainType = serializers.CharField()
    restingBP = serializers.FloatField()
    cholesterol = serializers.FloatField()
    fastingBS = serializers.FloatField()
    restingECG = serializers.CharField()
    maxHR = serializers.FloatField()
    exerciseAngina = serializers.CharField()
    oldpeak = serializers.FloatField()
    sTSlope = serializers.CharField()

    def to_representation(self, instance):
        attrs = super().to_representation(instance)

        attrs_m = {}
        attrs_m['Age'] = attrs['age']
        attrs_m['Sex'] = attrs['sex']
        attrs_m['ChestPainType'] = attrs['chestPainType']
        attrs_m['RestingBP'] = attrs['restingBP']
        attrs_m['Cholesterol'] = attrs['cholesterol']
        attrs_m['FastingBS'] = attrs['fastingBS']
        attrs_m['RestingECG'] = attrs['restingECG']
        attrs_m['MaxHR'] = attrs['maxHR']
        attrs_m['ExerciseAngina'] = attrs['exerciseAngina']
        attrs_m['Oldpeak'] = attrs['oldpeak']
        attrs_m['ST_Slope'] = attrs['sTSlope']
        return attrs_m


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
