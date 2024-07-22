FROM bitnami/spark:latest

USER root

ADD https://jdbc.postgresql.org/download/postgresql-42.6.0.jar /opt/bitnami/spark/jars/postgresql-42.6.0.jar

RUN chmod 644 /opt/bitnami/spark/jars/postgresql-42.6.0.jar

USER 1001