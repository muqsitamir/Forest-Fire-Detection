# Generated by Django 3.2 on 2022-11-02 15:01

import core.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_alter_camera_roi_mask'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='file',
            field=models.ImageField(storage=core.storage.OverwriteStorage(), upload_to='events'),
        ),
        migrations.AlterField(
            model_name='event',
            name='thumbnail',
            field=models.ImageField(storage=core.storage.OverwriteStorage(), upload_to='thumbnails'),
        ),
    ]
