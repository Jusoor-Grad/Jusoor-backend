from core.viewssets import AugmentedViewSet
from django.utils.translation import gettext_lazy as _
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin


class SentimentReportViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    
    serializer_class_by_action = {
        # 'list': SentimentReportSerializer,
        # 'retrieve': SentimentReportSerializer,
        # 'create': SentimentReportCreateSerializer
    }

    queryset_by_action = {}


class MessageSentimentViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin):
    
    serializer_class = None

    queryset_by_action = {}