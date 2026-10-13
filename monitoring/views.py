
import json
from datetime import timedelta

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from monitoring.forms import AnimalForm
from monitoring.models import Animal, IoTDevice, SensorReading


# Illustrative demo thresholds only; not veterinary guidelines.
DEMO_THRESHOLDS = {
    "activity": (10, 100),
    "temperature": (37, 40),
    "heart_rate": (40, 120),
}


def dashboard(request):
    now = timezone.now()
    today = timezone.localdate()
    recent_cutoff = now - timedelta(hours=24)

    recent_readings = list(
        SensorReading.objects.select_related(
            "device", "device__animal"
        ).order_by("-timestamp")[:100]
    )

    # Find the latest reading for each animal and sensor type.
    latest_by_sensor = {}

    for reading in recent_readings:
        key = (reading.device.animal_id, reading.sensor_type)

        if key not in latest_by_sensor:
            latest_by_sensor[key] = reading

    # Flag latest readings outside the configured demo thresholds.
    alert_items = []

    for reading in latest_by_sensor.values():
        limits = DEMO_THRESHOLDS.get(reading.sensor_type)

        if (
            limits
            and reading.timestamp >= recent_cutoff
            and not (limits[0] <= reading.value <= limits[1])
        ):
            alert_items.append(reading)

    # Prepare chart data.
    chart_data = {}

    for sensor_type in ("activity", "temperature", "heart_rate"):
        readings = list(
            SensorReading.objects.filter(sensor_type=sensor_type)
            .select_related("device", "device__animal")
            .order_by("-timestamp")[:20]
        )

        readings.reverse()

        chart_data[sensor_type] = {
            "labels": [
                timezone.localtime(reading.timestamp).strftime(
                    "%d %b %H:%M:%S"
                )
                for reading in readings
            ],
            "values": [reading.value for reading in readings],
            "animals": [
                reading.device.animal.name for reading in readings
            ],
        }

    context = {
        "total_animals": Animal.objects.count(),
        "active_devices": IoTDevice.objects.filter(
            is_active=True
        ).count(),
        "readings_today": SensorReading.objects.filter(
            timestamp__date=today
        ).count(),
        "behavior_alerts": len(alert_items),
        "alert_items": sorted(
            alert_items,
            key=lambda reading: reading.timestamp,
            reverse=True,
        ),
        "recent_readings": recent_readings[:15],
        "chart_data_json": json.dumps(chart_data),
    }

    return render(request, "monitoring/dashboard.html", context)


# List all registered animals.
def animal_list(request):
    animals = Animal.objects.all().order_by("name")

    return render(
        request,
        "monitoring/animal_list.html",
        {"animals": animals},
    )


# Register a new animal.
def animal_create(request):
    form = AnimalForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Animal registered successfully.")
        return redirect("animal_list")

    return render(
        request,
        "monitoring/animal_form.html",
        {
            "form": form,
            "page_title": "Register Animal",
        },
    )


# Edit an existing animal.
def animal_update(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    form = AnimalForm(request.POST or None, instance=animal)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Animal details updated successfully.")
        return redirect("animal_list")

    return render(
        request,
        "monitoring/animal_form.html",
        {
            "form": form,
            "page_title": "Edit Animal",
            "animal": animal,
        },
    )


# Delete an animal after confirmation.
def animal_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk)

    if request.method == "POST":
        animal.delete()
        messages.success(request, "Animal deleted successfully.")
        return redirect("animal_list")

    return render(
        request,
        "monitoring/animal_confirm_delete.html",
        {"animal": animal},
    )


def device_list(request):
    devices = (
        IoTDevice.objects
        .filter(is_active=True)
        .select_related("animal")
        .order_by("animal__name")
    )

    return render(
        request,
        "monitoring/device_list.html",
        {"devices": devices},
    )


def animal_monitoring(request, pk):
    animal = get_object_or_404(Animal, pk=pk)

    devices = IoTDevice.objects.filter(
        animal=animal,
        is_active=True,
    ).order_by("device_id")

    readings = (
        SensorReading.objects.filter(device__animal=animal)
        .select_related("device")
        .order_by("-timestamp")
    )

    latest_readings = {}

    for reading in readings:
        if reading.sensor_type not in latest_readings:
            latest_readings[reading.sensor_type] = reading

        if len(latest_readings) == 3:
            break

    chart_data = {}

    for sensor_type in ("activity", "temperature", "heart_rate"):
        sensor_readings = list(
            SensorReading.objects.filter(
                device__animal=animal,
                sensor_type=sensor_type,
            )
            .select_related("device")
            .order_by("-timestamp")[:50]
        )

        sensor_readings.reverse()

        chart_data[sensor_type] = {
            "labels": [
                timezone.localtime(r.timestamp).strftime(
                    "%d %b %H:%M:%S"
                )
                for r in sensor_readings
            ],
            "values": [r.value for r in sensor_readings],
        }

    context = {
        "animal": animal,
        "devices": devices,
        "latest_readings": latest_readings.values(),
        "recent_readings": readings[:30],
        "chart_data_json": json.dumps(chart_data),
    }

    return render(
        request,
        "monitoring/animal_monitoring.html",
        context,
    )
