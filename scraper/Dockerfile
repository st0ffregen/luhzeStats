FROM python:3.7
COPY . /usr/src/scraper
RUN pip install beautifulsoup4
RUN pip install mysqlclient
RUN pip install pydevd-pycharm~=211.7142.13
RUN pip install -r /usr/src/scraper/requirements.txt
CMD ["python3.7", "/usr/src/scraper/scraper.py"]
