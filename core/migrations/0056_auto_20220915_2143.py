# Generated by Django 3.2 on 2022-09-15 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_camera_contact_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='idol_4g_interval',
            field=models.FloatField(default=300),
        ),
        migrations.AddField(
            model_name='camera',
            name='pin_4g',
            field=models.IntegerField(default=36),
        ),
    ]
