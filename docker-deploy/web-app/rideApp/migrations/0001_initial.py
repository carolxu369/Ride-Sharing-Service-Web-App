# Generated by Django 4.1.5 on 2023-02-03 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=128)),
                ('password', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_driver', models.BooleanField(default=False)),
                ('driver_name', models.CharField(blank=True, max_length=128, null=True)),
                ('driver_vehicle', models.CharField(blank=True, max_length=128, null=True)),
                ('driver_plate_num', models.CharField(blank=True, max_length=128, null=True)),
                ('driver_max_passenger', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('driver_special_vehicle_info', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_shared', models.BooleanField()),
                ('arrival_time', models.DateTimeField()),
                ('sharer_earliest_time', models.DateTimeField(null=True)),
                ('sharer_latest_time', models.DateTimeField(null=True)),
                ('dest_addr', models.CharField(max_length=128)),
                ('total_passenger', models.PositiveIntegerField()),
                ('status', models.IntegerField(choices=[(1, 'open'), (2, 'confirmed'), (3, 'complete')], null=True)),
                ('owner_special_request', models.TextField(blank=True, default='', null=True)),
                ('vehicle_type', models.CharField(max_length=128)),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ride_driver', to='rideApp.user')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_owner', to='rideApp.user')),
                ('sharers', models.ManyToManyField(to='rideApp.user')),
            ],
        ),
    ]