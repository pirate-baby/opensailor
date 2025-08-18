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
build-essential \
curl
WORKDIR /src
RUN uv sync
# Build CSS for production
RUN if [ "$ENVIRONMENT" = "production" ]; then \
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 && \
    chmod +x tailwindcss-linux-x64 && \
    cd app && \
    ../tailwindcss-linux-x64 -i input.css -o ../static/output.css; \
fi
CMD /bin/bash -c "./app_startup/${ENVIRONMENT}.sh"