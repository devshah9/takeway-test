# Generated by Django 4.1.7 on 2023-03-24 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sm_api', '0004_alter_businesshours_end_time_local_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businesshours',
            old_name='end_time_local',
            new_name='end_time_utc',
        ),
        migrations.RenameField(
            model_name='businesshours',
            old_name='start_time_local',
            new_name='start_time_utc',
        ),
    ]
