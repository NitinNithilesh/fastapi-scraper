from fastapi import FastAPI, Request, HTTPException
from models.scraper import Scraper
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
products = Scraper()

AUTH_TOKEN = 'eFHY2xPK11ULGlSJ8vzyLjkHLSPm1ORtl9d141AUDaQqWmQ5Crx9DFBXufDVwARc'

# Options for scrape products post API
class Options(BaseModel):
    pages: int = 1
    proxy_string: str = None

# Verify if the provided token is valid
def verify_access_token(request: Request):
     if ('x_auth_token' not in request.headers) or (request.headers['x_auth_token'] != AUTH_TOKEN):
        raise HTTPException(status_code=401, detail='Invalid auth token')

# Custom middleware which is responsible to validate the token
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            verify_access_token(request)

            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

# Adds the custom middleware
app.add_middleware(CustomMiddleware)

# GET route to fetch all the products stored in the DB
@app.get('/scraper/products')
async def get_products():
    return await products.get_scraped_data()

# POST route to initiate the scraping process with the provided options
@app.post('/scraper/products')
async def scrape_products(options: Options):
    return await products.scrape_data(options.pages, options.proxy_string)
