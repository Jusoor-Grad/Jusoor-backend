# Generated by Django 5.0.4 on 2024-04-16 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_mentalhealthspecialization_therapistspecialization'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentpatient',
            name='overall_sentiment_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True),
        ),
    ]