from django.test import Client, TestCase

from .models import Instrument, Model, Organization


class SimpleTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        company = Organization.objects.create(name="Test company")
        model = Model.objects.create(name="Test model")
        model.manufacturers.add(company)
        model.save()
        Instrument.objects.create(
            uuid="d8b717b8-16e7-476a-9f5e-95b2a93ddff6",
            name="Test instrument",
            model=model,
        )

    def setUp(self):
        self.client = Client()

    def test_redirect_html(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.html")
        self.assertRedirects(
            response,
            "/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6.html",
            status_code=301,
        )

    def test_redirect_xml(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.xml")
        self.assertRedirects(
            response,
            "/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6.xml",
            status_code=301,
        )

    def test_redirect_json(self):
        response = self.client.get("/instrument/D8B717B816E7476A9F5E95B2A93DDFF6.json")
        self.assertRedirects(
            response,
            "/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6.json",
            status_code=301,
        )
