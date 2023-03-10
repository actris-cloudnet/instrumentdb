# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["ComponentsTest::test_child_json 1"] = {
    "Identifier": {
        "identifierType": "Handle",
        "identifierValue": "https://hdl.handle.net/21.12132/3.a13475b35ed34ea3",
    },
    "InstrumentType": [
        {
            "instrumentType": {
                "instrumentTypeIdentifier": {
                    "instrumentTypeIdentifierType": "URL",
                    "instrumentTypeIdentifierValue": "http://vocab.test/temperaturesensor",
                },
                "instrumentTypeName": "Temperature sensor",
            }
        }
    ],
    "LandingPage": "http://localhost:8000/instrument/a13475b3-5ed3-4ea3-ba81-0eaa884f11ab",
    "Manufacturers": [{"manufacturer": {"manufacturerName": "ACME"}}],
    "Model": {"modelName": "ACME T1"},
    "Name": "New temperature sensor",
    "Owners": [{"owner": {"ownerName": "My institute"}}],
    "RelatedIdentifiers": [
        {
            "relatedIdentifier": {
                "relatedIdentifierType": "Handle",
                "relatedIdentifierValue": "https://hdl.handle.net/21.12132/3.9084595731eb4900",
                "relationType": "IsComponentOf",
            }
        }
    ],
    "SchemaVersion": "1.0",
}

snapshots[
    "ComponentsTest::test_child_xml 1"
] = """<instrument>
  <identifier identifierType="Handle">https://hdl.handle.net/21.12132/3.a13475b35ed34ea3</identifier>
  <schemaVersion>1.0</schemaVersion>
  <landingPage>http://localhost:8000/instrument/a13475b3-5ed3-4ea3-ba81-0eaa884f11ab</landingPage>
  <name>New temperature sensor</name>
  <owners>
    <owner>
      <ownerName>My institute</ownerName>
    </owner>
  </owners>
  <manufacturers>
    <manufacturer>
      <manufacturerName>ACME</manufacturerName>
    </manufacturer>
  </manufacturers>
  <model>
    <modelName>ACME T1</modelName>
  </model>
  <instrumentTypes>
    <instrumentType>
      <instrumentTypeName>Temperature sensor</instrumentTypeName>
      <instrumentTypeIdentifier instrumentTypeIdentifierType="URL">http://vocab.test/temperaturesensor</instrumentTypeIdentifier>
    </instrumentType>
  </instrumentTypes>
  <relatedIdentifiers>
    <relatedIdentifier relatedIdentifierType="Handle" relationType="IsComponentOf">
          https://hdl.handle.net/21.12132/3.9084595731eb4900
        </relatedIdentifier>
  </relatedIdentifiers>
</instrument>"""

snapshots["ComponentsTest::test_parent_json 1"] = {
    "Identifier": {
        "identifierType": "Handle",
        "identifierValue": "https://hdl.handle.net/21.12132/3.9084595731eb4900",
    },
    "InstrumentType": [
        {
            "instrumentType": {
                "instrumentTypeIdentifier": {
                    "instrumentTypeIdentifierType": "URL",
                    "instrumentTypeIdentifierValue": "http://vocab.test/weatherstation",
                },
                "instrumentTypeName": "Weather station type",
            }
        }
    ],
    "LandingPage": "http://localhost:8000/instrument/90845957-31eb-4900-89a5-78696ec0453d",
    "Manufacturers": [{"manufacturer": {"manufacturerName": "My institute"}}],
    "Name": "My weather station",
    "Owners": [{"owner": {"ownerName": "My institute"}}],
    "RelatedIdentifiers": [
        {
            "relatedIdentifier": {
                "relatedIdentifierType": "Handle",
                "relatedIdentifierValue": "https://hdl.handle.net/21.12132/3.a13475b35ed34ea3",
                "relationType": "HasComponent",
            }
        },
        {
            "relatedIdentifier": {
                "relatedIdentifierType": "Handle",
                "relatedIdentifierValue": "https://hdl.handle.net/21.12132/3.eab72e886cb44902",
                "relationType": "HasComponent",
            }
        },
    ],
    "SchemaVersion": "1.0",
}

snapshots[
    "ComponentsTest::test_parent_xml 1"
] = """<instrument>
  <identifier identifierType="Handle">https://hdl.handle.net/21.12132/3.9084595731eb4900</identifier>
  <schemaVersion>1.0</schemaVersion>
  <landingPage>http://localhost:8000/instrument/90845957-31eb-4900-89a5-78696ec0453d</landingPage>
  <name>My weather station</name>
  <owners>
    <owner>
      <ownerName>My institute</ownerName>
    </owner>
  </owners>
  <manufacturers>
    <manufacturer>
      <manufacturerName>My institute</manufacturerName>
    </manufacturer>
  </manufacturers>
  <instrumentTypes>
    <instrumentType>
      <instrumentTypeName>Weather station type</instrumentTypeName>
      <instrumentTypeIdentifier instrumentTypeIdentifierType="URL">http://vocab.test/weatherstation</instrumentTypeIdentifier>
    </instrumentType>
  </instrumentTypes>
  <relatedIdentifiers>
    <relatedIdentifier relatedIdentifierType="Handle" relationType="HasComponent">
          https://hdl.handle.net/21.12132/3.a13475b35ed34ea3
        </relatedIdentifier>
    <relatedIdentifier relatedIdentifierType="Handle" relationType="HasComponent">
          https://hdl.handle.net/21.12132/3.eab72e886cb44902
        </relatedIdentifier>
  </relatedIdentifiers>
</instrument>"""

snapshots["SimpleTest::test_create_or_update_pid 1"] = {
    "data": [
        {"type": "21.T11148/f5e68cc7718a6af2a96c", "value": '"1.0"'},
        {
            "type": "21.T11148/9a15a4735d4bda329d80",
            "value": '"http://localhost:8000/instrument/8fd884df-6896-4bae-a72f-b6260b5b8744"',
        },
        {"type": "21.T11148/709a23220f2c3d64d1e1", "value": '"Test instrument"'},
        {
            "type": "21.T11148/4eaec4bc0f1df68ab2a7",
            "value": '[{"owner": {"ownerName": "Test owner"}}]',
        },
        {
            "type": "21.T11148/1f3e82ddf0697a497432",
            "value": '[{"manufacturer": {"manufacturerName": "Test manufacturer"}}]',
        },
        {
            "type": "21.T11148/c1a0ec5ad347427f25d6",
            "value": '{"modelName": "Test model", "modelIdentifier": {"modelIdentifierValue": "http://vocab.test/testmodel", "modelIdentifierType": "URL"}}',
        },
        {
            "type": "21.T11148/f76ad9d0324302fc47dd",
            "value": '[{"instrumentType": {"instrumentTypeName": "Test type", "instrumentTypeIdentifier": {"instrumentTypeIdentifierValue": "http://vocab.test/testtype", "instrumentTypeIdentifierType": "URL"}}}]',
        },
        {
            "type": "21.T11148/72928b84e060d491ee41",
            "value": '[{"measuredVariable": {"variableMeasured": "Test variable"}}]',
        },
        {
            "type": "21.T11148/22c62082a4d2d9ae2602",
            "value": '[{"date": {"date": "2002-03-18", "dateType": "Commissioned"}}, {"date": {"date": "2011-01-05", "dateType": "DeCommissioned"}}]',
        },
        {
            "type": "21.T11148/eb3c713572f681e6c4c3",
            "value": '[{"alternateIdentifier": {"alternateIdentifierValue": "836514404680691", "alternateIdentifierType": "SerialNumber"}}]',
        },
    ],
    "type": "instrument",
    "url": "http://localhost:8000/instrument/8fd884df-6896-4bae-a72f-b6260b5b8744",
    "uuid": "8fd884df-6896-4bae-a72f-b6260b5b8744",
}

snapshots["SimpleTest::test_json 1"] = {
    "AlternateIdentifiers": [
        {
            "alternateIdentifier": {
                "alternateIdentifierType": "SerialNumber",
                "alternateIdentifierValue": "836514404680691",
            }
        }
    ],
    "Dates": [
        {"date": {"date": "2002-03-18", "dateType": "Commissioned"}},
        {"date": {"date": "2011-01-05", "dateType": "DeCommissioned"}},
    ],
    "Identifier": {
        "identifierType": "Handle",
        "identifierValue": "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
    },
    "InstrumentType": [
        {
            "instrumentType": {
                "instrumentTypeIdentifier": {
                    "instrumentTypeIdentifierType": "URL",
                    "instrumentTypeIdentifierValue": "http://vocab.test/testtype",
                },
                "instrumentTypeName": "Test type",
            }
        }
    ],
    "LandingPage": "http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6",
    "Manufacturers": [{"manufacturer": {"manufacturerName": "Test manufacturer"}}],
    "MeasuredVariables": [{"measuredVariable": {"variableMeasured": "Test variable"}}],
    "Model": {
        "modelIdentifier": {
            "modelIdentifierType": "URL",
            "modelIdentifierValue": "http://vocab.test/testmodel",
        },
        "modelName": "Test model",
    },
    "Name": "Test instrument",
    "Owners": [{"owner": {"ownerName": "Test owner"}}],
    "SchemaVersion": "1.0",
}

snapshots["SimpleTest::test_no_format_accept_any 1"] = {
    "AlternateIdentifiers": [
        {
            "alternateIdentifier": {
                "alternateIdentifierType": "SerialNumber",
                "alternateIdentifierValue": "836514404680691",
            }
        }
    ],
    "Dates": [
        {"date": {"date": "2002-03-18", "dateType": "Commissioned"}},
        {"date": {"date": "2011-01-05", "dateType": "DeCommissioned"}},
    ],
    "Identifier": {
        "identifierType": "Handle",
        "identifierValue": "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
    },
    "InstrumentType": [
        {
            "instrumentType": {
                "instrumentTypeIdentifier": {
                    "instrumentTypeIdentifierType": "URL",
                    "instrumentTypeIdentifierValue": "http://vocab.test/testtype",
                },
                "instrumentTypeName": "Test type",
            }
        }
    ],
    "LandingPage": "http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6",
    "Manufacturers": [{"manufacturer": {"manufacturerName": "Test manufacturer"}}],
    "MeasuredVariables": [{"measuredVariable": {"variableMeasured": "Test variable"}}],
    "Model": {
        "modelIdentifier": {
            "modelIdentifierType": "URL",
            "modelIdentifierValue": "http://vocab.test/testmodel",
        },
        "modelName": "Test model",
    },
    "Name": "Test instrument",
    "Owners": [{"owner": {"ownerName": "Test owner"}}],
    "SchemaVersion": "1.0",
}

snapshots["SimpleTest::test_no_format_accept_json 1"] = {
    "AlternateIdentifiers": [
        {
            "alternateIdentifier": {
                "alternateIdentifierType": "SerialNumber",
                "alternateIdentifierValue": "836514404680691",
            }
        }
    ],
    "Dates": [
        {"date": {"date": "2002-03-18", "dateType": "Commissioned"}},
        {"date": {"date": "2011-01-05", "dateType": "DeCommissioned"}},
    ],
    "Identifier": {
        "identifierType": "Handle",
        "identifierValue": "https://hdl.handle.net/21.12132/3.d8b717b816e7476a",
    },
    "InstrumentType": [
        {
            "instrumentType": {
                "instrumentTypeIdentifier": {
                    "instrumentTypeIdentifierType": "URL",
                    "instrumentTypeIdentifierValue": "http://vocab.test/testtype",
                },
                "instrumentTypeName": "Test type",
            }
        }
    ],
    "LandingPage": "http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6",
    "Manufacturers": [{"manufacturer": {"manufacturerName": "Test manufacturer"}}],
    "MeasuredVariables": [{"measuredVariable": {"variableMeasured": "Test variable"}}],
    "Model": {
        "modelIdentifier": {
            "modelIdentifierType": "URL",
            "modelIdentifierValue": "http://vocab.test/testmodel",
        },
        "modelName": "Test model",
    },
    "Name": "Test instrument",
    "Owners": [{"owner": {"ownerName": "Test owner"}}],
    "SchemaVersion": "1.0",
}

snapshots[
    "SimpleTest::test_no_format_accept_xml 1"
] = """<instrument>
  <identifier identifierType="Handle">https://hdl.handle.net/21.12132/3.d8b717b816e7476a</identifier>
  <schemaVersion>1.0</schemaVersion>
  <landingPage>http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6</landingPage>
  <name>Test instrument</name>
  <owners>
    <owner>
      <ownerName>Test owner</ownerName>
    </owner>
  </owners>
  <manufacturers>
    <manufacturer>
      <manufacturerName>Test manufacturer</manufacturerName>
    </manufacturer>
  </manufacturers>
  <model>
    <modelName>Test model</modelName>
    <modelIdentifier modelIdentifierType="URL">http://vocab.test/testmodel</modelIdentifier>
  </model>
  <instrumentTypes>
    <instrumentType>
      <instrumentTypeName>Test type</instrumentTypeName>
      <instrumentTypeIdentifier instrumentTypeIdentifierType="URL">http://vocab.test/testtype</instrumentTypeIdentifier>
    </instrumentType>
  </instrumentTypes>
  <measuredVariables>
    <measuredVariable>Test variable</measuredVariable>
  </measuredVariables>
  <dates>
    <date dateType="Commissioned">2002-03-18</date>
    <date dateType="DeCommissioned">2011-01-05</date>
  </dates>
  <alternateIdentifiers>
    <alternateIdentifier alternateIdentifierType="SerialNumber">
        836514404680691
      </alternateIdentifier>
  </alternateIdentifiers>
</instrument>"""

snapshots[
    "SimpleTest::test_xml 1"
] = """<instrument>
  <identifier identifierType="Handle">https://hdl.handle.net/21.12132/3.d8b717b816e7476a</identifier>
  <schemaVersion>1.0</schemaVersion>
  <landingPage>http://localhost:8000/instrument/d8b717b8-16e7-476a-9f5e-95b2a93ddff6</landingPage>
  <name>Test instrument</name>
  <owners>
    <owner>
      <ownerName>Test owner</ownerName>
    </owner>
  </owners>
  <manufacturers>
    <manufacturer>
      <manufacturerName>Test manufacturer</manufacturerName>
    </manufacturer>
  </manufacturers>
  <model>
    <modelName>Test model</modelName>
    <modelIdentifier modelIdentifierType="URL">http://vocab.test/testmodel</modelIdentifier>
  </model>
  <instrumentTypes>
    <instrumentType>
      <instrumentTypeName>Test type</instrumentTypeName>
      <instrumentTypeIdentifier instrumentTypeIdentifierType="URL">http://vocab.test/testtype</instrumentTypeIdentifier>
    </instrumentType>
  </instrumentTypes>
  <measuredVariables>
    <measuredVariable>Test variable</measuredVariable>
  </measuredVariables>
  <dates>
    <date dateType="Commissioned">2002-03-18</date>
    <date dateType="DeCommissioned">2011-01-05</date>
  </dates>
  <alternateIdentifiers>
    <alternateIdentifier alternateIdentifierType="SerialNumber">
        836514404680691
      </alternateIdentifier>
  </alternateIdentifiers>
</instrument>"""
