from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet
from rest_framework import serializers, status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.schemas.openapi import AutoSchema
from ml_api.predictor.models import ModelSink
from ml_api.predictor.serializer import RegisterModelSerializer


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


class RegisterModelApiView(ViewSet,
                           generics.CreateAPIView,
                           generics.RetrieveAPIView,
                           generics.UpdateAPIView,
                           generics.DestroyAPIView
                           ):
    schema = AutoSchema(tags=["models", "upload"])
    pagination_class = ModelsResultsPagination
    modelset = ModelSink
    permission_classes = [AllowAny]
    queryset = modelset.objects.all()
    serializer_class = RegisterModelSerializer
