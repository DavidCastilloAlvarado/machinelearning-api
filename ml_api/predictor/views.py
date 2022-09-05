from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework import serializers, status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from predictor.models import ModelSink
from predictor.serializer import RegisterModelSerializer, RegisterModelSerializerRequest
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action


class ModelsResultsPagination(PageNumberPagination):
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


@extend_schema_view(list=extend_schema(parameters=[RegisterModelSerializerRequest],))
@extend_schema(tags=['Register a model'],)
class RegisterModelApiView(ViewSet,
                           generics.CreateAPIView,
                           generics.RetrieveAPIView,
                           generics.UpdateAPIView,
                           generics.DestroyAPIView,
                           generics.ListAPIView,
                           ):
    pagination_class = ModelsResultsPagination
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
