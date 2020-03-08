#!/bin/bash

# Constants
FLASK_ENV="dev"

echo "Start building ..."

###################################################
# Build Flask Assets
###################################################
python manage.py --env ${FLASK_ENV} assets build

###################################################
# Build Flask S3
###################################################
python manage.py --env ${FLASK_ENV} s3 upload

