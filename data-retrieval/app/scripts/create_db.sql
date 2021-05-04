DROP TABLE IF EXISTS asset;
CREATE TABLE asset(
    asset_symbol TEXT,
    PRIMARY KEY (asset_symbol)
);

DROP TABLE IF EXISTS algo;
CREATE TABLE algo(
    algo_id INT GENERATED ALWAYS AS IDENTITY,
    algo_name TEXT,
    PRIMARY KEY (algo_id)
);

DROP TABLE IF EXISTS exchange_rate;
CREATE TABLE exchange_rate (
    timestamp TIMESTAMP, 
    from_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    rate NUMERIC, 
    PRIMARY KEY (timestamp, from_asset, to_asset)
);

DROP TABLE IF EXISTS trade;
CREATE TABLE trade (
    timestamp timestamp, 
    algo_id INT REFERENCES algo ON DELETE CASCADE, 
    from_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    to_asset TEXT REFERENCES asset (asset_symbol) ON DELETE CASCADE, 
    amount NUMERIC, 
    PRIMARY KEY(timestamp, algo_id, from_asset, to_asset)
);

DROP TABLE IF EXISTS balance;
CREATE TABLE balance (
    timestamp timestamp, 
    algo_id INT REFERENCES algo ON DELETE CASCADE,  
    asset_symbol TEXT REFERENCES asset ON DELETE CASCADE,  
    balance NUMERIC, 
    PRIMARY KEY(timestamp, algo_id, asset_symbol)
);

CREATE OR REPLACE FUNCTION get_total_balance(algo_id algo.algo_id%TYPE) RETURNS balance.balance%TYPE AS $$

DECLARE
    raw_usd balance.balance%TYPE;
    sum balance.balance%TYPE := 0;
    asset RECORD;
    rate exchange_rate.rate%TYPE;
    amount balance.balance%TYPE;
    
BEGIN

    SELECT COALESCE(balance.balance, 0) INTO raw_usd
    FROM balance
    WHERE balance.asset_symbol = 'USD' AND balance.algo = algo_id
    ORDER BY balance.timestamp DESC;

    sum := sum + raw_usd;

    FOR asset IN
        SELECT asset_symbol FROM asset
    LOOP
        SELECT COALESCE(exchange_rate.rate, 0) INTO rate
        FROM exchange_rate
        WHERE exchange_rate.from_asset = 'USD' AND exchange_rate.to_asset = asset.asset_symbol
        ORDER BY exchange_rate.timestamp DESC;

        SELECT COALESCE(balance.balance, 0) INTO amount
        FROM balance
        WHERE balance.asset_symbol = asset.asset_symbol AND balance.algo = algo_id
        ORDER BY balance.timestamp DESC;

        sum := sum + rate * amount;
    END LOOP;

    RETURN sum;

END;

$$
LANGUAGE plpgsql;


/*
CREATE OR REPLACE PROCEDURE make_trade(
    timestamp timestamp,
    algo text,
    symbol text, 
    
)
language plpgsql    
as $$
begin
    -- subtracting the amount from the sender's account 
    update accounts 
    set balance = balance - amount 
    where id = sender;

    -- adding the amount to the receiver's account
    update accounts 
    set balance = balance + amount 
    where id = receiver;

    commit;
end;
$$
*/