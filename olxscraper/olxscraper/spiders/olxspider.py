import scrapy


class OlxspiderSpider(scrapy.Spider):
    name = "olxspider"
    allowed_domains = ['www.olx.in']
    start_urls = ['https://www.olx.in/kozhikode_g4058877/for-rent-houses-apartments_c1723']
    
    def parse(self, response):
        # Extracting the property URLs on the page
        property_links = response.css('li a::attr(href)').extract()
        for link in property_links:
            if link:
                full_url = response.urljoin(link)
                yield scrapy.Request(url=full_url, callback=self.parse_property)
        
        # Handling dynamic loading (e.g., load more)
        load_more_button = response.css('button[data-aut-id="btnLoadMore"]::attr(href)').get()
        if load_more_button:
            yield scrapy.Request(url=response.urljoin(load_more_button), callback=self.parse)

    def parse_property(self, response):
        # Extract the necessary details from each property
        yield {
            "property_name": response.css('h1[data-aut-id="itemTitle"]::text').get(),
            "property_id": response.url.split("-iid-")[-1],
            "breadcrumbs": response.css('ol li a::text').extract(),
            "price": {
                "amount": response.css('span[data-aut-id="itemPrice"]::text').re_first(r'\d+'),
                "currency": "₹"
            },
            "image_url": response.css('figure img::attr(src)').get(),
            "description": response.css('div[data-aut-id="itemDescriptionContent"] p::text').get(),
            "seller_name": response.css('span[data-aut-id="profileName"]::text').get(),
            "location": response.css('div[data-aut-id="itemLocation"] span::text').get(),
            "property_type": "Apartments",  # Assuming it's apartments for now
            "bathrooms": response.css('span[data-aut-id="itemBathrooms"]::text').get(),
            "bedrooms": response.css('span[data-aut-id="itemBedrooms"]::text').get()
        }

