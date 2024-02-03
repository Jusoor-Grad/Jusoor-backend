"""
    All notification-related asyn task definitions
"""

from celery import shared_task
from django.core.mail import send_mail

@shared_task()
def send_notification(msg):
    send_mail(
        'Testing celery',
        msg,
        'mohababubakir2001@gmail.com',
        ['mohababubakir2001@gmail.com']
    )



