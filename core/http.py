"""
all HTTP-related utilities

"""
from copy import copy
from rest_framework import status
from rest_framework.response import Response as _Response
from rest_framework.exceptions import ValidationError as _ValidationError
from .placeholders import SUCCESS
from typing import Dict, Optional
from rest_framework.views import exception_handler

def Response(data: Optional[Dict] = None, status = status.HTTP_200_OK, message: str = SUCCESS)  -> _Response:
    """Utility function to format all HTTP API respones into same format"""
  
    return _Response({
        'status': status,
        'data': data,
        'message': message
    }, status=status)

def ValidationError(message: str) -> _ValidationError:
    """Utility function to format all HTTP API respones into same format"""
    return _ValidationError({
        'error': message,
        })


def formatted_error_handler(exc, context):
    """
        Custom exception handler used
        NOTE: to use this formatter always invoke raise_exception=True in serializer validation
    """

    response = exception_handler(exc, context)

    if response is not None:
        
        data= copy(response.data)
        response.data = {
            'data': {'errors': data},
            'status': response.status_code,
            'message': response.status_text
        }

    return response

    

