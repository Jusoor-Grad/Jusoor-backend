# Generated by Django 4.2.9 on 2024-02-09 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_studentpatient_entry_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='therapist',
            name='speciality',
        ),
    ]