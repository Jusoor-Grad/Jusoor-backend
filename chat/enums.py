from django.utils.translation import gettext_lazy as _

PENDING = 'PENDING'
REVIEWED = 'REVIEWED'

FEEDBACK_STATUSES = {
    PENDING: _('the chat room feedback is pending'),
    REVIEWED: _('the chat room feedback has been reviewed'),
}

# inputs to avoid blacklisting
BLACKLIST_INPUTS = [
    r'.*(update|alter|change|read|show|view|delete|ignore|abandon|discard|remove|destroy).+prompt.*',
    r'.*(ignore|discard)(\s+|\s+.+\s+)above.*',
]