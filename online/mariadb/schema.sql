USE luhze;

CREATE TABLE articles (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	link VARCHAR(255) NOT NULL,
	title VARCHAR(255) NOT NULL,
	author VARCHAR(64) NOT NULL,
	ressort VARCHAR(64) NOT NULL,
	created DATE NOT NULL,
	wordcount INT NOT NULL
);

CREATE TABLE files (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	filename VARCHAR(64) NOT NULL,
	json MEDIUMTEXT NOT NULL
);

DELIMITER $$ 

CREATE PROCEDURE insertOrUpdate (IN new_filename VARCHAR(64), IN new_file MEDIUMTEXT)
BEGIN 
	IF EXISTS(SELECT json FROM files WHERE filename = new_filename) THEN # wenn es die Datei schon gibt
		IF ((SELECT json FROM files WHERE filename = new_filename) != new_file) THEN # wenn es die Datei schon gibt und der inhalt ein andere ist, sonst nichts
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