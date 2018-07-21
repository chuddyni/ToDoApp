-- todo/schema.sql

-- tabela z zadaniami
DROP TABLE IF EXISTS zadania;
CREATE TABLE zadania (
    id integer primary key autoincrement, -- unikalny indentyfikator
    user text not null, -- user
    zadanie text not null, -- opis zadania do wykonania
    zrobione boolean not null, -- informacja czy zadania zostalo juz wykonane
    data_pub datetime not null -- data dodania zadania
);

-- pierwsze dane
INSERT INTO zadania (id, user, zadanie, zrobione, data_pub)
VALUES (null,'chuddyni', 'Wyrzucić śmieci', 0, datetime(current_timestamp));
INSERT into zadania (id, user, zadanie, zrobione, data_pub)
VALUES (null,'admin', 'Nakarmić psa', 0, datetime(current_timestamp));