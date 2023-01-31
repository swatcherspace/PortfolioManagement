"""
Author: Ratnam, Abhi
Purpose: Starts fastAPI server
Modified Date: 31st Jan 2023 
"""
import sys
import uvicorn

if __name__ == "__main__":
    prod_ip = ""
    dev_ip = ""

    if len(sys.argv) > 1:
        """ Starts app on port 8000 when have the predefined arguments """
        if "prod" in sys.argv:
            uvicorn.run("routes.api:app", host=prod_ip, port=8000, reload=False)
        elif "dev" in sys.argv:
            uvicorn.run("routes.api:app", host=dev_ip, port=8000, reload=True)
        elif "localhost" in sys.argv:
            uvicorn.run("routes.api:app", host="localhost", port=8000, reload=True)
    else:
        print("please mention running environment [localhost, prod, dev].")
