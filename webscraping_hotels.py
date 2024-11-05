from tkinter import Tk, Label, Entry, Button, messagebox
from datetime import datetime
from tkinter import ttk
from playwright.sync_api import sync_playwright
import pandas as pd

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

def get_inputs():
    city = city_entry.get().strip()
    checkin_date = checkin_entry.get().strip()
    checkout_date = checkout_entry.get().strip()
    num_adults = adults_entry.get().strip()
    num_children = children_entry.get().strip()

    if not validate_date(checkin_date) or not validate_date(checkout_date):
        messagebox.showerror("Error", "Check-in and check-out dates must be in the future.")
    elif not num_adults.isdigit() or not 1 <= int(num_adults) <= 2:
        messagebox.showerror("Error", "Number of adults must be an integer between 1 and 2.")
    elif not num_children.isdigit() or not 0 <= int(num_children) <= 2:
        messagebox.showerror("Error", "Number of children must be an integer between 0 and 2.")
    else:
        scrape_hotels(city, checkin_date, checkout_date, num_adults, num_children)

# Create tkinter window
root = Tk()
root.title("Hotel Booking Details")
root.geometry("450x250")  # Increased window size
root.configure(bg="#f0f0f0")

# Custom font settings
font = ("Arial", 12)  # Set the font family and size

# Labels and Entry fields for user inputs
Label(root, text="City:", font=font, bg="#f0f0f0").grid(row=0, column=0, pady=5, padx=5)
city_entry = Entry(root, font=font)
city_entry.grid(row=0, column=1, pady=5, padx=5)

Label(root, text="Check-in Date (YYYY-MM-DD):", font=font, bg="#f0f0f0").grid(row=1, column=0, pady=5, padx=5)
checkin_entry = Entry(root, font=font)
checkin_entry.grid(row=1, column=1, pady=5, padx=5)

Label(root, text="Check-out Date (YYYY-MM-DD):", font=font, bg="#f0f0f0").grid(row=2, column=0, pady=5, padx=5)
checkout_entry = Entry(root, font=font)
checkout_entry.grid(row=2, column=1, pady=5, padx=5)

Label(root, text="Number of Adults (1-2):", font=font, bg="#f0f0f0").grid(row=3, column=0, pady=5, padx=5)
adults_entry = Entry(root, font=font)
adults_entry.grid(row=3, column=1, pady=5, padx=5)

Label(root, text="Number of Children (0-2):", font=font, bg="#f0f0f0").grid(row=4, column=0, pady=5, padx=5)
children_entry = Entry(root, font=font)
children_entry.grid(row=4, column=1, pady=5, padx=5)

# Button to trigger scraping
scrape_button = Button(root, text="Search Hotels", font=font, command=get_inputs, bg="#008080", fg="white")
scrape_button.grid(row=5, columnspan=2, pady=10, padx=5)

root.mainloop()
