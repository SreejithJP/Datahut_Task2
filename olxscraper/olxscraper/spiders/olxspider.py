import scrapy

class OlxspiderSpider(scrapy.Spider):
    name = "olxspider"
    allowed_domains = ['www.olx.in']
    start_urls = ['https://www.olx.in/kozhikode_g4058877/for-rent-houses-apartments_c1723']

    def parse(self, response):
        # Extract links from the anchor tags within data-aut-id="itemsList1"
        for link in response.css('[data-aut-id="itemsList1"] a::attr(href)').getall():
            yield response.follow(link, self.parse_item)

    def parse_item(self, response):
        # Extract the data from the profileCard
        profile_card = response.css('[data-aut-id="profileCard"]')
        if profile_card:
            # Extract property name
            property_name = response.css('._1hJph[data-aut-id="itemTitle"]::text').get(default='').strip()
            
            # Extract property ID from the div with class _1-oS0
            property_id_parts = response.css('div._1-oS0 strong::text').getall()
            property_id = property_id_parts[-1].strip() if property_id_parts else None


            # Extract breadcrumbs as a list
            breadcrumbs = response.css('[data-aut-id="breadcrumb"] a::text').getall()
            breadcrumbs = [breadcrumb.strip() for breadcrumb in breadcrumbs]  # Clean up any extra spaces

            # Extract price (with currency and amount)
            price_div = response.css('[data-aut-id="itemPrice"]::text').get(default='').strip()
            if price_div:
                currency = price_div[0]  # The first character is the currency symbol
                amount = price_div[1:].replace(',', '').strip()  # Remove commas and extra spaces
                price_dict = {
                    'amount': amount,
                    'currency': currency
                }
            else:
                price_dict = None

            # Extract image URL from data-aut-id="defaultImg"
            #image_url = response.css('[data-aut-id="defaultImg"] img::attr(src)').get(default='').strip()
            image_url = response.css('div._23Jeb figure img::attr(src)').get(default='').strip()


            # Extract description
            #description = response.css('[data-aut-id="itemDescriptionContent"]::text').get(default='').strip()
            description = response.css('[data-aut-id="itemDescriptionContent"] p::text').get(default='').strip()


            # Extract seller_name from the anchor tag with class _2tgkn
            seller_name = response.css('._2tgkn a::attr(title)').get(default='').strip()

            # Extract location from div with class _3Uj8e
            location = response.css('span._1RkZP::text').get(default='').strip()

            # Extract property_type from class B6X7c
            property_type = response.css('.B6X7c[data-aut-id="value_type"]::text').get(default='').strip()

            # Extract bedrooms as integer
            bedrooms_str = response.css('.B6X7c[data-aut-id="value_rooms"]::text').get(default='0').strip()
            bedrooms = int(bedrooms_str) if bedrooms_str.isdigit() else 0

            # Extract bathrooms as integer
            bathrooms_str = response.css('.B6X7c[data-aut-id="value_bathrooms"]::text').get(default='0').strip()
            bathrooms = int(bathrooms_str) if bathrooms_str.isdigit() else 0

            # Construct the data dictionary
            data = {
                'property_name': property_name,
                'property_id': property_id,
                'breadcrumbs': breadcrumbs,
                'price': price_dict,
                'image_url': image_url,
                'description': description,
                'seller_name': seller_name,
                'location': location,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms
            }

            # Yield the extracted data
            yield data
