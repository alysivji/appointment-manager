# Appointment Manager

This project will expose an API that users can use to createe, delete, and modify appointments.

## Setup Instructions

Requires Docker, Docker-Compose, Make.

1. Clone repo
1. `make build`
1. `make up`

App is live at `http://localhost:5000`

**API Endpoints**

```console
* GET, POST http://localhost:5000/v1/appointments
* GET, PATCH, DELETE http://localhost:5000/v1/appointments/:appointment_id

* GET, POST http://localhost:5000/v1/patients
* GET, DELETE http://localhost:5000/v1/patients/:patient_id

* GET, POST http://localhost:5000/v1/providers
* GET, DELETE http://localhost:5000/v1/providers/:provider_id
```

Todo: Create /v1/webhooks endpoint to programmatically create endpoint. For now, we need to manually do it via `make flask_shell`

## API Documentation

Todo: Add swagger documentation.

## Notes

### Think About

When sending back appointment information, we need to think about if we want to send back id or person's name. Then can look up the id based on the info they have.

### Assumptions

* All datetimes are UTC
* closed interval on appointment start, open interval on appointment end
* Another way to check overlap would be to have the union of doctor's schedule and opening times, and see if there is an overlap
  * maybe an is_available_function would be a good refactor

### Tests

* `make test` to run
* test coverage:

```text
----------- coverage: platform linux, python 3.6.5-final-0 -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/__init__.py                          17      0   100%
app/config.py                            11      0   100%
app/models.py                            35      3    91%
app/resources/__init__.py                 0      0   100%
app/resources/appointment.py            118     17    86%
app/resources/patient.py                 31      6    81%
app/resources/provider.py                31      6    81%
app/routes.py                            18      3    83%
app/schemas.py                           11      0   100%
app/utils.py                             28      0   100%
tests/__init__.py                         0      0   100%
tests/conftest.py                        21      0   100%
tests/models_test.py                     70      0   100%
tests/resources/__init__.py               0      0   100%
tests/resources/appointment_test.py     118      0   100%
---------------------------------------------------------
TOTAL                                   509     35    93%
```

### Continuous Integration

* Hooked this up to a [drone](https://drone.io) instance running on my VPS
* PRs have CI integration. [Example](https://github.com/alysivji/appointment-manager/pull/1)

### Makefile Commands

```text
Makefile for managing web application

Usage:
 make build            build images
 make up               creates containers and starts service
 make start            starts service containers
 make stop             stops service containers
 make down             stops service and removes containers

 make migration        create migrations m=migration msg
 make migrate          run migrations
 make migrate_back     rollback migrations
 make test             run tests
 make test_cov         run tests with coverage.py
 make test_fast        run tests without migrations
 make lint             run flake8 linter

 make attach           attach to process inside service
 make logs             see container logs
 make shell            connect to app container in new bash shell
 make flask_shell      connect to app container in ipython shell
 make dbshell          connect to postgres inside db container
```
