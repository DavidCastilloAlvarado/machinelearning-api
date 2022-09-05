# Machine Learning API

ML API is a probe of concept about how to deploy a simple ml model on cloud.

License: MIT

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

_______________

#### Build Docker compose

```
sudo docker-compose -f local.yml build
```

#### Up Docker compose

```
sudo docker-compose -f local.yml up
```

#### Create superuser

```
sudo docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

#### Run test

```
sudo docker-compose -f local.yml run --rm django pytest
```

#### Makemigrations db changes

```
sudo docker-compose -f local.yml run --rm django python manage.py makemigrations
```

#### Migrate db changes

```
sudo docker-compose -f local.yml run --rm django python manage.py migrate
```

#### Before commit please use pre-commit to check your code. [Link_docs](https://pre-commit.com/#install)

```
pre-commit run --all-files
```

## Recomendation

-------------

### Create a Sentry account

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

### Integrate Github with cloudbuild

To increase productivity please integrate the github with cloudbuild in google cloud platform ecosistem. [see more on GCP docs](https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github)

## Deployment

________________

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

## Deployment on GCP

### Integrate Redis to the project

1. Create an Redis instance on GCP ::

   ```bash
   gcloud redis instances create ml-api-rediscache --region us-central1
   ```

1. Create an VPC connector (serverless vpc access) for cloudrun, using the same region that redis instance ::

   ```bash
   gcloud compute networks vpc-access connectors \
   create mlapiconnectorvpc \
   --network default \
   --region us-central1 \
   --range 10.8.0.0/28
   ```

1. Create a bucket on GCP
1. Create a cloudbuild trigger on GCP
