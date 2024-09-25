import scrapy
import json
import csv

class OlxSpider(scrapy.Spider):
    name = "olx_spider"

    # Define the base URL with placeholders for parameters
    base_url = "https://www.olx.in/api/relevance/v4/search?category=1723&facet_limit=1000&lang=en-IN&location=4058877&location_facet_limit=20&page={page}&platform=web-desktop&pttEnabled=true&relaxedFilters=true&size=40&user=06222187199919496"

    # Set the number of pages to scrape
    max_pages = 10  

    def start_requests(self):
        # Loop to create requests for the desired number of pages
        for page in range(1, self.max_pages + 1):
            url = self.base_url.format(page=page)  # Replace {page} with the actual page number
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

    def parse(self, response):
        # Load JSON response
        data = json.loads(response.text)

        properties = []  # List to store all property data
        
        # Extract property data from the response
        for item in data.get('data', []):
            property_data = {}
            
            # Extract property name and ID
            property_data['property_name'] = item.get('title')
            property_data['property_id'] = item.get('ad_id')
            
            # Extract breadcrumbs
            property_data['breadcrumbs'] = item.get('breadcrumbs', [])

            # Extract price
            price_info = item.get('price', {})
            property_data['price'] = {
                'amount': price_info.get('value', {}).get('raw'),
                'currency': price_info.get('value', {}).get('currency', {}).get('pre', '₹')  # Default to ₹ if not present
            }
            
            # Extract image URL (taking first image URL for simplicity)
            images = item.get('images', [])
            property_data['image_url'] = images[0]['url'] if images else None  # Get the first image URL
            
            # Extract description
            property_data['description'] = item.get('description', "")

            # Extract seller name
            property_data['seller_name'] = item.get('user', {}).get('name', "Unknown Seller")  # Assuming user data is available

            # Extract location
            locations_resolved = item.get('locations_resolved', {})
            property_data['location'] = f"{locations_resolved.get('SUBLOCALITY_LEVEL_1_name')}, {locations_resolved.get('ADMIN_LEVEL_3_name')}, {locations_resolved.get('ADMIN_LEVEL_1_name')}"

            # Extract property type, bathrooms, and bedrooms
            parameters = item.get('parameters', [])
            for param in parameters:
                if param.get('key') == 'type':
                    property_data['property_type'] = param.get('value_name')
                elif param.get('key') == 'bathrooms':
                    try:
                        property_data['bathrooms'] = int(param.get('value_name', 0))
                    except ValueError:
                        # Handle non-integer cases (e.g., '4+')
                        property_data['bathrooms'] = int(param.get('value_name', '0').rstrip('+'))
                elif param.get('key') == 'rooms':
                    # Handle bedroom values
                    value_name = param.get('value_name', '0')
                    if value_name.endswith('+'):
                        property_data['bedrooms'] = int(value_name[:-1])  # Convert, removing '+'
                    else:
                        property_data['bedrooms'] = int(value_name)

            properties.append(property_data)

        # Log the number of properties processed
        self.log(f"Processed {len(properties)} properties on page {response.meta['page']}")

        # Save properties to CSV and JSON after processing all pages
        if response.meta['page'] == self.max_pages:
            self.save_to_files(properties)

    def save_to_files(self, properties):
        # Save data to JSON file
        with open('properties.json', 'w', encoding='utf-8') as json_file:
            json.dump(properties, json_file, ensure_ascii=False, indent=4)

        # Save data to CSV file
        with open('properties.csv', 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = properties[0].keys() if properties else []
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()  # Write the header
            writer.writerows(properties)  # Write the property data

        self.log("Data saved to properties.json and properties.csv")
