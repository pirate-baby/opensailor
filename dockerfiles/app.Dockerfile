FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/src
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}
COPY . /src
# this is for image and file type detection
RUN apt update && apt-get install -y libmagic1 \
# for psycopg2 build - because we are using different architectures, this must be built from source
# instead of psycopg2-binary
libpq-dev \
build-essential
WORKDIR /src
RUN uv sync
# CSS is pre-built and included in static/output.css
CMD /bin/bash -c "./app_startup/${ENVIRONMENT}.sh"