# Generated by Django 4.2.9 on 2024-02-04 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_studentpatient_entry_date'),
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TherapistAssignmentShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shifts', to='appointments.appointment')),
                ('new_therapist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shifts_taken', to='core.therapist')),
                ('old_therapist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shifts', to='core.therapist')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
