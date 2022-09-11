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
    age = serializers.IntegerField(help_text="age of the patient [years]")
    sex = serializers.CharField(help_text="sex of the patient [M: Male, F: Female]")
    chestPainType = serializers.CharField(help_text="""chest pain type [TA: Typical Angina, ATA: Atypical Angina, 
                                          NAP: Non-Anginal Pain, ASY: Asymptomatic]""")
    restingBP = serializers.FloatField(help_text="resting blood pressure [mm Hg]")
    cholesterol = serializers.FloatField(help_text="serum cholesterol [mm/dl]")
    fastingBS = serializers.FloatField(help_text="fasting blood sugar [1: if FastingBS > 120 mg/dl, 0: otherwise]")
    restingECG = serializers.CharField(help_text="""resting electrocardiogram results [Normal: Normal, ST: having ST-T wave
                                                    abnormality (T wave inversions and/or ST elevation or depression of > 0.05 mV), LVH:
                                                    showing probable or definite left ventricular hypertrophy by Estes' criteria]""")
    maxHR = serializers.FloatField(help_text="maximum heart rate achieved [Numeric value between 60 and 202]")
    exerciseAngina = serializers.CharField(help_text="exercise-induced angina [Y: Yes, N: No]")
    oldpeak = serializers.FloatField(help_text="ST [Numeric value measured in depression]")
    sTSlope = serializers.CharField(help_text="""the slope of the peak exercise ST segment [Up: upsloping, Flat: 
                                    flat, Down:downsloping]""")

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
