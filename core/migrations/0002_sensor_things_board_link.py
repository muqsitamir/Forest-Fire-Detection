# Generated by Django 3.2 on 2023-03-16 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='things_board_link',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
