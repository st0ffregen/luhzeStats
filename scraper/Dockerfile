FROM python:3.7
COPY . /usr/src/scraper
WORKDIR /usr/src/scraper
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python scraper.py
