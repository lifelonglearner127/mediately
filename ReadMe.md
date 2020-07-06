# mediately
- [Local Installation](#local-installation)
    - [Clone & Setting env file](#clone-&-setting-env-file)
    - [Postgresql](#postgresql)
    - [Setting gitub](#setting-github)
    - [Running on local](#running-on-local)
- [Testing](#testing)
- [Q&A](#q&a)

## Local Installation
### Clone & Setting env file
  - Clone the repository
    ```
    git clone https://github.com/lifelonglearner127/mediately.git
    ```

  - Setting an env file

    You need to create a github token in order to use github apis. Make sure pull request permission is allowed while creating a github token. You can create a github token on your developer setting page. You can refer to `.env.example` file. Here is an example of `.env` because some credentials might now work on your side.

    ```
      DATABASE_URL=postgres://mediately:mediately@localhost:5432/mediately
      CELERY_BROKER_URL=redis://localhost:6379
      LOKALISE_API_TOKEN=<YOUR LOKALISE_API_TOKEN>
      LOKALISE_PROJECT_ID=<YOUR LOKALISE PROJECT>
      GITHUB_TOKEN=22b1acbf17da8a3cf674aa3cfe8bbe17308147a7
      NGROK=fb04c2bfb3ff.ngrok.io
    ```

### Postgresql
> Please refer to this [link](https://www.postgresql.org/download/) to install Postgresql

  After installation, run such commands

    ```
    sudo su postgres
    psql
    CREATE DATABASE mediately;
    CREATE USER mediately WITH PASSWORD 'mediately';
    GRANT ALL PRIVILEGES ON DATABASE "mediately" to mediately;
    ```

### Setting github
  - Create a spec repository

    This github repository should contain the tool spec files in root directory like [this](https://github.com/lifelonglearner127/mediately-specs)

  - Create webhook

    - Webhooks can be created on the repository setting page. Make sure that your webhook include the pull request events.
    - Payload url is needed in order for project to work properly. You can use one of the public domain once you run ngrok. It should be something like this. `http://<ngrok public domain>/tools/payload` 

  - Constants

    Please make some changes in `tools/constants.py` file
    ```
    GITHUB_API_DOMAN = "api.github.com"
    GITHUB_REPOSITORY = "mediately-specs"
    GITHUB_USER = "lifelonglearner127"
    ```

### Running on local
> ngrok is needed for webhook. Set webhook payload url to one of ngrok urls.

  ```
  cd mediately
  virutalenv venv
  source venv/bin/activate
  pip install -r requirements.txt
  export DJANGO_READ_DOT_ENV_FILE=True
  python manager.py migrate
  python manager.py createsuperuser
  python manager.py runserver 8000
  ngrok http 8000
  ```

## Testing
- Hit the `localhost:8000` and you can see the table and form for creation.
- You can see [admin page](localhost:8000/admin) and `Tools` is there.
- You can see testcases at [here](https://docs.google.com/spreadsheets/d/16-aEULOSkuA4Eq9MC8CT7CTbnTqjTCUBuNlYOS4dg0o/edit?usp=sharing)

## Q&A
- I started the project from `cookiecutter` boilerplate code. So you only need to have a look at [`mediately/tools`](https://github.com/lifelonglearner127/mediately/tree/master/mediately/tools) app.

> Please check `tools/constants.py` for setting your github parameter.
