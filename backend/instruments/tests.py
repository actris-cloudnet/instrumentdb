import datetime
import doctest
import json
from pathlib import Path
from unittest.mock import Mock, patch

import requests
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
        cls.instrument = Instrument.objects.create(
            uuid=cls.uuid,
            pid="https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
            name="Test instrument",
            model=model,
            commission_date=datetime.date(2002, 3, 18),
            decommission_date=datetime.date(2011, 1, 5),
            serial_number="836514404680691",
        )
        cls.instrument.owners.add(company)

    def setUp(self):
        self.client = Client()

    def test_create_pid(self):
        with patch("instruments.models.requests.post") as mock_post:
            response = requests.models.Response()
            response.status_code = 200
            response._content = (
                b'{"pid":"https://hdl.handle.net/21.12132/3.8fd884df68964bae"}'
            )
            mock_post.return_value = response

            self.instrument.uuid = "8fd884df-6896-4bae-a72f-b6260b5b8744"
            self.instrument.pid = None
            self.instrument.create_pid()
            self.assertEquals(
                self.instrument.pid,
                "https://hdl.handle.net/21.12132/3.8fd884df68964bae",
            )

            with open("instruments/test_data/pid-service.json") as f:
                expected_json = json.load(f)
            mock_post.assert_called_once_with(
                "http://pid-service.test", json=expected_json
            )

    def _test_html_response(self, response):
        response_decoded = response.content.decode("utf-8")
        self.assertEquals(response.status_code, 200)
        test_strings = (
            "Test instrument",
            "PID",
            "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
            "Owners",
            "Manufacturers",
            "Test company",
            "Model name",
            "Test model",
            "Instrument types",
            "Test type",
            "Measured variables",
            "Test variable",
            "Commission date",
            '<time datetime="2002-03-18">March 18, 2002</time>',
            "Decommission date",
            '<time datetime="2011-01-05">Jan. 5, 2011</time>',
            "Serial number",
            "836514404680691",
            "Edit",
            "JSON",
            "XML",
        )
        for test_string in test_strings:
            self.assertInHTML(test_string, response_decoded)

    def _test_xml_response(self, response):
        self.assertEquals(response.status_code, 200)
        expected_xml = Path("instruments/test_data/response.xml").read_text()
        self.assertXMLEqual(response.content.decode("utf-8"), expected_xml)

    def _test_json_response(self, response):
        self.assertEquals(response.status_code, 200)
        expected_json = {
            "Identifier": {
                "identifierValue": "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
                "identifierType": "Handle",
            },
            "LandingPage": "http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6",
            "Name": "Test instrument",
            "Owners": [{"owner": {"ownerName": "Test company"}}],
            "Manufacturers": [{"manufacturer": {"manufacturerName": "Test company"}}],
            "Model": {"modelName": "Test model"},
            "InstrumentType": ["Test type"],
            "MeasuredVariables": [
                {"measuredVariable": {"variableMeasured": "Test variable"}}
            ],
            "Dates": [
                {"date": {"date": "2002-03-18", "dateType": "Commissioned"}},
                {"date": {"date": "2011-01-05", "dateType": "DeCommissioned"}},
            ],
            "AlternateIdentifiers": [
                {
                    "alternateIdentifier": {
                        "alternateIdentifierValue": "836514404680691",
                        "alternateIdentifierType": "SerialNumber",
                    }
                }
            ],
        }
        self.assertJSONEqual(response.content, expected_json)

    def test_html(self):
        response = self.client.get(f"{self.endpoint}.html")
        self._test_html_response(response)

    def test_xml(self):
        response = self.client.get(f"{self.endpoint}.xml")
        self._test_xml_response(response)

    def test_json(self):
        response = self.client.get(f"{self.endpoint}.json")
        self._test_json_response(response)

    def test_no_format_no_accept(self):
        response = self.client.get(f"/instrument/{self.uuid}", HTTP_ACCEPT="")
        self.assertEquals(response.status_code, 406)

    def test_no_format_accept_any(self):
        response = self.client.get(f"/instrument/{self.uuid}", HTTP_ACCEPT="*/*")
        self._test_json_response(response)  # Arbitrarily JSON

    def test_no_format_accept_json(self):
        response = self.client.get(
            f"/instrument/{self.uuid}", HTTP_ACCEPT="application/json"
        )
        self._test_json_response(response)

    def test_no_format_accept_xml(self):
        response = self.client.get(
            f"/instrument/{self.uuid}", HTTP_ACCEPT="application/xml"
        )
        self._test_xml_response(response)

    def test_no_format_accept_html(self):
        response = self.client.get(f"/instrument/{self.uuid}", HTTP_ACCEPT="text/html")
        self._test_html_response(response)

    def test_no_format_accept_unknown_format(self):
        response = self.client.get(f"/instrument/{self.uuid}", HTTP_ACCEPT="image/png")
        self.assertEquals(response.status_code, 406)

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
