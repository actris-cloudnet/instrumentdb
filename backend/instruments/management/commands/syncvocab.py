from functools import lru_cache

import requests
from django.core.management.base import BaseCommand
from django.db.models import Q

from instruments.models import Model, Type


class Command(BaseCommand):
    help = "Synchronizes models with vocabulary"

    def _iterate_concepts(self, value):
        if isinstance(value, list):
            return value
        return [value]

    @lru_cache
    def _fetch_graph(self, concept_url: str):
        response = requests.get(concept_url, headers={"accept": "application/json"})
        response.raise_for_status()
        return response.json()["graph"]

    def _does_descend_from(
        self, concept_url: str, ancestor_url: str, max_depth: int = 10
    ):
        if concept_url == ancestor_url:
            return True
        if max_depth == 0:
            return False
        graph = self._fetch_graph(concept_url)
        current_concept = next(item for item in graph if item["uri"] == concept_url)
        if "broader" not in current_concept:
            return False
        broader_concept_urls = [
            item["uri"] for item in self._iterate_concepts(current_concept["broader"])
        ]
        broader_concepts = [
            item for item in graph if item["uri"] in broader_concept_urls
        ]
        for concept in broader_concepts:
            if self._does_descend_from(concept["uri"], ancestor_url, max_depth - 1):
                return True
        return False

    def handle(self, *args, **options):
        count = 0
        for model in Model.objects.filter(concept_url__isnull=False):
            assert model.concept_url is not None
            graph = self._fetch_graph(model.concept_url)
            model_concept = next(
                item for item in graph if item["uri"] == model.concept_url
            )
            type_concept_urls = [
                item["uri"]
                for item in self._iterate_concepts(model_concept["broader"])
                if self._does_descend_from(
                    item["uri"],
                    "https://vocabulary.actris.nilu.no/actris_vocab/instrumenttype",
                )
            ]
            type_concepts = [item for item in graph if item["uri"] in type_concept_urls]

            model.types.clear()
            for type_concept in type_concepts:
                url = type_concept["uri"]
                name = type_concept["prefLabel"]["value"]
                type_obj, created = Type.objects.filter(
                    Q(concept_url=url) | Q(name=name)
                ).get_or_create()
                type_obj.concept_url = url
                type_obj.name = name
                type_obj.save()
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created type {type_obj.name}")
                    )
                model.types.add(type_obj)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Synchronized {count} models"))
