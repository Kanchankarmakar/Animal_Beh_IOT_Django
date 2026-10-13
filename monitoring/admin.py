from django.contrib import admin
from .models import Animal, IoTDevice, SensorReading


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "species",
        "breed",
        "health_status",
    )
    search_fields = ("name", "species", "breed")


@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "animal",
        "device_type",
        "is_active",
    )
    list_filter = ("device_type", "is_active")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "sensor_type",
        "value",
        "unit",
        "timestamp",
    )
    list_filter = ("sensor_type",)
    date_hierarchy = "timestamp"