# Generated by Django 3.2 on 2024-04-21 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_ptzcamerapreset_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='weather_station',
            field=models.JSONField(blank=True, null=True),
        ),
    ]