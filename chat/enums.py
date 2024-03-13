from django.utils.translation import gettext_lazy as _

PENDING = 'PENDING'
REVIEWED = 'REVIEWED'

FEEDBACK_STATUSES = {
    PENDING: _('the chat room feedback is pending'),
    REVIEWED: _('the chat room feedback has been reviewed'),
}