# Generated by Django 4.1.7 on 2023-03-23 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sm_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('store_id', models.IntegerField(primary_key=True, serialize=False)),
                ('timezone_str', models.CharField(default='America/Chicago', max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='storestatus',
            name='status',
            field=models.CharField(max_length=10),
        ),
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField()),
                ('start_time_local', models.TimeField()),
                ('end_time_local', models.TimeField()),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sm_api.store')),
            ],
        ),
        migrations.AlterField(
            model_name='storestatus',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sm_api.store'),
        ),
        migrations.DeleteModel(
            name='StoreSchedule',
        ),
    ]
