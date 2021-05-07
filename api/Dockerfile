FROM python:3.7
COPY . /usr/src/api
RUN pip install -U Flask
RUN pip install mysqlclient
RUN pip install -r /usr/src/api/requirements.txt
CMD python /usr/src/api/run.py
