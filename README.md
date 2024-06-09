# FastAPI Web Scraper

Scrape products from website using FastAPI

### Requirments

```
Python version > 3.6.0
```

### Installation

You can install all the requirements by running

```
pip install -r requirements.txt
```

You can also install them manually using

```
pip install uvicorn
pip install requests-html
pip install fastapi_cache
```

### Start Server

You can start the uvicorn server by running

```
python main.py
```

### APIs

##### Scrape Products

```
curl --location 'http://localhost:8000/scraper/products' \
--header 'x_auth_token: eFHY2xPK11ULGlSJ8vzyLjkHLSPm1ORtl9d141AUDaQqWmQ5Crx9DFBXufDVwARc' \
--header 'Content-Type: application/json' \
--data '{
    "pages": 1
}'
```

##### Get Products

```
curl --location 'http://localhost:8000/scraper/products' \
--header 'x_auth_token: eFHY2xPK11ULGlSJ8vzyLjkHLSPm1ORtl9d141AUDaQqWmQ5Crx9DFBXufDVwARc'
```
