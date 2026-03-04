FROM nginx:alpine

COPY docs/index.html /usr/share/nginx/html/index.html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -q --spider http://127.0.0.1:80/ || exit 1

EXPOSE 80
