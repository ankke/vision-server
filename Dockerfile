FROM jjanzic/docker-python3-opencv

ENV APP_NAME=app:app

RUN apt-get update
RUN apt-get -y install dumb-init gcc curl
RUN curl -sL https://taskfile.dev/install.sh | sh
RUN pip install --upgrade pip
RUN pip install pipenv --no-cache-dir
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pipenv install --dev --system
COPY . .

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD gunicorn --bind :5000 --log-level=debug $APP_NAME --reload
EXPOSE 5000
