import re

import base32_crockford
from django.core.exceptions import ValidationError
from django.db.models import CharField


def generate_check_digit(digits: str) -> str:
    assert len(digits) == 15
    total = 0
    for digit in digits:
        total = (total + int(digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return "X" if result == 10 else str(result)


def parse_orcid_id(value: str) -> str:
    """
    ORCID iD format:
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier

    >>> parse_orcid_id('0000-0002-1825-0097')
    '0000-0002-1825-0097'
    >>> parse_orcid_id('http://orcid.org/0000-0001-5109-3700')
    '0000-0001-5109-3700'
    >>> parse_orcid_id('000000021694233X')
    '0000-0002-1694-233X'
    >>> parse_orcid_id('000000021694233x')
    '0000-0002-1694-233X'
    >>> parse_orcid_id('HTTP://ORCID.ORG/0000-0002-1694-233X')
    '0000-0002-1694-233X'
    >>> parse_orcid_id('https://orcid.org/ 0000-0002-1694-233X')
    '0000-0002-1694-233X'
    >>> parse_orcid_id('2-1694-233X')
    Traceback (most recent call last):
        ...
    django.core.exceptions.ValidationError: ['Invalid structure.']
    >>> parse_orcid_id('0000-0002-1694-2330')
    Traceback (most recent call last):
        ...
    django.core.exceptions.ValidationError: ['Invalid check digit.']
    """
    m = re.fullmatch(
        r"(?:(?:https?://)?(?:www\.)?orcid.org/)?\s*(\d{4})-?(\d{4})-?(\d{4})-?(\d{3})([\dX])",
        value,
        re.I,
    )
    if m is None:
        raise ValidationError("Invalid structure.")
    aaaa, bbbb, cccc, ddd, e = m.groups()
    e = e.upper()
    if generate_check_digit(aaaa + bbbb + cccc + ddd) != e:
        raise ValidationError("Invalid check digit.")
    return f"{aaaa}-{bbbb}-{cccc}-{ddd}{e}"


def parse_ror_id(value: str) -> str:
    """
    ROR ID format:
    https://ror.org/facts/#core-components
    https://github.com/ror-community/ror-api/blob/db3e21233b82ad2df07f7ff6e6b565bf3ec46092/rorapi/management/commands/convertgrid.py#L12

    >>> parse_ror_id('05hppb561')
    '05hppb561'
    >>> parse_ror_id('http://ror.org/05hppb561')
    '05hppb561'
    >>> parse_ror_id('HTTP://ROR.ORG/05HPPB561')
    '05hppb561'
    >>> parse_ror_id('http://ror.org/ 05hppb561')
    '05hppb561'
    >>> parse_ror_id('05hppb500')
    Traceback (most recent call last):
        ...
    django.core.exceptions.ValidationError: ['Invalid checksum.']
    >>> parse_ror_id('5hppb561')
    Traceback (most recent call last):
        ...
    django.core.exceptions.ValidationError: ['Invalid structure.']
    """
    m = re.fullmatch(
        r"(?:(?:https?://)?(?:www\.)?ror.org/)?\s*0(?P<n>.{6})(?P<checksum>.{2})",
        value,
        re.I,
    )
    if m is None:
        raise ValidationError("Invalid structure.")
    n = base32_crockford.decode(m["n"])
    checksum = str(98 - ((n * 100) % 97)).zfill(2)
    if checksum != m["checksum"]:
        raise ValidationError(f"Invalid checksum.")
    return "0" + m["n"].lower() + m["checksum"]


class OrcidIdField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = len("aaaa-bbbb-cccc-ddde")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return value
        return parse_orcid_id(value)

    def formfield(self, **kwargs):
        kwargs["max_length"] = None
        return super().formfield(**kwargs)


class RorIdField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = len("0aaaaaabb")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return value
        return parse_ror_id(value)

    def formfield(self, **kwargs):
        kwargs["max_length"] = None
        return super().formfield(**kwargs)
