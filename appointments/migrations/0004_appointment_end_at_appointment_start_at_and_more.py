# Generated by Django 4.2.9 on 2024-02-05 15:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_studentpatient_entry_date'),
        ('appointments', '0003_therapistassignment_delete_therapistassignmentshift'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='end_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 5, 15, 31, 26, 553560, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='start_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 5, 15, 31, 52, 160733, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='therapistassignment',
            name='status',
            field=models.CharField(choices=[('PENDING_THERAPIST', 'Pending Therapist'), ('PENDING_PATIENT', 'Pending Patient'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed'), ('MISSED', 'Missed')], default='Active', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='therapistassignment',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='therapist_assignments', to='appointments.appointment'),
        ),
        migrations.AlterField(
            model_name='therapistassignment',
            name='therapist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointment_assignments', to='core.therapist'),
        ),
    ]