"""
    Defining all core permissions for the system
"""



from authentication.utils import HasLambdaPerm
from core.models import StudentPatient, Therapist
from rest_framework.permissions import IsAuthenticated


def IsTherapist():
    """
        Permission to only allow access to therapists
    """

    def validate_role(request, view):
        return IsAuthenticated().has_permission(request=request, view=view) and Therapist.objects.filter(user=request.user).exists()

    return HasLambdaPerm(validate_role)

def IsPatient():
    """
        Permission to only allow access to patients
    """

    def validate_role(request, view):
        return IsAuthenticated().has_permission(request=request, view=view) and  StudentPatient.objects.filter(user=request.user).exists()

    return HasLambdaPerm(validate_role)