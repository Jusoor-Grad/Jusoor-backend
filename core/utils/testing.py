from typing import Dict
from urllib import parse
from authentication.models import User
from rest_framework.test import force_authenticate


def auth_request(factory_function, url: str, body: Dict = None, user: User = User.objects.get(username="muhabmaster"), query_params: Dict = None, format: str = "json"):
    """
    a function that creates an authneticated request given an endpoint, a user object, optional query params, and a body
    """
    query_string = ""
    if query_params:
        query_string += "?" + parse.urlencode(query_params)
    request = factory_function(url + query_string, data=body, format=format)

    force_authenticate(request, user=user)

    return request
