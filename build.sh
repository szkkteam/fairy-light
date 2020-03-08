#!/bin/bash

# Constants
FLASK_ENV="prod"

echo "Start building ..."

###################################################
# Build Flask Assets
###################################################
python manage.py --env ${FLASK_ENV} assets build


