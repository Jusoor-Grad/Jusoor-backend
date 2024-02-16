# Generated by Django 4.2.9 on 2024-02-09 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_therapist_speciality'),
        ('appointments', '0008_delete_appointmentfeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientreferralrequest',
            name='responding_therapist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='referrals', to='core.therapist'),
        ),
    ]