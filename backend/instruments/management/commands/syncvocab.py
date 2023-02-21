import requests
from django.core.management.base import BaseCommand

from instruments.models import Model, Type


class Command(BaseCommand):
    help = "Synchronizes models with vocabulary"

    def handle(self, *args, **options):
        count = 0
        for model in Model.objects.filter(concept_url__isnull=False):
            assert model.concept_url is not None
            response = requests.get(
                model.concept_url, headers={"accept": "application/json"}
            )
            response.raise_for_status()
            graph = response.json()["graph"]
            model_concept = next(
                item for item in graph if item["uri"] == model.concept_url
            )
            type_concept = next(
                item for item in graph if item["uri"] == model_concept["broader"]["uri"]
            )

            type_obj, created = Type.objects.get_or_create(
                concept_url=type_concept["uri"]
            )
            type_obj.name = type_concept["prefLabel"]["value"]
            type_obj.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created type {type_obj.name}"))
            model.types.set([type_obj])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Synchronized {count} models"))
