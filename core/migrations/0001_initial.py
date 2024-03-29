# Generated by Django 3.2 on 2023-02-28 09:29

import core.fields
import core.storage
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0003_alter_user_first_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test', models.BooleanField(default=True)),
                ('live', models.BooleanField(default=True)),
                ('should_log', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('roi_mask', models.ImageField(blank=True, null=True, upload_to='roi_masks')),
                ('last_reported_at', models.DateTimeField(blank=True, null=True)),
                ('last_uploaded_at', models.DateTimeField(blank=True, null=True)),
                ('remaining_storage', models.FloatField(default=64)),
                ('frames_per_sec', models.IntegerField(default=1)),
                ('image_width', models.IntegerField(default=640)),
                ('image_height', models.IntegerField(default=480)),
                ('day_threshold', models.FloatField(default=1000)),
                ('night_threshold', models.FloatField(default=1000)),
                ('iou_threshold', models.FloatField(default=80)),
                ('longitude', models.FloatField(blank=True)),
                ('latitude', models.FloatField(blank=True)),
                ('sunset', models.DateTimeField(blank=True, null=True)),
                ('sunrise', models.DateTimeField(blank=True, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=16, null=True)),
                ('infrared', models.IntegerField(default=12)),
                ('pwm', models.IntegerField(default=100)),
                ('filter_a', models.IntegerField(default=16)),
                ('filter_b', models.IntegerField(default=18)),
                ('motion_1', models.IntegerField(default=11)),
                ('motion_2', models.IntegerField(default=13)),
                ('pin_4g', models.IntegerField(default=36)),
                ('rest_interval', models.IntegerField(default=5)),
                ('motion_interval', models.IntegerField(default=2)),
                ('video_interval', models.IntegerField(default=15)),
                ('update_after', models.FloatField(default=300)),
                ('idol_4g_interval', models.FloatField(default=300)),
                ('live_image', core.fields.CustomImageField(blank=True, null=True, storage=core.storage.OverwriteStorage(), unique=True, upload_to='liveimages')),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('file', models.ImageField(storage=core.storage.OverwriteStorage(), upload_to='events')),
                ('thumbnail', models.ImageField(storage=core.storage.OverwriteStorage(), upload_to='thumbnails')),
                ('date', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('FEATURED', 'Featured'), ('ARCHIVED', 'Archived'), ('NONE', 'None')], default='NONE', max_length=20)),
                ('camera', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.camera')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Specie',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('endangered', models.BooleanField(default=False)),
                ('color', models.CharField(default='rgb(75, 192, 192)', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tower',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('power_on_at', models.TimeField()),
                ('power_off_at', models.TimeField()),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.camera')),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('sensor_type', models.CharField(choices=[('Temperature', 'Temperature'), ('Humidity', 'Humidity')], default='Temperature', max_length=30)),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tower')),
            ],
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.FloatField(default=0)),
                ('voltage', models.FloatField(default=0)),
                ('status', models.CharField(blank=True, choices=[('ON', 'On'), ('OFF', 'Off')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.camera')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(choices=[('SMS_FAILED', 'SMS FAILED'), ('ALIVE', 'ALIVE'), ('SCRIPT_STARTED', 'SCRIPT STARTED'), ('CAMERA_ERROR', 'CAMERA ERROR'), ('CHECKED_MOTION', 'CHECKED MOTION'), ('EVENT_CAPTURED', 'EVENT CAPTURED'), ('UPLOAD_SUCCESS', 'UPLOAD SUCCESS'), ('UPLOAD_FAILED', 'UPLOAD FAILED'), ('DETECTOR_FAULT', 'DETECTOR FAULT')], max_length=20)),
                ('script', models.CharField(choices=[('CAPTURE', 'Capture'), ('UPLOAD', 'Upload'), ('OTHERS', 'Others')], max_length=20)),
                ('message', models.CharField(max_length=200)),
                ('logged_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.camera')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', core.fields.CustomImageField(storage=core.storage.OverwriteStorage(), unique=True, upload_to='wwf/%Y-%m-%d')),
                ('date', models.DateTimeField()),
                ('processed', models.BooleanField(default=False)),
                ('included', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.camera')),
                ('event', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.event')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='species',
            field=models.ManyToManyField(blank=True, to='core.Specie'),
        ),
        migrations.CreateModel(
            name='DontCare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.camera')),
            ],
        ),
        migrations.AddField(
            model_name='camera',
            name='tower',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.tower'),
        ),
        migrations.AddField(
            model_name='camera',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BoundingBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.image')),
                ('specie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.specie')),
            ],
        ),
    ]
