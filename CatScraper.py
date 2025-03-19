from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (remove for debugging)
chrome_options.add_argument("--disable-gpu")

# Set up ChromeDriver service
service = Service("chromedriver.exe")  # Ensure chromedriver.exe is in the same directory or provide full path
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to get the maximum number of pages from the pagination element
def get_max_pages():
    try:
        # Wait for the pagination buttons to load
        page_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'Pagination_pageItem__BoC_z'))
        )

        # Get the text of the last button (which represents the max page number)
        if page_buttons:
            max_pages = int(page_buttons[-1].text)  # Convert to integer
            print(f"Max pages found: {max_pages}")
            return max_pages
        else:
            print("No page buttons found. Assuming only 1 page.")
            return 1

    except Exception as e:
        print(f"Error extracting max pages: {e}")
        return 1  # Default to 1 page if there's an error

# Function to scrape listings from a given URL
def scrape_page(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    try:
        # Accept cookies if needed
        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
        )
        agree_button.click()
        print("Cookie consent accepted.")
    except Exception as e:
        print(f"Cookie button not found or already accepted. Error: {e}")

    # Find all listing elements
    listings = driver.find_elements(By.CSS_SELECTOR, 'a.ListingTile_tileLink__z3gRk')

    cats = []  # List to store all scraped cat listings

    if listings:
        print(f"Found {len(listings)} listings on {url}.")
        for i, listing in enumerate(listings):
            try:
                pet_type = "Cat"  # Static value for all listings
                
                # Extracting elements
                name = listing.find_element(By.CSS_SELECTOR, 'h2.TileBody_title__g_KqB').text
                breed = listing.find_element(By.CSS_SELECTOR, 'span[data-testid="listing-tile-attr-breed"]').text
                location = listing.find_element(By.CSS_SELECTOR, 'span[data-testid="listing-location"]').text
                details = listing.find_element(By.CSS_SELECTOR, 'span.TileBody_description__PjbHO').text
                img_element = listing.find_element(By.CSS_SELECTOR, 'img.ListingTileThumbnail_thumbnailImage__UsgKt')
                img_src = img_element.get_attribute("src") if img_element else None
                profile_link = listing.get_attribute("href")

                # Storing data in dictionary format
                cats.append({
                    "type": pet_type,
                    "name": name,
                    "breed": breed,
                    "location": location,
                    "details": details,
                    "image_url": img_src,
                    "profile_url": profile_link
                })

            except Exception as e:
                print(f"Error scraping listing {i+1}: {e}")
    else:
        print(f"No listings found on {url}. Check the CSS selector.")

    return cats

# Function to scrape all pages and return a list of dictionaries
def scrape_cats(base_url):
    all_cats = []
    page_number = 1

    # Navigate to the base URL to load the pagination element
    driver.get(base_url)
    time.sleep(3)  # Wait for the page to load

    # Get the max number of pages
    max_pages = get_max_pages()

    while page_number <= max_pages:
        # Construct the URL for the current page
        current_url = f"{base_url}?page={page_number}"
        print(f"Scraping page {page_number}: {current_url}")

        # Scrape the current page
        listings = scrape_page(current_url)
        all_cats.extend(listings)

        # Check if there are listings on the current page
        if not listings:
            print(f"No listings found on page {page_number}. Stopping pagination.")
            break

        # Move to the next page
        page_number += 1

    return all_cats

# Main script
base_url = "https://www.pets4homes.co.uk/adoption/cats/"
scrape_cats(base_url)

# Close the browser
driver.quit()


