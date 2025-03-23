from flask import Flask, render_template, jsonify, request
from DogsTrust import scrape_dogs
import threading
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from CatScraper import scrape_cats


app = Flask(__name__)

# SQLite connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), nullable=False)  # Ensure this matches the key in the dictionary
    name = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80))
    location = db.Column(db.String(80))
    details = db.Column(db.Text)
    image_url = db.Column(db.String(200))  # Ensure this matches the key in the dictionary
    profile_url = db.Column(db.String(200), unique=True)  # Ensure this matches the key in the dictionary

# Create tables (run this once)
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table('pet'):  # Replace 'pet' with your table name
        db.create_all()
        print("Database tables created.")
    else:
        print("Database tables already exist.")

@app.route('/')
def home():
    return render_template('index.html')  # Serves the main page

@app.route('/find-a-pet')
def find_a_pet():
    return render_template('FindAPet.html')

@app.route('/vets')
def vets():
    return render_template('Vets.html')

@app.route('/pet-advice')
def pet_advice():
    return render_template('PetAdvice.html')

@app.route('/pet-sitters')
def pet_sitters():
    return render_template('PetSitters.html')

@app.route('/contact_us')
def contact_us():
    return render_template('ContactUs.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/scrape', methods=['GET'])
def scrape():
    def run_scraper():
        # Push the application context
        with app.app_context():
            try:
                # Scrape dog data
                scraped_dogs = scrape_dogs()
                
                # Scrape cat data
                scraped_cats = scrape_cats("https://www.pets4homes.co.uk/adoption/cats/")  # Provide the appropriate URL
                print("Scraped Dogs:", scraped_dogs)
                print("Scraped Cats:", scraped_cats)
                # Combine both dogs and cats data
                all_scraped_data = scraped_dogs + scraped_cats

                # Insert or update data in the database
                for pet in all_scraped_data:
                    existing_pet = Pet.query.filter_by(profile_url=pet['profile_url']).first()
                    if not existing_pet:
                        # Insert new pet
                        new_pet = Pet(
                            type=pet.get('type', 'Dog'),  # Default to 'Dog' if type is not provided
                            name=pet['name'],
                            breed=pet['breed'],
                            location=pet['location'],
                            details=pet['details'],
                            image_url=pet['image_url'],
                            profile_url=pet['profile_url']
                        )
                        db.session.add(new_pet)
                    else:
                        # Update existing pet (if needed)
                        existing_pet.name = pet['name']
                        existing_pet.breed = pet['breed']
                        existing_pet.location = pet['location']
                        existing_pet.details = pet['details']
                        existing_pet.image_url = pet['image_url']
                
                # Commit changes to the database
                db.session.commit()
                print("Scraping and database update complete.")
            except Exception as e:
                print(f"Error during scraping: {e}")
                db.session.rollback()  # Rollback in case of error
    
    # Run the scraper in a separate thread to avoid blocking the Flask app
    thread = threading.Thread(target=run_scraper)
    thread.start()

    return "Scraping started. Please wait..."
@app.route('/results', methods=['GET'])
def results():
    # Get the animal type and location from query parameters
    animal = request.args.get('animal')
    location = request.args.get('location')

    if not animal:
        return jsonify({"error": "Missing animal type"}), 400

    try:
        # Query the database for matching pets
        query = Pet.query.filter(Pet.type == animal)
        if location:
            query = query.filter(Pet.location == location)
        pets = query.all()

        # Convert the results to JSON
        pets_json = [{
            "name": pet.name,
            "breed": pet.breed,
            "location": pet.location,
            "details": pet.details,
            "image_url": pet.image_url,
            "profile_url": pet.profile_url
        } for pet in pets]

        return jsonify(pets_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/locations', methods=['GET'])
def get_locations():
    locations = db.session.query(Pet.location).distinct().all()
    locations_list = [loc[0] for loc in locations if loc[0] is not None]  # Ensure no None values
    return jsonify({"locations": locations_list})
@app.route('/locations/<animal>', methods=['GET'])
def get_locations_by_animal(animal):
    try:
        # Query the database for distinct locations for the selected animal
        locations = db.session.query(Pet.location).filter(Pet.type == animal).distinct().all()
        locations_list = [loc[0] for loc in locations if loc[0] is not None]  # Ensure no None values
        return jsonify({"locations": locations_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)