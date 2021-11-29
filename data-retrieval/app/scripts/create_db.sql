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

DROP TABLE IF EXISTS algo_total CASCADE;
CREATE TABLE algo_total (
    timestamp timestamp, 
    algo TEXT REFERENCES algo (name) ON DELETE CASCADE,  
    total_balance NUMERIC NOT NULL, 
    PRIMARY KEY(timestamp, algo)
);

----------------------------------------------------------------------

DROP PROCEDURE IF EXISTS make_trade;
CREATE OR REPLACE PROCEDURE make_trade(
    tick TIMESTAMP,
    given_algo algo.name%TYPE,
    given_from_asset asset.symbol%TYPE, 
    given_to_asset asset.symbol%TYPE,
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
    total_balance_sum balance.balance%TYPE;

BEGIN
    SELECT COALESCE(balance.balance, 0) INTO old_from_asset_balance FROM balance WHERE balance.algo = given_algo AND balance.asset = given_from_asset ORDER BY balance.timestamp DESC;
    SELECT COALESCE(balance.balance, 0) INTO old_to_asset_balance FROM balance WHERE balance.algo = given_algo AND balance.asset = given_to_asset ORDER BY balance.timestamp DESC;

    SELECT exchange_rate.rate INTO newest_rate FROM exchange_rate WHERE exchange_rate.from_asset = given_from_asset AND exchange_rate.to_asset = given_to_asset ORDER BY exchange_rate.timestamp DESC;
    IF newest_rate IS NULL
    THEN 
        SELECT exchange_rate.rate INTO newest_rate FROM exchange_rate WHERE exchange_rate.from_asset = given_to_asset AND exchange_rate.to_asset = given_from_asset ORDER BY exchange_rate.timestamp DESC;
        newest_rate := 1 / newest_rate;
    END IF;

    INSERT INTO trade (timestamp, algo, from_asset, to_asset, amount)
    VALUES (tick, given_algo, given_from_asset, given_to_asset, amount_bought);

    new_from_asset_balance := ROUND(old_from_asset_balance - amount_bought * newest_rate, 10);
    new_to_asset_balance := ROUND(old_to_asset_balance + amount_bought, 10);

    INSERT INTO balance (timestamp, algo, asset, balance)
    VALUES (tick, given_algo, given_from_asset, new_from_asset_balance);

    INSERT INTO balance (timestamp, algo, asset, balance)
    VALUES (tick, given_algo, given_to_asset, new_to_asset_balance);
END;
$$
LANGUAGE plpgsql;



DROP PROCEDURE IF EXISTS update_price;
CREATE OR REPLACE PROCEDURE update_price(
    tick TIMESTAMP WITH TIME ZONE,
    given_from_asset asset.symbol%TYPE, 
    given_to_asset asset.symbol%TYPE,
    given_rate exchange_rate.rate%TYPE
) 
AS $$
DECLARE
    sum balance.balance%TYPE;
    amount balance.balance%TYPE;
    asset RECORD;
    cur_algo RECORD;
    rate exchange_rate.rate%TYPE;
BEGIN
    INSERT INTO exchange_rate (timestamp, from_asset, to_asset, rate) 
    VALUES (tick, given_from_asset, given_to_asset, given_rate);

    FOR cur_algo IN 
        SELECT name FROM algo
    LOOP
        sum := 0;

        FOR asset IN
            SELECT symbol FROM asset
        LOOP
            SELECT balance.balance INTO amount
            FROM balance
            WHERE balance.asset = asset.symbol AND balance.algo = cur_algo.name AND balance.timestamp <= tick
            ORDER BY balance.timestamp DESC;

            amount := COALESCE(amount, 0);
            CONTINUE WHEN amount = 0;

            IF asset.symbol = 'USD' OR asset.symbol = 'usd'
            THEN
                rate := 1;
            ELSE
                SELECT exchange_rate.rate INTO rate
                FROM exchange_rate
                WHERE exchange_rate.from_asset = as_asset AND exchange_rate.to_asset = asset.symbol AND exchange_rate.timestamp <= tick
                ORDER BY exchange_rate.timestamp DESC;

                IF rate IS NULL
                THEN
                    SELECT exchange_rate.rate INTO rate
                    FROM exchange_rate
                    WHERE exchange_rate.from_asset = asset.symbol AND exchange_rate.to_asset = as_asset AND exchange_rate.timestamp <= tick
                    ORDER BY exchange_rate.timestamp DESC;

                    rate := 1 / rate;
                END IF;
            END IF;

            sum := sum + rate * amount;
        END LOOP;

        INSERT INTO algo_total(timestamp, algo, total_balance)
        VALUES (tick, cur_algo.name, sum);
    END LOOP;
END;
$$
LANGUAGE plpgsql;



DROP PROCEDURE IF EXISTS register_algo;
CREATE OR REPLACE PROCEDURE register_algo(
    algo_name asset.symbol%TYPE, 
    starting_value algo_total.total_balance%TYPE
) 
AS $$
BEGIN
    INSERT INTO algo (name) 
    VALUES (algo_name);

    INSERT INTO algo_total(timestamp, algo, total_balance)
    VALUES (now(), algo_name, starting_value);

    INSERT INTO balance(timestamp, algo, asset, balance)
    VALUES (now(), algo_name, 'USD', starting_value);
END;
$$
LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_total_balance;
/* 

Deprecated. Just going to store the total balance as it changes.

CREATE OR REPLACE FUNCTION get_total_balance(given_algo algo.name%TYPE, as_asset asset.symbol%TYPE, time_window INTERVAL, group_size INTEGER) RETURNS TABLE(res_timestamp TIMESTAMP, res_total_balance NUMERIC) AS $$

DECLARE
    sum balance.balance%TYPE;
    tick TIMESTAMP;
    asset RECORD;
    rate exchange_rate.rate%TYPE;
    amount balance.balance%TYPE;
    first_balance_tick TIMESTAMP;

BEGIN
    SELECT balance.timestamp INTO first_balance_tick FROM balance WHERE balance.algo = given_algo ORDER BY balance.timestamp ASC LIMIT 1;

    FOR tick IN
        SELECT exchange_rate.timestamp FROM exchange_rate WHERE exchange_rate.timestamp > (now() - time_window) AND exchange_rate.timestamp >= first_balance_tick
        UNION
        SELECT trade.timestamp FROM trade WHERE trade.timestamp > (now() - time_window) AND trade.algo = given_algo
        UNION
        SELECT balance.timestamp FROM balance WHERE balance.timestamp > (now() - time_window) AND balance.algo = given_algo
        ORDER BY timestamp ASC
    LOOP
        sum := 0;

        FOR asset IN
            SELECT symbol FROM asset
        LOOP
            SELECT balance.balance INTO amount
            FROM balance
            WHERE balance.asset = asset.symbol AND balance.algo = given_algo AND balance.timestamp <= tick
            ORDER BY balance.timestamp DESC;

            amount := COALESCE(amount, 0);
            CONTINUE WHEN amount = 0;

            IF asset.symbol = as_asset
            THEN
                rate := 1;
            ELSE
                SELECT exchange_rate.rate INTO rate
                FROM exchange_rate
                WHERE exchange_rate.from_asset = as_asset AND exchange_rate.to_asset = asset.symbol AND exchange_rate.timestamp <= tick
                ORDER BY exchange_rate.timestamp DESC;

                IF rate IS NULL
                THEN
                    SELECT exchange_rate.rate INTO rate
                    FROM exchange_rate
                    WHERE exchange_rate.from_asset = asset.symbol AND exchange_rate.to_asset = as_asset AND exchange_rate.timestamp <= tick
                    ORDER BY exchange_rate.timestamp DESC;

                    rate := 1 / rate;
                END IF;
            END IF;

            sum := sum + rate * amount;
            RAISE NOTICE 'Tick:(%), Algo:(%), Asset:(%), Amount:(%), FBT(%), Rate:(%), Sum:(%)', tick, given_algo, asset, amount, first_balance_tick, rate, sum;
        END LOOP;
        
        res_timestamp := tick;
        res_total_balance := sum;

        RETURN NEXT;
    END LOOP;
END;
$$
LANGUAGE plpgsql;
*/