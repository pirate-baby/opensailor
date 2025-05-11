FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/src
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}
COPY . /src
RUN apt-get update && apt-get install -y libmagic1
WORKDIR /src
RUN uv sync
CMD /bin/bash -c "./app_startup/${ENVIRONMENT}.sh"