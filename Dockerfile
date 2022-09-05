# pull official base image
#FROM python:3.9-slim
ARG PYTHON_VERSION=3.9-slim-bullseye
# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

##### --------------------------------BUILD STAGE-------------------#######
# ------------------------------------------------------------------------------#
# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential \
    # psycopg2 dependencies
    libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
    -r ${BUILD_ENVIRONMENT}.txt

##------------------------------------- RUN STAGE----------------------####
# ------------------------------------------------------------------------------#
# Python 'run' stage
FROM python as python-run-stage
# ARG variable 
ARG ES_CERTIFICATE
ENV ES_CERTIFICATE=$ES_CERTIFICATE
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# set work directory
WORKDIR /usr/src/app

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    # psycopg2 dependencies
    libpq-dev \
    # Translations dependencies
    gettext \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# COPY ./requirements /usr/src/app/requirements
# #COPY ./requirements.txt /usr/src/app/requirements.txt
# RUN pip install -r /usr/src/app/requirements/production.txt
# # COPY ./entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint
# RUN chmod +x /entrypoint
# copy project
# RUN echo -e ${ES_CERTIFICATE} > es_certificate.crt 
#RUN echo -e ${ES_CERTIFICATE} > ./es_certificate.crt
#COPY es_certificate.crt /usr/src/app/es_certificate.crt
COPY . /usr/src/app/
# ENTRYPOINT ["/entrypoint"]

# run development server
#CMD python /usr/src/app/manage.py runserver 0.0.0.0:$PORT

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 0 config.wsgi:application
