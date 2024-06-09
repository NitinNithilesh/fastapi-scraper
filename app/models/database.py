import json
import shutil
import requests
import os

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from models.notification import Notification

notification = Notification()
FastAPICache.init(InMemoryBackend()) # Init's the in memory cache

# All database related operations and processes
class Database():
    def __init__(self):
        # Defines the DB path
        self.db_name = 'products.json'
        self.db_path = 'db/products.json'
        
        # Reads the data from existing DB and stores it in the class        
        database = open(self.db_path)
        self.products_db = json.load(database)
    
    # Searches and retrivies a particular data from the DB which matchs with the product title
    def get_product_from_db(self, product_title: str):
        # In cases where there are no data in DB right now
        if len(self.products_db) == 0:
            return {}
        
        # Loops and finds the product which matches the title
        fetched_product = [product for product in self.products_db if product['product_title'] == product_title]
        if len(fetched_product) > 0:
            return fetched_product[0]

        # Default fallback
        return {}
    
    # Returns if we should clear the existing cache or not
    def should_clear_cache(self, product: dict, product_from_db: dict):
        if 'product_price' in product and 'product_price' in product_from_db:
            if product['product_price'] == product_from_db['product_price']:
                # If there is any change in the price of the product
                return True
        # If the data is same as the existing product in DB
        return False
    
    # Downloads the image from the URL and stores it in local images folder    
    def download_and_save_image(self, product_data: dict):
        try:
            # Makes a request to the image URL to fetch the image response
            image_response = requests.get(product_data['product_image'], stream=True)
            image_response.raise_for_status()
            
            # Generates the filename using the link
            file_name = os.path.basename(product_data['product_image'])
            
            # Path in which the image is going to be stored
            image_path = f"db/images/{file_name}"
            
            # Store the image at the designated path
            with open(image_path, 'wb') as f:
                image_response.raw.decode_content = True
                shutil.copyfileobj(image_response.raw, f)
    
            return image_path
        except:
            # Fallback if we failed to fetch details from the image URL
            notification.notify('GENERAL', {'message': f'Unable to download and save image'})
            return "db/images"
        
    # Clean all the data before storing it in DB
    async def process_data(self, products: list):
        processed_data = []
        for product in products:
            # Change the data type of price to float
            product['product_price'] = float(product['product_price'])
            
            # Finds if the product exists or should we store it again
            product_from_db = self.get_product_from_db(product['product_title'])
            product_exists = self.should_clear_cache(product, product_from_db)
            if not product_exists:
                product['path_to_image'] = self.download_and_save_image(product)
                
                await self.clear_cache()
                processed_data.append(product)                
        
        if len(processed_data) > 0:
            old_products = self.products_db or []
            self.products_db = old_products + processed_data
            notification.notify('STORE_PRODUCTS', {'products_stored_in_db': len(processed_data)})
            
    # Clears the cache stored on the DB data
    async def clear_cache(self):
        await FastAPICache.clear('products_db')
    
    # Fetches all the data from DB and returns it. Before returning, it caches the data
    @cache(namespace='products_db')
    async def get_all_products(self):
        return self.products_db
    
    # Stores the products scraped in the DB
    async def store_products(self, products: dict):
        # Pre process the scraped data
        await self.process_data(products)

        # Stores the data after processing and cleaning the scraped data
        with open('db/products.json', "w") as f:
            json.dump(self.products_db, f, indent=2)
