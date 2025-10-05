# site/Dockerfile
FROM nginx:1.27-alpine

# наш конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# кладём всю папку site в web-root
WORKDIR /usr/share/nginx/html
COPY . .

EXPOSE 80