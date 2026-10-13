
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from monitoring.models import Animal, IoTDevice, SensorReading


class Command(BaseCommand):
    help = "Consolidate each animal's devices into one integrated device."

    @transaction.atomic
    def handle(self, *args, **options):
        animals = Animal.objects.all()
        consolidated = 0

        for animal in animals:
            main_id = f"SIM-{animal.pk}-MAIN"

            main_device, _ = IoTDevice.objects.get_or_create(
                device_id=main_id,
                defaults={
                    "animal": animal,
                    "device_type": "other",
                    "is_active": True,
                    "last_seen": timezone.now(),
                },
            )

            if main_device.animal_id != animal.pk:
                raise CommandError(
                    f"Device {main_id} belongs to another animal."
                )

            old_devices = IoTDevice.objects.filter(
                animal=animal
            ).exclude(pk=main_device.pk)

            for old_device in old_devices:
                moved = SensorReading.objects.filter(
                    device=old_device
                ).update(device=main_device)

                old_device.is_active = False
                old_device.save(update_fields=["is_active"])

                self.stdout.write(
                    f"Retired {old_device.device_id}; "
                    f"moved {moved} readings."
                )

            main_device.is_active = True
            main_device.last_seen = timezone.now()
            main_device.save(
                update_fields=["is_active", "last_seen"]
            )

            consolidated += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{animal.name}: integrated device {main_id}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Consolidation finished for {consolidated} animals."
            )
        )
