"""
all HTTP-related utilities

"""
from rest_framework import status
from rest_framework.response import Response
from .placeholders import ERROR, SUCCESS
from typing import Dict, Optional

def FormattedResponse(data: Optional[Dict] = None, status = status.HTTP_200_OK, message: str = SUCCESS)  -> Response:
    """Utility function to format all HTTP API respones into same format"""

    
    return Response({
        'status': status,
        'data': data,
        'message': message
    }, status=status)