FROM nginx:1.20.0
ARG APP_ENVIRONMENT
COPY ./src /usr/share/nginx/html
COPY ./nginx.conf.production /etc/nginx/nginx.conf.production
COPY ./nginx.conf.development /etc/nginx/nginx.conf.development
RUN nproc
RUN ulimit -n
WORKDIR /etc/nginx/
RUN echo $APP_ENVIRONMENT
CMD if [ ${APP_ENVIRONMENT} = "development" ] ; \
 then \
     echo 'nginx running in development mode' ; \
     mv nginx.conf.development nginx.conf ; \
     nginx-debug -g "daemon off;" ; \
 else \
     echo 'nginx running in production mode' ; \
     mv nginx.conf.production nginx.conf ; \
     nginx -g "daemon off;" ; \
 fi

