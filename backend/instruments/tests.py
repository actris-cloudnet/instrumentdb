import doctest
from pathlib import Path

from django.test import Client, TestCase

from . import fields
from .models import Instrument, Model, Organization, Type, Variable


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(fields))
    return tests


class SimpleTest(TestCase):

    uuid = "d8b717b8-16e7-476a-9f5e-95b2a93ddff6"
    endpoint = f"/instrument/{uuid}"

    @classmethod
    def setUpTestData(cls) -> None:
        company = Organization.objects.create(name="Test company")
        model = Model.objects.create(name="Test model")
        test_type = Type.objects.create(name="Test type")
        test_variable = Variable.objects.create(name="Test variable")
        model.manufacturers.add(company)
        model.types.add(test_type)
        model.variables.add(test_variable)
        model.save()
        instrument = Instrument.objects.create(
            uuid=cls.uuid, name="Test instrument", model=model
        )
        instrument.owners.add(company)

    def setUp(self):
        self.client = Client()

    def test_html(self):
        response = self.client.get(f"{self.endpoint}.html")
        response_decoded = response.content.decode("utf-8")
        self.assertEquals(response.status_code, 200)
        test_strings = (
            "Test instrument",
            "PID",
            "Owners",
            "Manufacturers",
            "Test company",
            "Model name",
            "Test model",
            "Instrument types",
            "Test type",
            "Measured variables",
            "Test variable",
            "Edit",
            "JSON",
            "XML",
        )
        for test_string in test_strings:
            self.assertInHTML(test_string, response_decoded)

    def test_xml(self):
        response = self.client.get(f"{self.endpoint}.xml")
        self.assertEquals(response.status_code, 200)
        expected_xml = Path("instruments/test_data/response.xml").read_text()
        self.assertXMLEqual(response.content.decode("utf-8"), expected_xml)

    def test_json(self):
        response = self.client.get(f"{self.endpoint}.json")
        self.assertEquals(response.status_code, 200)
        expected_json = {
            "Identifier": {
                "identifierValue": "20.1000/5555",
                "identifierType": "Handle",
            },
            "LandingPage": "http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6.html",
            "Name": "Test instrument",
            "Owners": [{"owner": {"ownerName": "Test company"}}],
            "Manufacturers": [{"manufacturer": {"manufacturerName": "Test company"}}],
            "Model": {"modelName": "Test model"},
            "InstrumentType": ["Test type"],
            "MeasuredVariables": [
                {"measuredVariable": {"variableMeasured": "Test variable"}}
            ],
        }
        self.assertJSONEqual(response.content, expected_json)

    def test_no_format(self):
        response = self.client.get(f"/instrument/{self.uuid}")
        self.assertEquals(response.status_code, 404)

    def test_invalid_format(self):
        response = self.client.get(f"{self.endpoint}.asd")
        self.assertEquals(response.status_code, 404)

    def test_redirect_html(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.html")
        self.assertRedirects(
            response,
            f"{self.endpoint}.html",
            status_code=301,
        )

    def test_redirect_xml(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.xml")
        self.assertRedirects(
            response,
            f"{self.endpoint}.xml",
            status_code=301,
        )

    def test_redirect_json(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.json")
        self.assertRedirects(
            response,
            f"{self.endpoint}.json",
            status_code=301,
        )
