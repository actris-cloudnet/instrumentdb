# Instrument database

Application for managing metadata about scientific instruments and creating
persistent identifiers (PIDs) for them according to [PIDINST](https://github.com/rdawg-pidinst/schema).

## Development

Start application:

```sh
docker compose up
```

Create admin user:

```sh
docker compose exec django ./manage.py createsuperuser
```

Log in and create some instruments in <http://localhost:8000/admin>.

Install [pre-commit](https://pre-commit.com/) hooks:

```sh
pre-commit install
```

To make migrations, run tests, etc., use prefix:
```sh
docker compose exec django ./manage.py
```
