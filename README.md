# StockWatcher
Performs Fundamental Analysis On Stocks based on the realtime market data. 

## Create a DB and inside add the below table to get started:-
```

CREATE TABLE stocks (
    id serial PRIMARY KEY,
    name character varying NOT NULL UNIQUE,
    type character varying,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    ltp double precision,
    volume double precision,
    "lowPriceRange" double precision,
    "highPriceRange" double precision,
    time_created timestamp without time zone,
    time_updated timestamp without time zone
);

CREATE TABLE fundamentals (
	id serial PRIMARY KEY,
    name character varying NOT NULL UNIQUE references stocks(name) ON DELETE CASCADE,
    shares_outstanding bigint,
    dividend_rate double precision,
    debt_to_equity double precision,
    book_value_per_share double precision,
    roe double precision,
    current_ratio double precision,
    pe_ratio double precision,
    pb_ratio double precision,
    market_cap double precision,
    earning_per_share double precision,
    industry_pe double precision,
    capped_type varchar(80),
    dividend_yield_percent double precision,
    face_value integer,
    news json,
    time_created timestamp without time zone,
    time_updated timestamp without time zone

);

## To install dependencies
pipenv install -r requirements.txt

## To Activate env
pipenv shell

## Activate env (in case of python env)

source PATH_TO_ENV/bin/activate

Check Server IP address in setup.sh before running on server
## Run setup file
./setup.sh
```

After the installation, depending on the address you've modified, do whatever f** you wanna do with it.

