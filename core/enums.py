from enum import Enum


class UserRole(Enum):
    THERAPIST = 'therapist'
    PATIENT = 'patient'


class QuerysetBranching(Enum):
    USER_GROUP = 'group'
    PERMISSION = 'permission'

PATIENT_PROFILE_FIELD = 'patient_profile'
THERAPIST_PROFILE_FIELD = 'therapist_profile'