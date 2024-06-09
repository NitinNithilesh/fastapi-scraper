import uvicorn

# Starts the app server
if __name__ == '__main__':
    uvicorn.run('routers.scraper:app')