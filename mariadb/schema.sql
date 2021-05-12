CREATE USER IF NOT EXISTS 'api' IDENTIFIED BY 'testApi';
CREATE USER IF NOT EXISTS 'scraper' IDENTIFIED BY 'testScraper';


CREATE DATABASE IF NOT EXISTS luhze CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE luhze;


CREATE TABLE authors (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	name VARCHAR(128) NOT NULL,
	createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	UNIQUE(name)
);

CREATE TABLE documents (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	document TEXT NOT NULL,
	charCount INT NOT NULL,
	createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	UNIQUE(document)

);

CREATE TABLE articles (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	link VARCHAR(255) NOT NULL,
	title VARCHAR(255) NOT NULL,
	authorId INT NOT NULL,
	ressort VARCHAR(64) NOT NULL,
	publishedDate DATETIME NOT NULL,
	documentId INT NOT NULL,
	createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (authorId) REFERENCES authors(id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (documentId) REFERENCES documents(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE wordOccurrence (
	word VARCHAR(128) NOT NULL,
	year INT NOT NULL,
	quarter INT NOT NULL,
	occurrence INT NOT NULL,
	quarterWordCount INT NOT NULL,
    occurrenceRatio INT NOT NULL, # occurrence/100000 words
	createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (word, year, quarter)
);


#grant privileges

GRANT SELECT ON luhze.authors TO 'api'@'%';#nicht sicher wie sicher hier diese wildcard ist
GRANT SELECT ON luhze.wordOccurrence TO 'api'@'%';
GRANT SELECT ON luhze.articles TO 'api'@'%';
GRANT SELECT ON luhze.documents TO 'api'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.authors TO 'scraper'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.documents TO 'scraper'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.articles TO 'scraper'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.wordOccurrence TO 'scraper'@'%';
CREATE USER IF NOT EXISTS 'root123' IDENTIFIED BY 'root123'; # remove for production
GRANT ALL PRIVILEGES ON luhze.* TO 'root123'@'%'; # remove for production