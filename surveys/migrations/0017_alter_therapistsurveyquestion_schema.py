# Generated by Django 4.2.10 on 2024-03-25 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0016_alter_therapistsurveyquestionresponse_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='therapistsurveyquestion',
            name='schema',
            field=models.JSONField(blank=True, default=1),
            preserve_default=False,
        ),
    ]