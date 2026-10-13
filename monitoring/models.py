
from django.db import models
from django.core.validators import MinValueValidator


class Animal(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    age_years = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    health_status = models.CharField(
        max_length=30,
        default="Unknown",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.species})"


class IoTDevice(models.Model):
    DEVICE_TYPES = [
        ("accelerometer", "Accelerometer"),
        ("temperature", "Temperature Sensor"),
        ("heart_rate", "Heart Rate Sensor"),
        ("other", "Other"),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_id = models.CharField(
        max_length=100,
        unique=True,
    )
    device_type = models.CharField(
        max_length=30,
        choices=DEVICE_TYPES,
        default="other",
    )
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.device_id


class SensorReading(models.Model):
    device = models.ForeignKey(
        IoTDevice,
        on_delete=models.CASCADE,
        related_name="readings",
    )
    sensor_type = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["device", "timestamp"],
                name="reading_device_time_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device.device_id}: "
            f"{self.sensor_type}={self.value} {self.unit}"
        )
