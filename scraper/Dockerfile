FROM python:3.7
COPY . /usr/src/scraper
RUN python -m pip install --upgrade pip
RUN pip install -r /usr/src/scraper/requirements.txt
CMD python /usr/src/scraper/scraper.py
