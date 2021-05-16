DROP TABLE IF EXISTS asset CASCADE;
CREATE TABLE asset(
    symbol TEXT,
    source TEXT NOT NULL,
    PRIMARY KEY (symbol)
);

DROP TABLE IF EXISTS algo CASCADE;
CREATE TABLE algo(
    name TEXT NOT NULL,
    PRIMARY KEY (name)
);

DROP TABLE IF EXISTS trades_on CASCADE;
CREATE TABLE trades_on(
    algo TEXT REFERENCES algo (name) ON DELETE CASCADE,
    asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE,
    PRIMARY KEY (algo, asset)
);

DROP TABLE IF EXISTS exchange_rate CASCADE;
CREATE TABLE exchange_rate (
    timestamp TIMESTAMP, 
    from_asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE, 
    rate NUMERIC NOT NULL, 
    PRIMARY KEY (timestamp, from_asset, to_asset)
);

DROP TABLE IF EXISTS trade CASCADE;
CREATE TABLE trade (
    timestamp timestamp, 
    algo TEXT REFERENCES algo (name) ON DELETE CASCADE, 
    from_asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE, 
    amount NUMERIC NOT NULL, 
    PRIMARY KEY(timestamp, algo, from_asset, to_asset)
);

DROP TABLE IF EXISTS balance CASCADE;
CREATE TABLE balance (
    timestamp timestamp, 
    algo TEXT REFERENCES algo (name) ON DELETE CASCADE,  
    asset TEXT REFERENCES asset (symbol) ON DELETE CASCADE,  
    balance NUMERIC NOT NULL, 
    PRIMARY KEY(timestamp, algo, asset)
);

----------------------------------------------------------------------


CREATE OR REPLACE PROCEDURE make_trade(
    tick TIMESTAMP,
    algo algo.name%TYPE,
    from_asset asset.symbol%TYPE, 
    to_asset asset.symbol%TYPE,
    amount_bought balance.balance%TYPE
) 
AS $$
DECLARE
    old_from_asset_balance balance.balance%TYPE;
    old_to_asset_balance balance.balance%TYPE;
    new_from_asset_balance balance.balance%TYPE;
    new_to_asset_balance balance.balance%TYPE;
    change_in_from_asset balance.balance%TYPE;
    newest_rate exchange_rate.rate%TYPE;

BEGIN
    SELECT COALESCE(balance.balance, 0) INTO old_from_asset_balance FROM balance WHERE balance.algo = algo AND balance.asset = from_asset ORDER BY balance.timestamp DESC;
    SELECT COALESCE(balance.balance, 0) INTO old_to_asset_balance FROM balance WHERE balance.algo = algo AND balance.asset = to_asset ORDER BY balance.timestamp DESC;

    SELECT exchange_rate.rate INTO newest_rate FROM exchange_rate WHERE exchange_rate.from_asset = from_asset AND exchange_rate.to_asset = to_asset ORDER BY exchange_rate.timestamp DESC;
    IF newest_rate IS NULL
    THEN 
        SELECT exchange_rate.rate INTO newest_rate FROM exchange_rate WHERE exchange_rate.from_asset = to_asset AND exchange_rate.to_asset = from_asset ORDER BY exchange_rate.timestamp DESC;
        newest_rate := 1 / newest_rate;
    END IF;

    INSERT INTO trade (tick, algo, from_asset, to_asset, amount)
    VALUES (tick, algo, from_asset, to_asset, amount);

    new_from_asset_balance := old_from_asset_balance - amount_bought * rate;
    new_to_asset_balance := old_to_asset_balance + amount_bought;

    INSERT INTO balance (timestamp, algo, asset, balance)
    VALUES (tick, algo, from_asset, new_from_asset_balance);

    INSERT INTO balance (timestamp, algo, asset, balance)
    VALUES (tick, algo, to_asset, new_to_asset_balance);

    COMMIT;
END;
$$
LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_total_balance(algo algo.name%TYPE, as_asset asset.symbol%TYPE) RETURNS TABLE(res_timestamp TIMESTAMP, res_total_balance NUMERIC) AS $$

DECLARE
    raw_asset balance.balance%TYPE;
    sum balance.balance%TYPE;
    tick TIMESTAMP;
    asset RECORD;
    rate exchange_rate.rate%TYPE;
    amount balance.balance%TYPE;

BEGIN
    FOR tick IN
        SELECT exchange_rate.timestamp FROM exchange_rate
        UNION
        SELECT trade.timestamp FROM trade
        UNION
        SELECT balance.timestamp FROM balance 
    LOOP
        sum := 0;

        FOR asset IN
            SELECT symbol FROM asset
        LOOP
            SELECT COALESCE(balance.balance, 0) INTO amount
            FROM balance
            WHERE balance.asset = asset.symbol AND balance.algo = algo AND balance.timestamp < tick
            ORDER BY balance.timestamp DESC;

            IF asset == as_asset
            THEN
                rate := 1;
            ELSE
                SELECT exchange_rate.rate INTO rate
                FROM exchange_rate
                WHERE exchange_rate.from_asset = as_asset AND exchange_rate.to_asset = asset.symbol AND exchange_rate.timestamp < tick
                ORDER BY exchange_rate.timestamp DESC;

                IF rate IS NULL
                THEN
                    SELECT exchange_rate.rate INTO rate
                    FROM exchange_rate
                    WHERE exchange_rate.from_asset = asset.symbol AND exchange_rate.to_asset = as_asset AND exchange_rate.timestamp < tick
                    ORDER BY exchange_rate.timestamp DESC;

                    rate := 1 / rate;
                END IF;
            END IF;

            sum := sum + rate * amount;
        END LOOP;
        
        res_timestamp := tick;
        res_total_balance := sum;

        RETURN NEXT;
    END LOOP;
END;
$$
LANGUAGE plpgsql;