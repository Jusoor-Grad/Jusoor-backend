# Generated by Django 5.0.4 on 2024-04-16 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_studentpatient_overall_sentiment_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentpatient',
            name='overall_sentiment_score',
        ),
    ]