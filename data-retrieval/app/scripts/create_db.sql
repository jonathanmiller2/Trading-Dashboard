DROP TABLE IF EXISTS asset CASCADE;
CREATE TABLE asset(
    asset_symbol TEXT,
    PRIMARY KEY (asset_symbol)
);

DROP TABLE IF EXISTS algo CASCADE;
CREATE TABLE algo(
    algo_id INT GENERATED ALWAYS AS IDENTITY,
    algo_name TEXT NOT NULL,
    PRIMARY KEY (algo_id)
);

DROP TABLE IF EXISTS exchange_rate CASCADE;
CREATE TABLE exchange_rate (
    timestamp TIMESTAMP, 
    from_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    rate NUMERIC NOT NULL, 
    PRIMARY KEY (timestamp, from_asset, to_asset)
);

DROP TABLE IF EXISTS trade CASCADE;
CREATE TABLE trade (
    timestamp timestamp, 
    algo_id INT REFERENCES algo ON DELETE CASCADE, 
    from_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    amount NUMERIC NOT NULL, 
    PRIMARY KEY(timestamp, algo_id, from_asset, to_asset)
);

DROP TABLE IF EXISTS balance CASCADE;
CREATE TABLE balance (
    timestamp timestamp, 
    algo_id INT REFERENCES algo ON DELETE CASCADE,  
    asset_symbol TEXT REFERENCES asset ON DELETE CASCADE,  
    balance NUMERIC NOT NULL, 
    PRIMARY KEY(timestamp, algo_id, asset_symbol)
);

----------------------------------------------------------------------


CREATE OR REPLACE PROCEDURE make_trade(
    tick TIMESTAMP,
    algo_name algo.algo_name%TYPE,
    from_asset asset.asset_symbol%TYPE, 
    to_asset asset.asset_symbol%TYPE,
    rate exchange_rate.rate%TYPE,
    amount_bought balance.balance%TYPE
) 
AS $$
DECLARE
    algo_id algo.algo_id%TYPE;
    old_from_asset_balance balance.balance%TYPE;
    old_to_asset_balance balance.balance%TYPE;
    new_from_asset_balance balance.balance%TYPE;
    new_to_asset_balance balance.balance%TYPE;
    change_in_from_asset balance.balance%TYPE;

BEGIN
    SELECT algo.algo_id INTO algo_id FROM algo WHERE algo.algo_name = algo_name;
    SELECT COALESCE(balance.balance, 0) INTO old_from_asset_balance FROM balance WHERE balance.algo_id = algo_id AND balance.asset_symbol = from_asset ORDER BY balance.timestamp DESC;
    SELECT COALESCE(balance.balance, 0) INTO old_to_asset_balance FROM balance WHERE balance.algo_id = algo_id AND balance.asset_symbol = to_asset ORDER BY balance.timestamp DESC;

    INSERT INTO trade (tick, algo_id, from_asset, to_asset, amount)
    VALUES (tick, algo_id, from_asset, to_asset, amount);

    new_from_asset_balance := old_from_asset_balance - amount_bought * rate;
    new_to_asset_balance := old_to_asset_balance + amount_bought;

    INSERT INTO balance (timestamp, algo_id, asset_symbol, balance)
    VALUES (tick, algo_id, from_asset, new_from_asset_balance);

    INSERT INTO balance (timestamp, algo_id, asset_symbol, balance)
    VALUES (tick, algo_id, to_asset, new_to_asset_balance);

    COMMIT;
END;
$$
LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_total_balance(algo_id algo.algo_id%TYPE, as_asset asset.asset_symbol%TYPE) RETURNS TABLE(res_timestamp TIMESTAMP, res_total_balance NUMERIC) AS $$

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
        SELECT COALESCE(balance.balance, 0) INTO raw_asset
        FROM balance
        WHERE balance.asset_symbol = as_asset AND balance.algo = algo_id AND exchange_rate.timestamp < tick
        ORDER BY balance.timestamp DESC;

        sum := raw_asset;

        FOR asset IN
            SELECT asset_symbol FROM asset
        LOOP
            SELECT COALESCE(balance.balance, 0) INTO amount
            FROM balance
            WHERE balance.asset_symbol = asset.asset_symbol AND balance.algo = algo_id AND balance.timestamp < tick
            ORDER BY balance.timestamp DESC;

            SELECT COALESCE(exchange_rate.rate, 0) INTO rate
            FROM exchange_rate
            WHERE exchange_rate.from_asset = as_asset AND exchange_rate.to_asset = asset.asset_symbol AND exchange_rate.timestamp < tick
            ORDER BY exchange_rate.timestamp DESC;

            IF rate IS NULL
            THEN
                SELECT COALESCE(exchange_rate.rate, 0) INTO rate
                FROM exchange_rate
                WHERE exchange_rate.from_asset = asset.asset_symbol AND exchange_rate.to_asset = as_asset AND exchange_rate.timestamp < tick
                ORDER BY exchange_rate.timestamp DESC;

                rate := 1 / rate;
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
