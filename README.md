# StockWatcher

Performs Fundamental Analysis On Stocks based on the realtime market data. 

## Alembic has been used for dealing with migrations
alembic revision --autogenerate -m "First Migration" 

alembic upgrade head 

## To install dependencies
pipenv install -r requirements.txt

## Create a virtual env 
python -m venv venv/ 
source venv/bin/activate 

## To run 
uvicorn  main:app --reload 
```

After the installation, depending on the address you've modified, do whatever f** you wanna do with it.

