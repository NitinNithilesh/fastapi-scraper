from requests_html import HTMLSession
from models.notification import Notification
from models.database import Database

notification = Notification()
database = Database()

return_payload = {}


class Scraper():
    def __init__(self):
        self.product_list = []
        self.item = {}
        self.request = {}
        self.product_counter = 0
    
    # Inits the req session for the page that is going to be scraped
    # Added retry fallback to retry initing the session if failed initially
    def init_session(self, page_number: int = 1, proxy_string: str = None):
        try:
            # Creates a session
            url = f'https://dentalstall.com/shop/page/{page_number}'
            html_session = HTMLSession()

            # Add any proxy string passed
            if proxy_string is not None:
                html_session.proxies = {
                    'http': proxy_string,
                }
                
            # Stores the current session in the requet
            self.request = html_session.get(url)
        except Exception as error:
            # Retrying the session that we were not able to create
            notification.notify('GENERAL', {'message': error})
            notification.notify('GENERAL', {'message': 'Retrying...'})
            self.init_session(page_number, proxy_string)
    
    # Scrapes the product details
    def find_product_details(self):
            return self.request.html.find('div.mf-product-details')

    # Scrapes the image details
    def find_product_image_details(self):
            return self.request.html.find('div.mf-product-thumbnail')

    # Scrapes the product image
    def scrape_product_image(self, image_element: dict):
            if image_element.attrs.get('data-lazy-src'):
                return image_element.attrs.get('data-lazy-src')

    # Scrapes the product images
    def scrape_product_name(self, price_element: dict):
            if price_element.attrs.get('alt'):
                return price_element.attrs.get('alt')

    # Scrapes the product price
    def scrape_product_price(self, product: dict):
            if product.find('span.woocommerce-Price-amount', first=True):
                # Splits and fetchs only the price amomunt
                return product.find('span.woocommerce-Price-amount', first=True).text.split('₹')[1]
            # Fallbacks to price 0 if not present
            return '0'
    
    # Cleans the product details fetched
    def clean_product_data(self, products: list):
            for product in products:
                self.item = {}
                self.item['product_price'] = self.scrape_product_price(product)
                self.product_list.append(self.item)

    # Cleans the product image fetched
    def clean_product_image_data(self, product_images: list):
            for product_image in product_images:
                img_tag = product_image.find('img', first=True)
                self.product_list[self.product_counter]['product_title'] = self.scrape_product_name(img_tag)
                self.product_list[self.product_counter]['product_image'] = self.scrape_product_image(img_tag)
                self.product_counter += 1

    # Fetches all the products stored in DB
    async def get_scraped_data(self):
            return await database.get_all_products()

    # Stores all the scraped products in DB
    async def store_products(self, products: list):
            await database.store_products(products)
    
    # Function that scrapes all the data from the website            
    async def scrape_data(self, pages: int = 1, proxy_string: str = None):
        notification.notify('GENERAL', {'message': f'Scraping products from {pages} pages'})

        # Loop to scrape the number of pages provied in the request
        for i in range(pages):
            # Creates a scraping session with the site and current page
            self.init_session(i + 1, proxy_string)
    
            # Scrapes all the details required from the site            
            products = self.find_product_details()
            product_images = self.find_product_image_details()
    
            # Cleans all the scraped details
            self.clean_product_data(products)
            self.clean_product_image_data(product_images)

            notification.notify('GENERAL', {'message': f'Fetched products from page {i+1}'})
        
        notification.notify('SCRAPE_PRODUCTS', {'total_products': self.product_counter + 1})
        notification.notify('GENERAL', {'message': 'Processing and storing them'})
        # Stores all the scraped and cleaned data in the DB
        await self.store_products(self.product_list)
        
        return_payload['message'] = 'Products scraped successfully'
        return_payload['success'] = True
        
        # Returns the response to the API                
        return return_payload
