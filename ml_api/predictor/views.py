from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework import serializers, status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from predictor.models import ModelSink, PredictionsHistory
from predictor.serializer import RegisterModelSerializer, RegisterModelSerializerRequest
from predictor.serializer import PredictionsHistorySerializer, PredictionsHistorySerializerRequest, PerformPredictionHeartFailureSerializer, PerformPredictionIdModelSerializer, PerformPredictionOutputSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from django.db.utils import IntegrityError
import joblib
from sklearn.pipeline import make_pipeline
from lightgbm import LGBMClassifier
from ml_api.utils.gcs import download_to_file
from django.core.cache import cache
import pandas as pd
import logging
import os


class ModelsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5

    def get_paginated_response(self, data):
        n_pages = self.page.paginator.count//self.page_size
        n_pages = n_pages + 1 if self.page.paginator.count % self.page_size else n_pages
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'pages_count': n_pages,
            'results': data
        })


@extend_schema_view(list=extend_schema(parameters=[PredictionsHistorySerializerRequest],
                                       description="""List all your model in the database"""),
                    create=extend_schema(
                        description="""Create a new models, ensure that your url will be under server IAM control """),
                    retrieve=extend_schema(
                        description="""Call an specific model using the unique <b>id</b> in the database"""),
                    update=extend_schema(
                        description="""Update the values of a model already saved"""),
                    destroy=extend_schema(
                        description="""Destroy a machine learning model from the database using his <b>id</b>"""),
                    )
@extend_schema(tags=['Register a model'],)
class RegisterModelApiView(ViewSet,
                           generics.CreateAPIView,
                           generics.RetrieveAPIView,
                           generics.UpdateAPIView,
                           generics.DestroyAPIView,
                           generics.ListAPIView,
                           ):
    pagination_class = ModelsPagination
    modelset = ModelSink
    permission_classes = [AllowAny]
    queryset = modelset.objects.all()
    serializer_class = RegisterModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_backends += [filters.OrderingFilter]
    filter_backends += [filters.SearchFilter]
    filterset_fields = ['version', 'algorithm']
    search_fields = ['name', 'algorithm']
    ordering_fields = ['version', '-version']
    ordering = ['-version']

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            raise serializers.ValidationError(e)


@extend_schema_view(list=extend_schema(parameters=[PredictionsHistorySerializerRequest],
                                       description="""List the history of a model o model base on filters
                                       
                                                        - algorithm name
                                                        
                                                        - version
                                                        
                                                        - order by creation date"""),
                    create=extend_schema(
                        description="""Create a records inside the history model, but this only instructional, the history will be created internaly """),
                    retrieve=extend_schema(
                        description="""Retrieve an individual record"""),
                    )
@extend_schema(tags=['Predictions History'],)
class PredictionsHistoryApiView(ViewSet,
                                generics.CreateAPIView,
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
    filterset_fields = ['algorithm__version', 'algorithm__algorithm']
    search_fields = ['algorithm__name', 'algorithm__algorithm']
    ordering_fields = ['created_at', '-created_at']
    ordering = ['-created_at', ]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            raise serializers.ValidationError(e)


@extend_schema_view(predict=extend_schema(parameters=[PerformPredictionIdModelSerializer],
                                          description="""To perform prediction using the selected model in the parameter <b>id</b> which is the id model. """,
                                          responses={"200": PerformPredictionOutputSerializer, },
                                          request=PerformPredictionHeartFailureSerializer,
                                          ),

                    )
@extend_schema(tags=['Predictor'],)
class PerformPredictionApiView(GenericViewSet, ):
    permission_classes = [AllowAny]
    serializer_class = PerformPredictionHeartFailureSerializer
    allowed_methods = ['POST']

    def __load_files_data(self, file_name, serializer, record_field):
        _loaded = cache.get(file_name)
        if _loaded is None:
            if not os.path.isfile(file_name):
                file_name = download_to_file(serializer['id'].get(record_field), file_name)
            _loaded = joblib.load(file_name)
            cache.set(file_name, _loaded,  60*60)
        return _loaded

    def __load_model(self, serializer):
        pipeline_name = f"model_pipeline_{serializer['id']['id']}"
        pipe = cache.get(pipeline_name)
        if pipe is None:
            model_file = f"./model_{serializer['id']['id']}.joblib"
            encod_file = f"./encoder_{serializer['id']['id']}.joblib"
            model_loaded = self.__load_files_data(model_file, serializer, 'url')
            ct_loaded = self.__load_files_data(encod_file, serializer, 'url_encoder')
            pipe = make_pipeline(ct_loaded, model_loaded)
            cache.set(pipeline_name, pipe,  60*5)

        return pipe

    def __save_prediction(self, serializer, data, output,):
        record = dict(
            input_data=data.to_dict('records'),  # array of dicts
            full_response=output,  # dict
            response=output if type(output) == list else [output],  # array of dicts
            algorithm=ModelSink.objects.get(id=serializer['id']['id']),  # Modelsink object
            comments="",  # string

        )
        print(record)
        PredictionsHistory.objects.create(**record)

    @action(detail=False, methods=['POST'])
    def predict(self, request, *args, **kwargs):
        params = PerformPredictionIdModelSerializer(data=request.GET)
        params.is_valid(raise_exception=True)

        # serialize options params
        model_reg = params.validated_data
        many = model_reg.get('many')

        # Reading data request
        data = self.serializer_class(data=request.data, many=many)
        data.is_valid(raise_exception=True)

        # loading the Model
        pipe = self.__load_model(model_reg)

        # Prepare input
        if many:
            x_input = pd.DataFrame.from_records(data.validated_data)
        else:
            x_input = pd.DataFrame.from_records([data.validated_data])

        # Perform prediction
        try:
            output = pipe.predict_proba(x_input)[:, 1]
        except Exception as e:
            return Response({"error": e, "model_description": model_reg['id']['description']}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare output
        if not many:
            output = dict(prob=output.tolist()[0])
        else:
            output = [dict(prob=item) for item in output.tolist()]

        output = PerformPredictionOutputSerializer(output, many=many)
        self.__save_prediction(model_reg, x_input, output.data)
        return Response(output.data, status=status.HTTP_200_OK)
