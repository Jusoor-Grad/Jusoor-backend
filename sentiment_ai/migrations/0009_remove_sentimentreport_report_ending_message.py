# Generated by Django 5.0.4 on 2024-05-02 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment_ai', '0008_messagesentiment_adhd_messagesentiment_anxiety_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentimentreport',
            name='report_ending_message',
        ),
    ]