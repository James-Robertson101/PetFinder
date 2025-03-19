from flask import Flask, render_template, jsonify
from DogsTrust import scrape_dogs
import threading
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)

# SQLite connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80))
    location = db.Column(db.String(80))
    details = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    profile_url = db.Column(db.String(200), unique=True)

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
                # Scrape the data
                scraped_data = scrape_dogs()

                # Insert or update data in the database
                for dog in scraped_data:
                    existing_pet = Pet.query.filter_by(profile_url=dog['profile']).first()
                    if not existing_pet:
                        # Insert new pet
                        new_pet = Pet(
                            type=dog.get('type', 'Dog'),  # Default to 'Dog' if type is not provided
                            name=dog['name'],
                            breed=dog['breed'],
                            location=dog['location'],
                            details=dog['details'],
                            image_url=dog['image'],
                            profile_url=dog['profile']
                        )
                        db.session.add(new_pet)
                    else:
                        # Update existing pet (if needed)
                        existing_pet.name = dog['name']
                        existing_pet.breed = dog['breed']
                        existing_pet.location = dog['location']
                        existing_pet.details = dog['details']
                        existing_pet.image_url = dog['image']
                
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
    # Query the database for all pets
    pets = Pet.query.all()
    pets_json = [{
        "name": pet.name,
        "breed": pet.breed,
        "location": pet.location,
        "details": pet.details,
        "image_url": pet.image_url,
        "profile_url": pet.profile_url
    } for pet in pets]

    return jsonify(pets_json)

@app.route('/locations', methods=['GET'])
def get_locations():
    locations = db.session.query(Pet.location).distinct().all()
    locations_list = [loc[0] for loc in locations if loc[0] is not None]  # Ensure no None values
    return jsonify({"locations": locations_list})
if __name__ == '__main__':
    app.run(debug=True)