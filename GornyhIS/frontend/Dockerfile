FROM nginx:alpine

# Удаляем дефолтную страницу nginx
RUN rm /usr/share/nginx/html/*

# Копируем наш интерфейс в папку сервера
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
