# Generated by Django 4.2.10 on 2024-03-17 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='therapistsurveyquestion',
            old_name='question',
            new_name='description',
        ),
    ]