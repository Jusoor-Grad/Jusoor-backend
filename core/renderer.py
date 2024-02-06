from typing import Any
from h11 import ERROR
from rest_framework.viewsets import ModelViewSet

from core.http import Response
from core.placeholders import SUCCESS

from rest_framework.renderers import JSONRenderer

class FormattedJSONRenderrer(JSONRenderer):
    """Custom JSON renderer to format the response"""
    def render(self, data: Any, accepted_media_type: str = None, renderer_context: dict = None) -> bytes:
        """Format the response"""

        status_code = renderer_context['response'].status_code
        response = response = {
          "status": SUCCESS,
          "data": data,
          "message": None
        }

        if not str(status_code).startswith('2'):
            response["status"] = ERROR
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["data"] = data

        return super().render(response, accepted_media_type, renderer_context)