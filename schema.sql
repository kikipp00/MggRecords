-- noinspection SqlNoDataSourceInspectionForFile

DROP TABLE IF EXISTS Want;
DROP TABLE IF EXISTS Reading;
DROP TABLE IF EXISTS AlreadyRead;

CREATE TABLE Want(
    PRIMARY KEY (userid, title),
    userid INTEGER NOT NULL,
    title text NOT NULL, -- I think titles have to be unique in mgg
    url text,
    author text[],
    alt_title text[]
);
CREATE TABLE Reading(
    PRIMARY KEY (userid, title),
    userid INTEGER NOT NULL,
    title text NOT NULL,
    url text,
    author text[],
    alt_title text[]
);
CREATE TABLE AlreadyRead(
    PRIMARY KEY (userid, title),
    userid INTEGER NOT NULL,
    title text NOT NULL,
    url text,
    author text[],
    alt_title text[]
);