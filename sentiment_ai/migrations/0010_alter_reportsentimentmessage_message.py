# Generated by Django 5.0.4 on 2024-05-02 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment_ai', '0009_remove_sentimentreport_report_ending_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportsentimentmessage',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sentiment_report', to='sentiment_ai.messagesentiment'),
        ),
    ]
