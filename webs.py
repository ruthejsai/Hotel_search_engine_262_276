from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

def validate_date(date_string):
    try:
        date = datetime.strptime(date_string, '%Y-%m-%d')
        if date < datetime.now():
            return False
        return True
    except ValueError:
        return False

def scrape_hotels(city, checkin_date, checkout_date, num_adults, num_children):
    with sync_playwright() as p:
        page_url = f'https://www.booking.com/searchresults.en-us.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=USD&ss={city}&ssne={city}&ssne_untouched={city}&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults={num_adults}&no_rooms=1&group_children={num_children}&sb_travel_purpose=leisure'
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)
                    
        hotels = page.locator('//div[@data-testid="property-card"]').all()
        print(f'There are: {len(hotels)} hotels in {city} from {checkin_date} to {checkout_date}.')
        
        hotels_list = []
        for hotel in hotels:
            hotel_dict = {}
            hotel_dict['hotel'] = hotel.locator('//div[@data-testid="title"]').inner_text()
            try:
                hotel_dict['price'] = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text(timeout=5000)
            except Exception as e:
                print(f"Error extracting price for hotel '{hotel_dict['hotel']}': {str(e)}")
                hotel_dict['price'] = 'N/A'
            hotel_dict['score'] = hotel.locator('//div[@data-testid="review-score"]/div[1]').inner_text()
            hotel_dict['avg review'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text()
            hotel_dict['reviews count'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text().split()[0]
            
            hotels_list.append(hotel_dict)
        
        df = pd.DataFrame(hotels_list)
        df.to_csv(f'{city}_hotels_data.csv', index=False)
        
        browser.close()

def main():
    city = input("Enter the name of the city: ").strip()
    checkin_date = input("Enter the check-in date (YYYY-MM-DD): ").strip()
    checkout_date = input("Enter the check-out date (YYYY-MM-DD): ").strip()
    num_adults = input("Enter the number of adults (1-2): ").strip()
    num_children = input("Enter the number of children (0-2): ").strip()

    if not validate_date(checkin_date) or not validate_date(checkout_date):
        print("Error: Check-in and check-out dates must be in the future.")
        return
    if not num_adults.isdigit() or not 1 <= int(num_adults) <= 2:
        print("Error: Number of adults must be an integer between 1 and 2.")
        return
    if not num_children.isdigit() or not 0 <= int(num_children) <= 2:
        print("Error: Number of children must be an integer between 0 and 2.")
        return

    scrape_hotels(city, checkin_date, checkout_date, num_adults, num_children)

if __name__ == '__main__':
    main()
