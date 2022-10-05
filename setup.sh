node stock-market-india/app.js 3000 &
uvicorn  main:app --reload --port=8000 --workers 4
