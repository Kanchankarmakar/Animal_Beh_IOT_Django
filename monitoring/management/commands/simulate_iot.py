
import random
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from monitoring.models import Animal, IoTDevice, SensorReading


# Synthetic values for software testing only.
SENSOR_CONFIG = {
    "activity": {
        "unit": "activity_index",
        "minimum": 0.0,
        "maximum": 100.0,
    },
    "temperature": {
        "unit": "degC",
        "minimum": 36.0,
        "maximum": 40.5,
    },
    "heart_rate": {
        "unit": "bpm",
        "minimum": 40.0,
        "maximum": 120.0,
    },
}


class Command(BaseCommand):
    help = (
        "Generate multiple sensor readings through one integrated "
        "IoT device per animal."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=1,
            help="Number of batches. Use 0 for continuous simulation.",
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=5.0,
            help="Seconds between batches.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        interval = options["interval"]

        if count < 0:
            raise CommandError("--count must be 0 or greater.")

        if interval < 0:
            raise CommandError("--interval cannot be negative.")

        if count == 0 and interval <= 0:
            raise CommandError(
                "Use a positive --interval for continuous simulation."
            )

        if not Animal.objects.exists():
            raise CommandError(
                "No animals found. Register an animal first."
            )

        batch_number = 0

        try:
            while count == 0 or batch_number < count:
                created = self.generate_batch()
                batch_number += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Batch {batch_number}: saved {created} readings."
                    )
                )

                if count == 0 or batch_number < count:
                    time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("\nSimulator stopped.")
            )

    @transaction.atomic
    def generate_batch(self):
        now = timezone.now()
        created_count = 0

        for animal in Animal.objects.all():
            device_id = f"SIM-{animal.pk}-MAIN"

            # One integrated device per animal.
            device, created = IoTDevice.objects.get_or_create(
                device_id=device_id,
                defaults={
                    "animal": animal,
                    "device_type": "other",
                    "is_active": True,
                    "last_seen": now,
                },
            )

            if device.animal_id != animal.pk:
                raise CommandError(
                    f"Device ID conflict for {device_id}."
                )

            if not device.is_active:
                continue

            for sensor_type, config in SENSOR_CONFIG.items():
                value = round(
                    random.uniform(
                        config["minimum"],
                        config["maximum"],
                    ),
                    2,
                )

                SensorReading.objects.create(
                    device=device,
                    sensor_type=sensor_type,
                    value=value,
                    unit=config["unit"],
                    timestamp=now,
                )

                created_count += 1

            device.last_seen = now
            device.save(update_fields=["last_seen"])

        return created_count
