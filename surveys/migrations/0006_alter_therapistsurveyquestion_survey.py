# Generated by Django 4.2.10 on 2024-03-23 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_therapistsurveyquestion_index_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='therapistsurveyquestion',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='surveys.therapistsurvey'),
        ),
    ]