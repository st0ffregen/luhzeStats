FROM mariadb:10.5
ARG APP_ENVIRONMENT
ARG MYSQL_API_USER
ARG MYSQL_API_PASSWORD
ARG MYSQL_SCRAPING_USER
ARG MYSQL_SCRAPING_PASSWORD

COPY ./schema.sql /docker-entrypoint-initdb.d/schema.sql

RUN if [[ "$APP_ENVIRONMENT" = "development" ]] ; then \
        echo 'CREATE USER IF NOT EXISTS \'root123\' IDENTIFIED BY \'root123\';\n' >> /docker-entrypoint-initdb.d/schema.sql ; \
        echo "GRANT ALL PRIVILEGES ON luhze.* TO 'root123'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql ; \
    fi

RUN echo 'CREATE USER IF NOT EXISTS \'api\' IDENTIFIED BY \'testApi\';\n' >> /docker-entrypoint-initdb.d/schema.sql
RUN echo 'CREATE USER IF NOT EXISTS \'scraper\' IDENTIFIED BY \'testScraper\'\n;' >> /docker-entrypoint-initdb.d/schema.sql

RUN echo "GRANT SELECT ON luhze.authors TO 'api'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT ON luhze.wordOccurrence TO 'api'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT ON luhze.articles TO 'api'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT ON luhze.documents TO 'api'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.authors TO 'scraper'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.documents TO 'scraper'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.articles TO 'scraper'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
RUN echo "GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.wordOccurrence TO 'scraper'@'%';\n" >> /docker-entrypoint-initdb.d/schema.sql
