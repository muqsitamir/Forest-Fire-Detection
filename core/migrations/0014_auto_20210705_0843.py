# Generated by Django 2.2 on 2021-07-05 08:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_fieldimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='camera',
            old_name='interval',
            new_name='video_interval',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='current_status',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='temperature',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='voltage',
        ),
        migrations.AddField(
            model_name='camera',
            name='update_after',
            field=models.FloatField(default=1800),
        ),
        migrations.AlterField(
            model_name='camera',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='camera',
            name='latitude',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='camera',
            name='longitude',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='camera',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.FloatField(default=0)),
                ('voltage', models.FloatField(default=0)),
                ('status', models.CharField(blank=True, choices=[('ON', 'On'), ('OFF', 'Off')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Camera')),
            ],
        ),
    ]
