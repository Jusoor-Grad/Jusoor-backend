# Generated by Django 4.2.10 on 2024-02-22 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0015_alter_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
