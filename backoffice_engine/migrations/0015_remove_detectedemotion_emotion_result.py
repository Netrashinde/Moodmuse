# Generated by Django 5.2.1 on 2025-06-27 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice_engine', '0014_detectedemotion_user_song_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectedemotion',
            name='emotion_result',
        ),
    ]
