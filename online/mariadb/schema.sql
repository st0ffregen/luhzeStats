CREATE USER IF NOT EXISTS 'api' IDENTIFIED BY 'testApi';
CREATE USER IF NOT EXISTS 'gatherer' IDENTIFIED BY 'testGatherer';
CREATE USER IF NOT EXISTS 'root' IDENTIFIED  BY 'root'; # remove for production
GRANT ALL PRIVILEGES ON luhze.* TO 'root'@'%'; # remove for production


CREATE DATABASE IF NOT EXISTS luhze CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE luhze;


# speichert den letzt analysierten Zustand der DB, d.h. 
# wenn an wordOccurence Änderung vorgenommen wird
# muss das hier eingetragen werden damit dann bei der nächsten Berechnung der Werte 
# nur die neuen Artikel ausgewertet werden müssen und nicht nochmal alle 
# die neuen Artikel werden mit addedDate von documents ermittelt
# muss ein genaus datum mit uhrzeit haben weil mehrfach am tag die artikel neu ausgewertet werden
CREATE TABLE lastmodified (
	lastModifiedWordOccurence DATETIME PRIMARY KEY, # gilt fuer den ersten schritt der analyse wo nur die quarter tabellen befüllt werden
	lastModifiedTotalWordOccurence DATETIME NOT NULL, # hier wird die total tabelle befüllt
	lastModifiedFiles DATETIME NOT NULL, # hier werden die files befüllt
	lastModifiedRanking DATETIME NOT NULL # hier wird das ranking befüllt
);

CREATE TABLE authors (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	firstName VARCHAR(64) NOT NULL,  # es gibt manchmal nur einen namen z.B. hastduzeit -> dann nur nachname aufnehmen
	lastName VARCHAR(64) NOT NULL,
	mostUsedWords VARCHAR(255), # kann weg, brauche eine tabelle pro autor*in
	UNIQUE(firstName, lastName)
);

CREATE TABLE ranking ( # gibs auch als file aber um nur von einer autorin abzufragen, diese tabelle hier
    authorId INT NOT NULL,
    charcount INT NOT NULL,
    daysSinceFirstArticle INT NOT NULL,
    daysSinceLastArticle INT NOT NULL,
    articleCount INT NOT NULL,
    charcountBackInTime INT NOT NULL,
    daysSinceFirstArticleBackInTime INT NOT NULL,
    daysSinceLastArticleBackInTime INT NOT NULL,
    articleCountBackInTime INT NOT NULL,
    backInTime INT NOT NULL, #in months
    FOREIGN KEY (authorId) REFERENCES authors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    PRIMARY KEY (authorId, backInTime)
);

CREATE TABLE files ( #speichert vorbereitete json dateien
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	filename VARCHAR(64) NOT NULL UNIQUE,
	json JSON NOT NULL UNIQUE
);

CREATE TABLE documents ( #speichert den sourcecode der texte
	# braucht addedDate, wann die documents in die tabelle aufgenommen wurden
	# dann kann ich mit dem lastmodified Datum die Artikel bestimmen, die ich noch nicht ausgewertet habe
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	document TEXT NOT NULL,
	charcount INT NOT NULL, #wie viele chars der text hat
	createdDate DATETIME NOT NULL, # das entstehungs datum des artikels, dann kann ich heruasfinden zu welchem quartal das document gehört
	addedDate DATETIME NOT NULL, #datum an den es der db hinzugefügt wurde, ist datetime um es mit lastModified zu vergleichen
	UNIQUE(document)
);

CREATE TABLE articles (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	link VARCHAR(255) NOT NULL,
	title VARCHAR(255) NOT NULL,
	authorId INT NOT NULL,
	ressort VARCHAR(64) NOT NULL,
	created DATETIME NOT NULL,
	documentId INT NOT NULL,
	FOREIGN KEY (authorId) REFERENCES authors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	FOREIGN KEY (documentId) REFERENCES documents(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE wordOccurenceOverTheQuarters ( # einfach alles in eine Tabelle
	word VARCHAR(128) NOT NULL,
	yearAndQuarter INT NOT NULL, #e.g. 20203
	occurencePerWords INT NOT NULL, # durchschnitt, also verhaeltnis aus occurence/100000 Wörter (oder ähnliche Zahl) IN DEM QUARTAL
	occurence INT NOT NULL, # absulute Zahl wie oft das spezifische wort auftaucht IN DEM QUARTAL
	quarterWordCount INT NOT NULL, # totaler worcound, also wie viele wörter es insegesamt auf luhze.de IN DEM QUARTAL gibt, absulute Zahl wie oft das wort auftaucht, ist immer der selbe, wird mitgeschrieben damit bei neuen artikel die occurence neu berechnet werden kann
    PRIMARY KEY (word, yearAndQuarter)
);


CREATE TABLE totalWordOccurence ( # bildet fuer die autocomplete api alle worter mit gesamt werten ab
    word VARCHAR(128) PRIMARY KEY NOT NULL,
    occurencePerWords INT NOT NULL, # durchschnitt, also verhaeltnis aus occurence/100000 Wörter (oder ähnliche Zahl)
    occurence INT NOT NULL, # absulute Zahl wie oft das spezifische wort auftaucht
    totalWordCount INT NOT NULL # totaler worcound, also wie viele wörter es insegesamt auf luhze.de

);



#grant privileges
GRANT SELECT ON luhze.files TO 'api'@'%'; #nicht sicher wie sicher hier diese wildcard ist
GRANT SELECT ON luhze.authors TO 'api'@'%';
GRANT SELECT ON luhze.totalWordOccurence TO 'api'@'%';
GRANT SELECT ON luhze.wordOccurenceOverTheQuarters TO 'api'@'%';
GRANT SELECT ON luhze.lastmodified TO 'api'@'%';
GRANT SELECT ON luhze.ranking TO 'api'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.authors TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.documents TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.files TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.articles TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.lastmodified TO 'gatherer'@'%';
GRANT INSERT, UPDATE, SELECT ON luhze.totalWordOccurence TO 'gatherer'@'%';
GRANT INSERT, UPDATE, SELECT ON luhze.wordOccurenceOverTheQuarters TO 'gatherer'@'%';
GRANT INSERT, UPDATE, SELECT ON luhze.ranking TO 'gatherer'@'%';


# insert start date to lastmodified 
INSERT INTO lastmodified (lastModifiedWordOccurence, lastModifiedTotalWordOccurence, lastModifiedFiles, lastModifiedRanking) VALUES ('1900-01-01 00:00:00','1900-01-01 00:00:00','1900-01-01 00:00:00','1900-01-01 00:00:00');
