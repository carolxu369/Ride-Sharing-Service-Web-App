from django.db import models
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)

    # if registered as a driver
    is_driver = models.BooleanField(blank=False, default=False)
    driver_name = models.CharField(max_length=128, null=True, blank=True)
    driver_vehicle = models.CharField(max_length=128, null=True, blank=True)
    driver_plate_num = models.CharField(max_length=128, null=True, blank=True)
    driver_max_passenger = models.PositiveIntegerField(
        default=1, null=True, blank=True)
    driver_special_vehicle_info = models.TextField(
        default='', null=True, blank=True)

    def __str__(self):
        return self.username

class Ride(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='ride_owner')
    driver = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='ride_driver')
    is_shared = models.BooleanField(blank=False)
    sharers = models.ManyToManyField(User)

    # requests
    arrival_time = models.DateTimeField()
    sharer_earliest_time = models.DateTimeField(null=True)
    sharer_latest_time = models.DateTimeField(null=True)
    dest_addr = models.CharField(max_length=128)
    total_passenger = models.PositiveIntegerField(blank=False)

    status_choice = ((1, 'open'), (2, 'confirmed'), (3, 'complete'))
    status = models.IntegerField(choices=status_choice, null=False, default=1)

    owner_special_request = models.TextField(default='', null=True, blank=True)
    vehicle_type = models.CharField(max_length=128, blank=False)
    sharer_num = models.JSONField(null=True)
    owner_passenger = models.PositiveIntegerField(default = 1, blank=False)

    def __str__(self):
        return str(self.id)
