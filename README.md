# Fairy-Light photography
A server-side rendered simple web application which consist a landing page and an online shop for digital products
## Table of contents
- [Features](#features)
- [Flask Backend](#flask-backend)
- [Template rendering](#template-rendering)
- [Local Development](#local-development-quickstart)
- [License](#license)

## Features
- Localized frontend
- Server-side rendering with HTML templates
- User session management with redis
- Payment provider with [Stripe](https://stripe.com)
- Online shop for digital products

Demo can be found here: [Demo](https://fairy-light-staging.herokuapp.com/index)

## Flask Backend 
- [SQLAlchemy](http://docs.sqlalchemy.org/en/rel_1_1/) ORM with [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.2/) and migrations provided by [Flask-Alembic](https://flask-alembic.readthedocs.io/en/stable/)
- RESTful APIs provided by a customized integration between [Flask-RESTful](http://flask-restful.readthedocs.io/en/latest/) and [Flask-Marshmallow](http://flask-marshmallow.readthedocs.io/en/latest/)
- [Flask-Security](https://flask-security.readthedocs.io/en/latest/) provides authentication, authorization, registration and change/forgot password functionality
   - User session management via [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
   - User permissions and roles via [Flask-Principal](https://pythonhosted.org/Flask-Principal/)
   - Secrets encryption via [passlib](https://passlib.readthedocs.io/en/stable/) and [itsdangerous](https://pythonhosted.org/itsdangerous/)
   - CSRF protection via [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/)
- [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/) integrated for painless model CRUD administration
- [Flask-Session](http://pythonhosted.org/Flask-Session/) for server-side sessions
- [Celery](http://www.celeryproject.org/) for asynchronous tasks, such as sending emails via [Flask-Mail](https://pythonhosted.org/Flask-Mail/)

The backend is structured using the [Application Factory Pattern](http://flask.pocoo.org/docs/0.12/patterns/appfactories/), in conjunction with a little bit of declarative configuration in `backend/config.py` (for ordered registration of extensions, and auto-detection of views, models, serializers, model admins and cli commands). The entry point is the `create_app()` method in `backend/app.py` (`wsgi.py` in production).

## Template rendering
The frontend is written in HTML/CSS/Javascript with [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating engine. 

## Local Development QuickStart

### Running locally

This assumes you're on a reasonably standard \*nix system. Windows *might* work if you know what you're doing, but you're on your own there.

Dependencies:

- Python 3.6+
- Your virtualenv tool of choice (strongly recommended)
- PostgreSQL or MariaDB (MySQL)
- Redis (used for sessions persistence and the Celery tasks queue)
- node.js & npm (v6 or later recommended, only required for development)
- MailHog (not required, but it's awesome for testing email related tasks)

```bash
# install
$ git clone git@github.com:szkkteam/fairy-light.git
$ cd flask-react-spa
$ mkvirtualenv -p /path/to/python3 flask_react_spa
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt  # for tests and sphinx docs

# configure
$ edit `backend/config.example.py` and save as `backend/config.py`
$ edit `frontend/app/config.example.js` and save as `frontend/app/config.js`

# set up database
$ sudo -u postgres -i psql
postgres=# CREATE USER flask_api WITH PASSWORD 'flask_api';
postgres=# CREATE DATABASE flask_api;
postgres=# GRANT ALL PRIVILEGES ON DATABASE flask_api TO flask_api;
postgres=# \q  # (quit)

# run db migrations
$ python manage.py db upgrade

# load db fixtures (optional)
$ python manage.py db fixtures fixtures.json

# frontend dev server:
$ npm install
$ npm run start

# backend dev server:
$ python manage.py run

# backend celery workers:
$ python manage.py celery worker
$ python manage.py celery beat
```

## License

MIT
