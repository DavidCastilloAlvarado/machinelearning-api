import os

import joblib
import pandas as pd
from django.core.cache import cache
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, generics, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet
from sklearn.pipeline import make_pipeline

from ml_api.predictor.models import ModelSink, PredictionsHistory
from ml_api.predictor.serializer import (
    PerformPredictionHeartFailureSerializer,
    PerformPredictionIdModelSerializer,
    PerformPredictionOutputSerializer,
    PredictionsHistorySerializer,
    PredictionsHistorySerializerRequest,
    RegisterModelSerializer,
)
from ml_api.utils.gcs import download_to_file


class ModelsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 5

    def get_paginated_response(self, data):
        n_pages = self.page.paginator.count // self.page_size
        n_pages = n_pages + 1 if self.page.paginator.count % self.page_size else n_pages
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "pages_count": n_pages,
                "results": data,
            }
        )


@extend_schema_view(
    list=extend_schema(
        parameters=[PredictionsHistorySerializerRequest],
        description="""List all your model in the database""",
    ),
    create=extend_schema(
        description="""
        Create new models, and ensure that your blob URLs 
        will be available to the server IAM control."""
    ),
    retrieve=extend_schema(
        description="""Call an specific model using the unique <b>id</b> in the database"""
    ),
    update=extend_schema(description="""Update the values of a model already saved"""),
    destroy=extend_schema(
        description="""Destroy a machine learning model from the database using his <b>id</b>"""
    ),
)
@extend_schema(
    tags=["Model Registration"],
)
class RegisterModelApiView(
    ViewSet,
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
    generics.ListAPIView,
):
    pagination_class = ModelsPagination
    modelset = ModelSink
    permission_classes = [IsAuthenticated]
    queryset = modelset.objects.all()
    serializer_class = RegisterModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_backends += [filters.OrderingFilter]
    filter_backends += [filters.SearchFilter]
    filterset_fields = ["version", "algorithm"]
    search_fields = ["name", "algorithm"]
    ordering_fields = ["version", "-version"]
    ordering = ["-version"]
    throttle_scope = "registration"

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            raise serializers.ValidationError(e)


@extend_schema_view(
    list=extend_schema(
        parameters=[PredictionsHistorySerializerRequest],
        description="""List the history of a model o model base on filters

                                                        - algorithm name

                                                        - version

                                                        - order by creation date""",
    ),
    retrieve=extend_schema(description="""Retrieve an individual record"""),
)
@extend_schema(
    tags=["Predictions History"],
)
class PredictionsHistoryApiView(
    ViewSet,
    # generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.ListAPIView,
):
    pagination_class = ModelsPagination
    modelset = PredictionsHistory
    permission_classes = [AllowAny]
    queryset = modelset.objects.all()
    serializer_class = PredictionsHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filter_backends += [filters.OrderingFilter]
    filter_backends += [filters.SearchFilter]
    filterset_fields = ["algorithm__version", "algorithm__algorithm"]
    search_fields = ["algorithm__name", "algorithm__algorithm"]
    ordering_fields = ["created_at", "-created_at"]
    ordering = [
        "-created_at",
    ]
    throttle_scope = "history"

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            raise serializers.ValidationError(e)


@extend_schema_view(
    predict=extend_schema(
        parameters=[PerformPredictionIdModelSerializer],
        description="""
        To perform prediction using the selected model in the parameter <b>id</b> which is the id model. <br>
        - You can send one or multiples records at the same time, usign the flag many true/false <br>
        - If you are in many true mode, then your input must be a list of jsons records.""",
        responses={
            "200": PerformPredictionOutputSerializer,
            "429": OpenApiResponse(
                description="Request was throttled. Expected available in 2 second."
            ),
        },
        request=PerformPredictionHeartFailureSerializer,
        examples=[
            OpenApiExample(
                "Heart failure example 1",
                summary="example from the challenge doc",
                description="""send a single record and then recive a fload number (probability)
                            of the heart failure in that patient""",
                value={
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
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Heart failure example 1",
                summary="example from the challenge doc",
                value={"prob": 0.8996033992826433},
                request_only=False,
                response_only=True,
            ),
        ],
    ),
)
@extend_schema(
    tags=["Predictor"],
)
class PerformPredictionApiView(
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = PerformPredictionHeartFailureSerializer
    allowed_methods = ["POST"]
    throttle_scope = "perform"

    def __load_files_data(self, file_name, serializer, record_field):
        _loaded = cache.get(file_name)
        if _loaded is None:
            if not os.path.isfile(file_name):
                file_name = download_to_file(
                    serializer["id"].get(record_field), file_name
                )
            _loaded = joblib.load(file_name)
            cache.set(file_name, _loaded, 60 * 60)
        return _loaded

    def __load_model(self, serializer):
        pipeline_name = f"model_pipeline_{serializer['id']['id']}"
        pipe = cache.get(pipeline_name)
        if pipe is None:
            model_file = f"./model_{serializer['id']['id']}.joblib"
            encod_file = f"./encoder_{serializer['id']['id']}.joblib"
            model_loaded = self.__load_files_data(model_file, serializer, "url")
            ct_loaded = self.__load_files_data(encod_file, serializer, "url_encoder")
            pipe = make_pipeline(ct_loaded, model_loaded)
            cache.set(pipeline_name, pipe, 60 * 5)

        return pipe

    def __save_prediction(
        self,
        serializer,
        data,
        output,
    ):
        record = dict(
            input_data=data.to_dict("records"),  # array of dicts
            full_response=output,  # dict
            response=output if type(output) == list else [output],  # array of dicts
            algorithm=ModelSink.objects.get(
                id=serializer["id"]["id"]
            ),  # Modelsink object
            comments="",  # string
        )
        PredictionsHistory.objects.create(**record)

    @action(detail=False, methods=["POST"])
    def predict(self, request, *args, **kwargs):
        params = PerformPredictionIdModelSerializer(data=request.GET)
        params.is_valid(raise_exception=True)

        # serialize options params
        model_reg = params.validated_data
        many = model_reg.get("many")

        # Reading data request
        data = self.serializer_class(data=request.data, many=many)
        data.is_valid(raise_exception=True)

        # loading the Model
        pipe = self.__load_model(model_reg)

        # Prepare input
        if many:
            x_input = pd.DataFrame.from_records(data.data)
        else:
            x_input = pd.DataFrame.from_records([data.data])

        # Perform prediction
        try:
            output = pipe.predict_proba(x_input)[:, 1]
        except Exception as e:
            return Response(
                {"error": str(e), "model_description": model_reg["id"]["description"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare output
        if not many:
            output = dict(prob=output.tolist()[0])
        else:
            output = [dict(prob=item) for item in output.tolist()]

        output = PerformPredictionOutputSerializer(output, many=many)
        self.__save_prediction(model_reg, x_input, output.data)
        return Response(output.data, status=status.HTTP_200_OK)
