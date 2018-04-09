# Appointment Manager

This project will expose an API that users can use to createe, delete, and modify appointments.

## Migration Commands, need to wire into `Makefile`

* `make shell` to connect to web app container
  * `flask db init` creates new migration repository
  * `flask db migrate -m "message"` generates migration script
  * `flask db upgrade` runs migrations
  * `flask db downgrade` rolls back migration

## Think About

When sending back appointment information, we need to think about if we want to send back id or person's name. Then can look up the id based on the info they have.

## Assumptions

* All datetimes are UTC
* closed interval on appointment start, open interval on appointment end
* maybe an is_available_function would be a good refactor

## Notes

* I know there is a lot to clean up, but did not take the time to do so as this is a project to show my knowledge. I can discuss what I would clean up if I had more time and needed to deploy to production
