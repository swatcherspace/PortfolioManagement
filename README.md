# StockWatcher
Performs Fundamental Analysis On Stocks based on the realtime market data. 

# An extension to the work done by [maanavshah](https://github.com/maanavshah) 
Without his approach to get the NSE and BSE Data for learning/development i was not able to build this over top of it.


## Create a DB and inside add the below table to get started:-
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

## Pull the latest code [stock-market-india](https://github.com/maanavshah/stock-market-india) and place it on StockWatcher/stock-market-india 
## Same level as setup.sh and main.py file
reference is in below image:-

<img width="248" alt="Screenshot 2022-10-05 at 8 46 17 PM" src="https://user-images.githubusercontent.com/24920237/194097374-45e7cf9f-0207-45a8-889c-ebac77520f4e.png">

Now navigate to StockWatcher/stock-market-india/ and do the following below steps:-

Let's get step by step here.

Identify the location for your application.

First identify the location for your application. Let's take it as /home/user/your_app. The path doesn’t matter, so feel free to locate the directory wherever it is best for you.

Installing Node.js

Here is where we will set up Node.js and Express. Node.js is a framework and Express provides a web server. The webserver we need does not need to do anything fancy. The only feature that the webserver needs are the ability to provide static files.

To get started download and install Node.JS: nodejs.org

Install Express

Express is a package that executes within Node.js. To install express, in the Command Prompt navigate to your directory for the application which is /home/user/your_app.

Now let's install Express as a package for Node.js. At the command prompt type “npm install express”. That installed Express and should have created a directory called “node_modules”.

#for detailed info please refer [stock-market-india](https://github.com/maanavshah/stock-market-india)





## To install dependencies
pipenv install -r requirements.txt

## To Activate env
pipenv shell

## To run 
./setup.sh

After the installation, depending on the address you've modified, do whatever f** you wanna do with it.

