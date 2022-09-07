from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework import serializers, status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from predictor.models import ModelSink, PredictionsHistory
from predictor.serializer import RegisterModelSerializer, RegisterModelSerializerRequest
from predictor.serializer import PredictionsHistorySerializer, PredictionsHistorySerializerRequest
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from django.db.utils import IntegrityError


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
