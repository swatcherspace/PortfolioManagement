# StockWatcher
Performs Fundamental Analysis On Stocks based on the realtime market data. 

## Create a DB and inside add the below table to get started:-
```
CREATE TABLE employees (
	id serial PRIMARY KEY,
    first_name varchar(80),
    last_name varchar(80),
    company_id integer,
    work_email varchar(80),
    manager_id integer,
    dob  varchar(80),
    employee_number  integer,
    tax_id integer,
    employment_status varchar(80),
    marital_status varchar(80)
);
## To install dependencies
pipenv install -r requirements.txt

## To Activate env
pipenv shell

## To run 
./setup.sh
```

After the installation, depending on the address you've modified, do whatever f** you wanna do with it.

