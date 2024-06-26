# Generated by Django 5.0.4 on 2024-04-18 16:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0014_delete_chatroom'),
        ('sentiment_ai', '0006_remove_reportsentimentmessage_sentiment_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentimentreport',
            name='report_ending_message',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='terminated_sentiment_report', to='chat.chatmessage'),
            preserve_default=False,
        ),
    ]
