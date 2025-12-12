FROM postgres:16

RUN apt-get update && apt-get install -y locales \
  && sed -i 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
  && locale-gen

ENV LANG=ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=ru_RU.UTF-8"

COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/
