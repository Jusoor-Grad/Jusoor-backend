# Generated by Django 4.2.10 on 2024-02-20 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0014_alter_therapistassignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('PENDING_THERAPIST', 'Pending Therapist'), ('PENDING_PATIENT', 'Pending Patient'), ('CONFIRMED', 'Confirmed'), ('CANCELLED_BY_PATIENT', 'Cancelled By Patient'), ('CANCELLED_BY_THERAPIST', 'Cancelled By Therapist'), ('COMPLETED', 'Completed')], max_length=40),
        ),
    ]
