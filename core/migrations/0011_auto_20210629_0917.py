# Generated by Django 2.2 on 2021-06-29 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20210629_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='power_off_at',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='slot',
            name='power_on_at',
            field=models.TimeField(),
        ),
    ]
