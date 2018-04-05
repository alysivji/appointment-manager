# Appointment Manager

This project will expose an API that users can use to createe, delete, and modify appointments.

## Migration Commands, need to wire into `Makefile`

* `make shell` to connect to web app container
  * `flask db init` creates new migration repository
  * `flask db migrate -m "message"` generates migration script   * `flask db upgrade` runs migrations
  * `flask db downgrade` rolls back migration
