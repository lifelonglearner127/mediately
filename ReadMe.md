## mediately

### Local Setting
- clone the repository
- make `.env` file and input credentials. you can see `.env.example` file in root repository
- create virtualenv and install all packages
- export DJANGO_READ_DOT_ENV_FILE=True and run `python manage.py runserver` command


### What You need to review
I started the project from `cookiecutter` boilerplate code.
So you only need to have a look at [`mediately/tools`](https://github.com/lifelonglearner127/mediately/tree/master/mediately/tools) app.


### Local configuration
> Please refer to this [link](https://www.postgresql.org/download/) to install Postgresql

- Configure postgresql:

    ```
    sudo su postgres
    psql
    CREATE DATABASE mediately;
    CREATE USER mediately WITH PASSWORD 'mediately';
    GRANT ALL PRIVILEGES ON DATABASE "mediately" to mediately;
    ```

- Setting up .env

    ```
    DATABASE_URL=postgres://mediately:mediately@localhost:5432/mediately
    CELERY_BROKER_URL=redis://localhost:6379
    LOKALISE_API_TOKEN=<YOUR LOKALISE_API_TOKEN>
    LOKALISE_PROJECT_ID=<YOUR LOKALISE PROJECT>
    GITHUB_TOKEN=eb76ec8bd4513fa940095e92bca16f1524caa5e9
    ```
- Install project & create user
    ```
    virutalenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    export DJANGO_READ_DOT_ENV_FILE=True
    python manager.py createsuperuser
    python manager.py runserver
    ```

- Hit `localhost:8000/` & sign in with superuser credentials
- Hit `http://localhost:8000/tools/specs/` for create tool spec
- Hit `http://localhost:8000/tools/specs/<spec_id>` for update tool spec

> Please check `tools/constants.py` for setting your github parameter.
