import scrapy


class OlxspiderSpider(scrapy.Spider):
    name = "olxspider"
    allowed_domains = ["www.olx.in"]
    start_urls = ["https://www.olx.in/"]

    def parse(self, response):
        # Extracting all the listings
        listings = response.css('li._1DNjI')

        # Iterating through each listing
        for listing in listings:
            # Extracting the itemTitle
            item_title = listing.css('span[data-aut-id="itemTitle"]::text').get()
    
            # Extracting the itemPrice
            item_price = listing.css('span[data-aut-id="itemPrice"]::text').get()
    
            # Printing the result
            print(f"Title: {item_title}, Price: {item_price}")

