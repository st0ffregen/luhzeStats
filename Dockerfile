FROM php:7.4.7-apache
COPY online/src/ /var/www/html
EXPOSE 80
