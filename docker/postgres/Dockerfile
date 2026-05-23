FROM postgres:18-alpine

RUN apk add --no-cache \
    postgresql-contrib \
    postgresql-plpython3 \
    python3 \
    py3-pip \
    && pip3 install --no-cache-dir \
    psycopg2-binary \
    python-dotenv

COPY pg_hba.conf /usr/share/postgresql/pg_hba.conf.sample
COPY postgresql.conf /usr/share/postgresql/postgresql.conf.sample
COPY init.sql /docker-entrypoint-initdb.d/

RUN chmod 644 /usr/share/postgresql/*.conf.sample

RUN mkdir -p /backups /scripts && chown postgres:postgres /backups /scripts

USER postgres