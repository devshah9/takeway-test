# Generated by Django 4.1.7 on 2023-03-31 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sm_api', '0006_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='name',
            field=models.CharField(default='asdf', max_length=20),
            preserve_default=False,
        ),
    ]