CREATE USER IF NOT EXISTS api IDENTIFIED BY 'testApi';
CREATE USER IF NOT EXISTS gatherer IDENTIFIED BY 'testGatherer';


CREATE DATABASE IF NOT EXISTS luhze CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE luhze;

CREATE TABLE authors (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	firstName VARCHAR(64) NOT NULL,
	lastName VARCHAR(64) NOT NULL,
	mostUsedWords VARCHAR(255), # ersatz fuer array, speichert 5 woerter, darf null sein, weil von gatherer nicht befüllt
	UNIQUE(firstName, lastName)
);

CREATE TABLE files (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	filename VARCHAR(64) NOT NULL,
	json JSON NOT NULL,
	UNIQUE(filename, json)
);

CREATE TABLE documents (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	document TEXT NOT NULL,
	wordcount INT NOT NULL,
	UNIQUE(document)
);

CREATE TABLE articles (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	link VARCHAR(255) NOT NULL,
	title VARCHAR(255) NOT NULL,
	authorId INT NOT NULL,
	ressort VARCHAR(64) NOT NULL,
	created DATE NOT NULL,
	documentId INT NOT NULL,
	FOREIGN KEY (authorId) REFERENCES authors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	FOREIGN KEY (documentId) REFERENCES documents(id) ON UPDATE CASCADE ON DELETE RESTRICT
);



DELIMITER $$ 

CREATE PROCEDURE insertOrUpdate (IN new_filename VARCHAR(64), IN new_file JSON)
BEGIN 
	IF EXISTS(SELECT json FROM files WHERE filename = new_filename) THEN # wenn es die Datei schon gibt
		IF ((SELECT json FROM files WHERE filename = new_filename) != new_file) THEN # wenn es die Datei schon gibt und der inhalt ein andere ist, sonst nichts, durch unique klausel ersetzten?
			UPDATE files as f
			SET f.json = new_file
			WHERE f.filename = new_filename;
		END IF;
	ELSE
		INSERT INTO files (id, filename, json)
		VALUES (null, new_filename, new_file);
	END IF;
END; $$
DELIMITER ;

#grant privileges
GRANT SELECT ON luhze.files TO 'api'@'%'; #nicht sicher wie sicher hier diese wildcard ist
GRANT SELECT ON luhze.authors TO 'api'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.authors TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.documents TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.files TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.articles TO 'gatherer'@'%';
GRANT EXECUTE ON PROCEDURE insertOrUpdate TO 'gatherer'@'%';