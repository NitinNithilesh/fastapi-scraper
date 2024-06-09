# Used to send the notification to the user
class Notification():
    def __init__(self):
        self.message = 'Success'

    # Prepares the notification message based on the type of the notification
    # This can be extended to preparing the payload of the message based on the provided that we use
    def prepare_notification(self, type, options):
        if type == 'SCRAPE_PRODUCTS':
            self.message = f'Products scaped sucessfully.\nTotal products scraped - {options['total_products']}'
        if type == 'STORE_PRODUCTS':
            self.message = f'{options['products_stored_in_db']} products are stored in DB'
        if type == 'GENERAL':
            self.message = options['message']
    
    # Sends out the notification to the user
    def notify(self, type, options):
        self.prepare_notification(type, options)
        print(self.message)
