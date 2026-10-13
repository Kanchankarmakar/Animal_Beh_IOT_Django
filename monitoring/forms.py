
from django import forms

from .models import Animal


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            "name",
            "species",
            "breed",
            "age_years",
            "health_status",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter animal name",
            }),
            "species": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Cow, Dog, Goat",
            }),
            "breed": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter breed (optional)",
            }),
            "age_years": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "Age in years",
            }),
            "health_status": forms.Select(
                choices=[
                    ("Unknown", "Unknown"),
                    ("Healthy", "Healthy"),
                    ("Under Observation", "Under Observation"),
                    ("Needs Attention", "Needs Attention"),
                ],
                attrs={"class": "form-select"},
            ),
        }
