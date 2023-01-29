# Generated by Django 4.1.3 on 2023-01-29 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
            name='Sensor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('device', models.CharField(default='sensor', max_length=20)),
                ('sensor_type', models.CharField(choices=[('Temperature', 'Temperature'), ('Humidity', 'Humidity')], default='Temperature', max_length=30)),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.tower')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('headline', models.CharField(max_length=200)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('detail', models.TextField()),
                ('severity', models.CharField(choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], default='Low', max_length=30)),
                ('datetime', models.DateTimeField()),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.tower')),
            ],
        ),
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('device', models.CharField(default='camera', max_length=20)),
                ('image', models.ImageField(upload_to='images/')),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.tower')),
            ],
        ),
    ]
