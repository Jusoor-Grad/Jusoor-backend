# Generated by Django 4.2.10 on 2024-03-11 11:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0002_chatbot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatbot',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bot_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bot_rooms', to='chat.chatbot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chat_rooms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='chat_room',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='messages', to='chat.chatroom'),
            preserve_default=False,
        ),
    ]