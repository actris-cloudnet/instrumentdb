import datetime
import doctest
import xml.etree.ElementTree as ET
from unittest.mock import patch

import requests
from django.test import Client
from snapshottest.django import TestCase

from . import fields
from .models import (
    Campaign,
    Instrument,
    Location,
    Model,
    Organization,
    Person,
    Pi,
    Type,
    Variable,
)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(fields))
    return tests


def _pretty_xml(src: str) -> str:
    element = ET.XML(src)
    ET.indent(element)
    return ET.tostring(element, encoding="unicode")


class SimpleTest(TestCase):

    uuid = "d8b717b8-16e7-476a-9f5e-95b2a93ddff6"
    endpoint = f"/instrument/{uuid}"
    instrument: Instrument

    @classmethod
    def setUpTestData(cls) -> None:
        owner = Organization.objects.create(name="Test owner")
        manufacturer = Organization.objects.create(name="Test manufacturer")
        model = Model.objects.create(
            name="Test model", concept_url="http://vocab.test/testmodel"
        )
        test_type = Type.objects.create(
            name="Test type", concept_url="http://vocab.test/testtype"
        )
        test_variable = Variable.objects.create(
            name="Test variable", concept_url="http://vocab.test/testvariable"
        )
        model.manufacturers.add(manufacturer)
        model.types.add(test_type)
        model.variables.add(test_variable)
        model.save()
        cls.instrument = Instrument.objects.create(
            uuid=cls.uuid,
            pid="https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
            name="Test instrument",
            model=model,
            serial_number="836514404680691",
        )
        cls.instrument.owners.add(owner)
        location1 = Location.objects.create(name="Location 1")
        location2 = Location.objects.create(name="Location 2")
        Campaign.objects.create(
            instrument=cls.instrument,
            location=location1,
            date_range=(datetime.date(2002, 3, 18), datetime.date(2005, 6, 24)),
        )
        Campaign.objects.create(
            instrument=cls.instrument,
            location=location2,
            date_range=(datetime.date(2008, 2, 10), datetime.date(2011, 1, 5)),
        )
        person1 = Person.objects.create(first_name="John", last_name="Doe")
        person2 = Person.objects.create(first_name="Jane", last_name="Doe")
        Pi.objects.create(
            instrument=cls.instrument,
            person=person1,
            date_range=(datetime.date(2002, 3, 18), datetime.date(2005, 6, 24)),
        )
        Pi.objects.create(
            instrument=cls.instrument,
            person=person2,
            date_range=(datetime.date(2008, 2, 10), datetime.date(2011, 1, 5)),
        )

    def setUp(self):
        self.client = Client()

    def test_create_or_update_pid(self):
        with patch("instruments.models.requests.post") as mock_post:
            response = requests.models.Response()
            response.status_code = 200
            response._content = (
                b'{"pid":"https://hdl.handle.net/21.12132/3.8fd884df68964bae"}'
            )
            mock_post.return_value = response

            self.instrument.uuid = "8fd884df-6896-4bae-a72f-b6260b5b8744"
            self.instrument.pid = None
            self.instrument.create_or_update_pid()
            self.assertEqual(
                self.instrument.pid,
                "https://hdl.handle.net/21.12132/3.8fd884df68964bae",
            )

            mock_post.assert_called_once()
            self.assertIn("json", mock_post.call_args.kwargs)
            self.assertMatchSnapshot(mock_post.call_args.kwargs["json"])

    def _test_html_response(self, response):
        response_decoded = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        test_strings = (
            "Test instrument",
            "PID",
            "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
            "Owner",
            "Test owner",
            "Manufacturer",
            "Test manufacturer",
            "Model",
            '<a href="http://vocab.test/testmodel">Test model</a>',
            "Instrument type",
            '<a href="http://vocab.test/testtype">Test type</a>',
            "Measured variable",
            '<a href="http://vocab.test/testvariable">Test variable</a>',
            "Locations",
            '<time datetime="2002-03-18">2002-03-18</time>',
            '<time datetime="2005-06-24">2005-06-24</time>',
            "Location 1",
            '<time datetime="2008-02-10">2008-02-10</time>',
            '<time datetime="2011-01-05">2011-01-05</time>',
            "Location 2",
            "Principal Investigators",
            '<time datetime="2002-03-18">2002-03-18</time>',
            '<time datetime="2005-06-24">2005-06-24</time>',
            "John Doe",
            '<time datetime="2008-02-10">2008-02-10</time>',
            '<time datetime="2011-01-05">2011-01-05</time>',
            "Jane Doe",
            "Serial number",
            "836514404680691",
            "JSON",
            "XML",
        )
        for test_string in test_strings:
            self.assertInHTML(test_string, response_decoded)

    def _test_xml_response(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")
        self.assertMatchSnapshot(_pretty_xml(response.content))

    def _test_json_response(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertMatchSnapshot(response.json())

    def _test_pi_api(self, response):
        expected_json = [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "orcid_id": None,
                "start_date": "2008-02-10",
                "end_date": "2011-01-05",
            },
            {
                "first_name": "John",
                "last_name": "Doe",
                "orcid_id": None,
                "start_date": "2002-03-18",
                "end_date": "2005-06-24",
            },
        ]
        self.assertJSONEqual(response.content, expected_json)

    def _test_pi_api_single(self, response):
        expected_json = [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "orcid_id": None,
                "start_date": "2008-02-10",
                "end_date": "2011-01-05",
            }
        ]
        self.assertJSONEqual(response.content, expected_json)

    def _test_pi_api_single_2(self, response):
        expected_json = []
        self.assertJSONEqual(response.content, expected_json)

    def test_html(self):
        response = self.client.get(f"{self.endpoint}.html")
        self._test_html_response(response)

    def test_pi_api(self):
        response = self.client.get(f"{self.endpoint}/pi")
        self._test_pi_api(response)

    def test_xml(self):
        response = self.client.get(f"{self.endpoint}.xml")
        self._test_xml_response(response)

    def test_json(self):
        response = self.client.get(f"{self.endpoint}.json")
        self._test_json_response(response)

    def test_no_format_no_accept(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="")
        self.assertEqual(response.status_code, 406)

    def test_no_format_accept_any(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="*/*")
        self._test_json_response(response)  # Arbitrarily JSON

    def test_no_format_accept_json(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="application/json")
        self._test_json_response(response)

    def test_no_format_accept_xml(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="application/xml")
        self._test_xml_response(response)

    def test_no_format_accept_html(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="text/html")
        self._test_html_response(response)

    def test_no_format_accept_unknown_format(self):
        response = self.client.get(self.endpoint, HTTP_ACCEPT="image/png")
        self.assertEqual(response.status_code, 406)

    def test_invalid_format(self):
        response = self.client.get(f"{self.endpoint}.asd")
        self.assertEqual(response.status_code, 404)

    def test_redirect_without_format(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6")
        self.assertRedirects(
            response,
            self.endpoint,
            status_code=301,
        )

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

    def test_pi_api_single_date(self):
        response = self.client.get(f"{self.endpoint}/pi?date=2009-01-01")
        self._test_pi_api_single(response)

    def test_pi_api_date_out_of_range(self):
        response = self.client.get(f"{self.endpoint}/pi?date=1990-01-01")
        self._test_pi_api_single_2(response)


class ComponentsTest(TestCase):
    instrument: Instrument
    instrument2: Instrument
    instrument3: Instrument
    instrument4: Instrument

    @classmethod
    def setUpTestData(cls) -> None:
        owner = Organization.objects.create(name="My institute")

        manufacturer = Organization.objects.create(name="ACME")

        model = Model.objects.create(name="ACME T1")
        model.manufacturers.add(manufacturer)
        model.types.add(
            Type.objects.create(
                name="Temperature sensor",
                concept_url="http://vocab.test/temperaturesensor",
            )
        )
        cls.instrument = Instrument.objects.create(
            uuid="b8e85a25-8ad1-42b4-ba86-9fde15013b15",
            pid="https://hdl.handle.net/21.12132/3.b8e85a258ad142b4",
            name="Old temperature sensor",
            model=model,
        )
        cls.instrument.owners.add(owner)

        cls.instrument2 = Instrument.objects.create(
            uuid="a13475b3-5ed3-4ea3-ba81-0eaa884f11ab",
            pid="https://hdl.handle.net/21.12132/3.a13475b35ed34ea3",
            name="New temperature sensor",
            model=model,
        )
        cls.instrument2.owners.add(owner)

        model3 = Model.objects.create(name="ACME H1")
        model3.manufacturers.add(manufacturer)
        model3.types.add(
            Type.objects.create(
                name="Humidity sensor", concept_url="http://vocab.test/humiditysensor"
            )
        )
        cls.instrument3 = Instrument.objects.create(
            uuid="eab72e88-6cb4-4902-ad64-40f3665f949c",
            pid="https://hdl.handle.net/21.12132/3.eab72e886cb44902",
            name="My humidity sensor",
            model=model3,
        )
        cls.instrument3.owners.add(owner)

        cls.instrument4 = Instrument.objects.create(
            uuid="90845957-31eb-4900-89a5-78696ec0453d",
            pid="https://hdl.handle.net/21.12132/3.9084595731eb4900",
            name="My weather station",
        )
        cls.instrument4.owners.add(owner)
        cls.instrument4.components.add(cls.instrument2, cls.instrument3)

    def setUp(self):
        self.client = Client()

    def test_parent_xml(self):
        response = self.client.get(
            "/instrument/90845957-31eb-4900-89a5-78696ec0453d.xml"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")
        self.assertMatchSnapshot(_pretty_xml(response.content))

    def test_child_xml(self):
        self.maxDiff = None
        response = self.client.get(
            "/instrument/a13475b3-5ed3-4ea3-ba81-0eaa884f11ab.xml"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")
        self.assertMatchSnapshot(_pretty_xml(response.content))

    def test_parent_html(self):
        response = self.client.get(
            "/instrument/90845957-31eb-4900-89a5-78696ec0453d.html"
        )
        response_decoded = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        test_strings = (
            "My weather station",
            "Components",
            "New temperature sensor",
            "My humidity sensor",
            "My humidity sensor",
        )
        for test_string in test_strings:
            self.assertInHTML(test_string, response_decoded)

    def test_child_html(self):
        response = self.client.get(
            "/instrument/a13475b3-5ed3-4ea3-ba81-0eaa884f11ab.html"
        )
        response_decoded = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        test_strings = (
            "Component of",
            "My weather station",
        )
        for test_string in test_strings:
            self.assertInHTML(test_string, response_decoded)

    def test_parent_json(self):
        response = self.client.get(
            "/instrument/90845957-31eb-4900-89a5-78696ec0453d.json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertMatchSnapshot(response.json())

    def test_child_json(self):
        response = self.client.get(
            "/instrument/a13475b3-5ed3-4ea3-ba81-0eaa884f11ab.json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertMatchSnapshot(response.json())
