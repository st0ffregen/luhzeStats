FROM python:3.7
COPY . /usr/src/app
RUN pip install -U Flask
RUN pip install mysqlclient
RUN pip install -r /usr/src/app/requirements.txt
CMD python /usr/src/app/app.py
