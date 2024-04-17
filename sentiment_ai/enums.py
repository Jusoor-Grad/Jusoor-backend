
#  report statuses




from django.utils.translation import gettext_lazy as _


PENDING = 'PENDING'
REJECTED = 'REJECTED'
COMPLETED = 'COMPLETED'
FAILED = 'FAILED'

REPORT_STATUSES = {
    PENDING: _('Pending'), ## the report is still being generated
    REJECTED: _('Rejected'), ## the report was rejected by the patient
    COMPLETED: _('Completed'), ## the report was successfully generated
    FAILED: _('Failed'), ## the report generation failed due to inconsistent schema errors
}
