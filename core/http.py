"""
all HTTP-related utilities

"""
from copy import copy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .placeholders import ERROR, SUCCESS
from typing import Dict, Optional
from rest_framework.views import exception_handler

def FormattedResponse(data: Optional[Dict] = None, status = status.HTTP_200_OK, message: str = SUCCESS)  -> Response:
    """Utility function to format all HTTP API respones into same format"""
  
    return Response({
        'status': status,
        'data': data,
        'message': message
    }, status=status)

def FormattedValidationError(message: str) -> ValidationError:
    """Utility function to format all HTTP API respones into same format"""
    return ValidationError({
        'status': status.HTTP_400_BAD_REQUEST,
        'message': message,
        'data': None
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
            'data': data,
            'status': response.status_code,
            'message': response.status_text
        }

    return response

    

