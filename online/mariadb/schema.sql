CREATE USER IF NOT EXISTS api IDENTIFIED BY 'testApi';
CREATE USER IF NOT EXISTS gatherer IDENTIFIED BY 'testGatherer';


CREATE DATABASE IF NOT EXISTS luhze CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE luhze;

CREATE TABLE articles (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	link VARCHAR(255) NOT NULL,
	title VARCHAR(255) NOT NULL,
	author VARCHAR(64) NOT NULL,
	ressort VARCHAR(64) NOT NULL,
	created DATE NOT NULL,
	wordcount INT NOT NULL,
	sourcecode TEXT NOT NULL,
);

CREATE TABLE files (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	filename VARCHAR(64) NOT NULL,
	json JSON NOT NULL
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
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.files TO 'gatherer'@'%';
GRANT SELECT, DELETE, INSERT, UPDATE ON luhze.articles TO 'gatherer'@'%';
GRANT EXECUTE ON PROCEDURE insertOrUpdate TO 'gatherer'@'%';