# Generated by Django 5.2.1 on 2025-06-19 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice_engine', '0005_remove_detectedemotion_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detectedemotion',
            name='photos',
            field=models.ImageField(upload_to='backoffice_engine/user_upload_photo/temp'),
        ),
    ]
