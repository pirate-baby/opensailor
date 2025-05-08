FROM postgres:16
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}
COPY ./db_startup/${ENVIRONMENT}-initdb.sh /app/initdb.sh
ENTRYPOINT ["/app/initdb.sh"]