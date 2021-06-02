CREATE DATABASE IF NOT EXISTS luhze CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
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


GRANT SELECT ON luhze.authors TO 'api'@'%';
GRANT SELECT ON luhze.wordOccurrence TO 'api'@'%';
GRANT SELECT ON luhze.articles TO 'api'@'%';
GRANT SELECT ON luhze.documents TO 'api'@'%';
