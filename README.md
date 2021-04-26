# luhzeStats
This project delivers the newest statistics from [luhze.de](https://www.luhze.de) to the user. 

# Features
* Scrapes [luhze.de](https://www.luhze.de) every x minutes
* displays various charts that show aggregated information about publications, articles and authors
* includes an inconclusive author ranking with ridiculous, far-fetched influences and weights
* includes an interactive chart that displays the ration of a chosen word compared to 100,000 words for each year since the beginning 

# Building the Project
## Config
In the ```.env``` there are some configurations you can customize. Most importantly you should look up the number of 
overview pages currently available on [luhze.de](https://www.luhze.de). You can find them here https://www.luhze.de/page/{YourNumber}.
Now you can specify the initial value for ```NUMBERS_OF_OVERVIEW_PAGES_TO_SCRAPE_AGAIN```. Later on it's recommended to 
choose a value around 2 to 3.

## Local
For a local environment building the project is as simple as   
```
$ cp .env.example .env  
$ docker-compose up
```

## Production
Copy the ```.env.example``` to ```.env```, change the passwords and stage to production
```
$ docker-compose up
```

# Testing
* there are no tests available yet