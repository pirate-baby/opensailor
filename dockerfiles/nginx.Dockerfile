FROM nginx:1.25
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}
COPY ./nginx/${ENVIRONMENT}.conf /etc/nginx/nginx.conf
COPY ./static /usr/share/nginx/static