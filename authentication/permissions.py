"""
    Defining all core permissions for the system
"""



from authentication.utils import HasLambdaPerm
from core.models import StudentPatient, Therapist


def IsTherapist():
    """
        Permission to only allow access to therapists
    """

    def validate_role(request, view):
        return Therapist.objects.filter(user=request.user).exists()

    return HasLambdaPerm(validate_role)

def IsPatient():
    """
        Permission to only allow access to patients
    """

    def validate_role(request, view):
        return StudentPatient.objects.filter(user=request.user).exists()

    return HasLambdaPerm(validate_role)