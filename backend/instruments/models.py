from email.mime import image

from django.db import models


class Type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Variable(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=255)
    ror_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=255)
    manufacturers = models.ManyToManyField(Organization)

    def __str__(self) -> str:
        return self.name


class Instrument(models.Model):
    name = models.CharField(
        max_length=255, help_text="Name by which the instrument instance is known."
    )
    owners = models.ManyToManyField(Organization)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    description = models.TextField(
        blank=True,
        help_text="Technical description of the device and its capabilities.",
    )
    commission_date = models.DateField(null=True, blank=True)
    decommission_date = models.DateField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    types = models.ManyToManyField(
        Type, help_text="Classification of the type of the instrument.", blank=True
    )
    variables = models.ManyToManyField(
        Variable,
        help_text="The variable(s) that this instrument measures or observes.",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class RelatedIdentifier(models.Model):
    IDENTIFIER_TYPE_CHOICES = [
        ("ARK", "ARK"),
        ("arXiv", "arXiv"),
        ("bibcode", "bibcode"),
        ("DOI", "DOI"),
        ("EAN13", "EAN13"),
        ("EISSN", "EISSN"),
        ("Handle", "Handle"),
        ("IGSN", "IGSN"),
        ("ISBN", "ISBN"),
        ("ISSN", "ISSN"),
        ("ISTC", "ISTC"),
        ("LISSN", "LISSN"),
        ("PMID", "PMID"),
        ("PURL", "PURL"),
        ("RAiD", "RAiD"),
        ("RRID", "RRID"),
        ("UPC", "UPC"),
        ("URL", "URL"),
        ("URN", "URN"),
        ("w3id", "w3id"),
    ]
    RELATION_TYPE_CHOICES = [
        ("IsDescribedBy", "Described by"),
        ("IsNewVersionOf", "New version of"),
        ("IsPreviousVersionOf", "Previous version of"),
        ("HasComponent", "Has component"),
        ("IsComponentOf", "Component of"),
        ("References", "References"),
        ("HasMetadata", "Has metadata"),
        ("WasUsedIn", "Was used in"),
        ("IsIdenticalTo", "Identical to"),
        ("IsAttachedTo", "Attached to"),
    ]
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="related_identifiers"
    )
    identifier = models.CharField(max_length=255)
    identifier_type = models.CharField(max_length=7, choices=IDENTIFIER_TYPE_CHOICES)
    relation_type = models.CharField(max_length=19, choices=RELATION_TYPE_CHOICES)


class AlternateIdentifier(models.Model):
    IDENTIFIER_TYPE_CHOICES = (
        ("SerialNumber", "Serial number"),
        ("InventoryNumber", "Inventory number"),
        ("Other", "Other"),
    )
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="alternate_identifiers"
    )
    identifier = models.CharField(max_length=255)
    identifier_type = models.CharField(max_length=15, choices=IDENTIFIER_TYPE_CHOICES)
