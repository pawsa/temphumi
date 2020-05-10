#! /bin/sh

FLASK_ENV=development FLASK_RUN_PORT=${PORT:-5000} \
FLASK_APP=temphumi exec flask run
