
from enum import Enum
from dateutil.rrule import SU, MO, TU, WE, TH, FR, SA

class UserRole(Enum):
    THERAPIST = 'therapist'
    PATIENT = 'patient'


class QuerysetBranching(Enum):
    USER_GROUP = 'group'
    PERMISSION = 'permission'

PATIENT_PROFILE_FIELD = 'patient_profile'
THERAPIST_PROFILE_FIELD = 'therapist_profile'


# ------------- temporal constants

day_mapper = {
    'sunday': SU,
    'monday': MO,
    'tuesday': TU,
    'wednesday': WE,
    'thursday': TH,
}