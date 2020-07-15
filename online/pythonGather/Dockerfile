FROM python:3.7-buster
COPY . /usr/src/app
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip install beautifulsoup4
RUN pip install mysqlclient
CMD ["python3.7", "/usr/src/app/gatherer.py"]
