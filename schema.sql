-- noinspection SqlNoDataSourceInspectionForFile

DROP TABLE IF EXISTS Want;
DROP TABLE IF EXISTS Reading;
DROP TABLE IF EXISTS AlreadyRead;

CREATE TABLE Want(
    title text NOT NULL PRIMARY KEY, -- I think titles have to be unique in mgg
    url text,
    author text,
    alt_title text
);
CREATE TABLE Reading(
    title text NOT NULL PRIMARY KEY,
    url text,
    author text,
    alt_title text
);
CREATE TABLE AlreadyRead(
    title text NOT NULL PRIMARY KEY,
    url text,
    author text,
    alt_title text
);