from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

def scrape_dogs():
    """
    Scrapes all dog listings from Dog's Trust website.
    
    Returns:
        list: A list of dictionaries containing dog details.
    """
    # Set up ChromeDriver
    service = Service("chromedriver.exe")  # Update this with the correct path if needed
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigate to the website
        base_url = "https://dogstrust.org.uk/rehoming"
        driver.get(base_url)

        # Accept cookies
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            ).click()
            print("Cookies accepted.")
        except Exception as e:
            print("Failed to accept cookies:", e)

        # Click the "Show dogs" button
        try:
            show_dogs_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Button-module--primary--145cb.Button-module--basebutton--57c04"))
            )
            show_dogs_button.click()
            print("'Show dogs' button clicked.")
        except Exception as e:
            print("Failed to click 'Show dogs' button:", e)
            return {"error": "Failed to click 'Show dogs' button"}

        # Wait for listings to load
        time.sleep(1)  # Can be improved with explicit waits

        # Scrape dog listings
        dogs = []
        page_number = 1  # Initialize page counter

        while True:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "DogListingCard-module--dogcardcontainer--11630"))
                )
            except:
                print("No more dog cards found.")
                break

            dog_cards = driver.find_elements(By.CLASS_NAME, "DogListingCard-module--dogcardcontainer--11630")

            for card in dog_cards:
                try:
                    name = card.find_element(By.CLASS_NAME, "DogListingCard-module--dognametext--be57e").text
                except:
                    name = "N/A"

                try:
                    breed = card.find_element(By.CLASS_NAME, "DogListingCard-module--dogbreedtext--00794").text
                except:
                    breed = "N/A"

                try:
                    location = card.find_element(By.CLASS_NAME, "DogListingCard-module--rehomingcentretext--c6be8").text
                except:
                    location = "N/A"

                try:
                    details = card.find_element(By.CLASS_NAME, "DogListingCard-module--dogcarddetails--a06d2").text
                except:
                    details = "N/A"

                try:
                    img = card.find_element(By.TAG_NAME, "img")
                    img_src = img.get_attribute("src")
                except:
                    img_src = "N/A"

                try:
                    link = card.find_element(By.TAG_NAME, "a")
                    profile_link = link.get_attribute("href")
                except:
                    profile_link = "N/A"

                dogs.append({
                    "animal": "Dog",  # Use 'animal' instead of 'type' if required
                    "name": name,
                    "breed": breed,
                    "location": location,
                    "details": details,
                    "image_url": img_src,  # Change 'image' to 'image_url'
                    "profile_url": profile_link  # Change 'profile' to 'profile_url'
                    })
            # Try to find and click the "Next" button
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                )
                next_button.click()
                page_number += 1  # Increment page count
                print(f"Scraping page {page_number}...")  # Display current page number
                time.sleep(0.5)  # Allow time for new page to load
            except:
                print("No more pages to scrape.")
                break

    finally:
        driver.quit()  # Ensure the driver closes properly


    print("Dog data saved successfully.")
    return dogs
