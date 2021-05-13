FROM mariadb:10.5
#ARG MYSQL_USER
#ARG MYSQL_PASSWORD
#ARG MYSQL_ROOT_PASSWORD
#RUN echo ${MYSQL_API_USER}
#RUN echo ${MYSQL_API_PASSWORD}
#RUN echo ${MYSQL_ROOT_PASSWORD}

COPY schema.sql /docker-entrypoint-initdb.d/schema.sql

#RUN echo "CREATE USER IF NOT EXISTS 'api' IDENTIFIED BY 'testApi';" | cat - /docker-entrypoint-initdb.d/schema.sql > temp && mv temp /docker-entrypoint-initdb.d/schema.sql
#RUN echo "CREATE USER IF NOT EXISTS 'scraper' IDENTIFIED BY 'testScraper';" | cat - /docker-entrypoint-initdb.d/schema.sql > temp && mv temp /docker-entrypoint-initdb.d/schema.sql

