CREATE OR REPLACE FUNCTION add_product(product INT, amount INT)
RETURNS void AS $$
declare
	new_amount integer;
	old_amount integer;
BEGIN
   SELECT dostepnosc INTO old_amount FROM produkty WHERE id_produktu = product;
   new_amount = amount + old_amount;
   UPDATE produkty SET dostepnosc = new_amount WHERE id_produktu = product;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_new_product(new_name VARCHAR(100), country VARCHAR(100), producent VARCHAR(100), category VARCHAR(100), amount INT, price DOUBLE PRECISION)
RETURNS void AS $$
declare
BEGIN
   INSERT INTO produkty (nazwa_produktu, kraj, producent, kategoria, dostepnosc, cena_za_100g, promocja)
   VALUES(new_name, country, producent, category, amount, price, 0); 
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_to_basket(user_id INT, product_id INT, amount INT, price DOUBLE PRECISION)
RETURNS void AS $$
declare
	availible_amount INT;
	new_amount INT;
	nowa_ilosc INT;
	new_price DOUBLE PRECISION;
	sale INT;
BEGIN
	SELECT dostepnosc INTO availible_amount FROM produkty WHERE product_id = id_produktu;
	IF amount > availible_amount THEN
		RAISE 'OUT OF STOCK';
	END IF;
	
	SELECT promocja INTO sale FROM produkty WHERE product_id = id_produktu;
	new_price = price - 0.01 * sale * price
	
	IF EXISTS (SELECT * FROM koszyki_klientow WHERE id_produktu = product_id AND id_uzytkownika = user_id) THEN
		SELECT ilosc INTO nowa_ilosc FROM koszyki_klientow WHERE id_produktu = product_id AND id_uzytkownika = user_id;
		UPDATE koszyki_klientow SET ilosc = nowa_ilosc + amount WHERE id_produktu = product_id AND id_uzytkownika = user_id;
	ELSE
		new_amount = availible_amount - amount;
		UPDATE produkty SET dostepnosc = new_amount WHERE id_produktu = product_id;
		INSERT INTO koszyki_klientow (id_uzytkownika, id_produktu, ilosc, cena)
		VALUES (user_id, product_id, amount, new_price);
	END IF;
		
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE VIEW user_basket AS
	SELECT id_uzytkownika, ilosc, cena, nazwa_produktu, produkty.id_produktu FROM koszyki_klientow
	JOIN produkty ON koszyki_klientow.id_produktu = produkty.id_produktu;
	
CREATE VIEW coffee AS
	SELECT pr.id_produktu, pr.nazwa_produktu, pr.kraj, pr.kategoria, pr.cena_za_100g, pr.promocja FROM produkty pr
	JOIN kategorie ka ON pr.kategoria = ka.kategoria
	WHERE typ = 'kawa';
	
CREATE VIEW tea AS
	SELECT pr.id_produktu, pr.nazwa_produktu, pr.kraj, pr.kategoria, pr.cena_za_100g, pr.promocja FROM produkty pr
	JOIN kategorie ka ON pr.kategoria = ka.kategoria
	WHERE typ = 'herbata';
	
CREATE VIEW accesories AS
	SELECT pr.id_produktu, pr.nazwa_produktu, pr.kraj, pr.kategoria, pr.cena_za_100g, pr.promocja FROM produkty pr
	JOIN kategorie ka ON pr.kategoria = ka.kategoria
	WHERE typ = 'akcesoria';
	
INSERT INTO skladniki (skladnik) VALUES ('liscie herbaty zielonej');
INSERT INTO skladniki (skladnik) VALUES ('liscie herbaty czarnej');
INSERT INTO skladniki (skladnik) VALUES ('ziarna kawy');
INSERT INTO skladniki (skladnik) VALUES ('cynamon');
INSERT INTO skladniki (skladnik) VALUES ('imbir');
INSERT INTO skladniki (skladnik) VALUES ('egzamin na 5');
INSERT INTO skladniki (skladnik) VALUES ('liscie herbaty');

INSERT INTO sklad_produktow (id_produktu, skladnik) VALUES (1, 'liscie herbaty zielonej');
INSERT INTO sklad_produktow (id_produktu, skladnik) VALUES (1, 'imbir');
INSERT INTO sklad_produktow (id_produktu, skladnik) VALUES (1, 'cynamon');


CREATE OR REPLACE FUNCTION zamow(klient INTEGER, adres INTEGER) RETURNS VOID AS $$

DECLARE identit INTEGER;
DECLARE krotka RECORD;

BEGIN

	INSERT 
		INTO zamowienia(id_uzytkownika, data_zamowienia, id_adresu) 
		VALUES(krotka.id_uzytkownika, CURRENT_DATE, adres) 
		RETURNING id_zamowienia 
		INTO identit;

	FOR krotka IN SELECT * FROM koszyki_klientow WHERE(id_uzytkownika = klient) LOOP

	INSERT
		INTO zamowione_produkty(id_zamowienia, id_produktu, ilosc)
		VALUES(identit, krotka.id_produktu, krotka.ilosc);

	END LOOP;

DELETE FROM koszyki_klientow WHERE(id_uzytkownika = klient);

END;
$$ LANGUAGE 'plpgsql';