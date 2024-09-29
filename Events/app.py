from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import hashlib
import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'a1f83445869b64940271592bf79871a4'  # Needed to use flash for showing messages

# Path to your Firebase Admin SDK credentials JSON file
cred = credentials.Certificate(r"C:\Users\User\Desktop\Events\tectra-12b77-firebase-adminsdk-zwedl-1ae6d93834.json")

# Initialize the Firebase app with the credentials and storage bucket
firebase_admin.initialize_app(cred, {
    'storageBucket': 'tectra-12b77.appspot.com'  # Replace with your actual bucket name
})

# Create a reference to the Firestore database
db = firestore.client()

# Get a reference to the storage bucket
bucket = storage.bucket()

# Hash password using SHA-256 for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/after_login_page')
def after_login_page():
    return render_template('after_login_page.html')

# Profile route
@app.route('/profile')
def profile():
    if 'user_id' not in session:  # Check if user is logged in
        flash("Please log in to access your profile.", "error")
        return redirect(url_for('login'))  # Redirect to the login page

    user_id = session['user_id']
    
    # Fetch user details from Firestore
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get().to_dict()

    if not user:
        flash("User not found.", "error")
        return redirect(url_for('login'))

    # Render profile page with user details
    return render_template('profile.html', user=user)




@app.route('/current_applications')
def current_app_page():
    return render_template('current_applications.html')

@app.route('/application_history')
def application_history_page():
    return render_template('application_history.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/your_event')
def your_event_page():
    return render_template('your_event.html')


# Update Profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        username = request.form['username']
        password = request.form['password']  # Ensure you hash this before saving
        email = request.form['email']

        # Update user information in Firestore
        db.collection('users').document(user_id).update({
            'name': username,
            'email': email,
            'password': hash_password(password)
        })

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
    else:
        flash("You need to log in first.", "error")
        return redirect(url_for('login'))

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/event-details')
def event_details():
    event_id = request.args.get('id')  # Get the event ID from the query parameter
    
    # Sample event data, in a real application, you would fetch this from a database
    event_data = {
        '1': {'name': '2024 BUSINESS Webinar', 'location': 'Madura, Tamil Nadu, India', 'date': 'Mar 23, 2024', 'image_url': 'static/img/event10.png'},
        '2': {'name': 'EOSC Symposium 2024', 'location': 'Coimbatore, Tamil Nadu, India', 'date': 'Nov 20, 2024', 'image_url': 'static/img/event11.png'},
        '3': {'name': 'Hackathon', 'location': 'Delhi, India', 'date': 'Sept 27, 2024', 'image_url': 'static/img/event12.png'},
    }
    
    event = event_data.get(event_id, {})
    return render_template('event_details.html', event=event)

@app.route('/your_event')
def your_event():
    user_id = session['user_id']
    events = db.collection('events').where('creator', '==', user_id).get()
    return render_template('your_event.html', events=events)


@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/api/book_ticket', methods=['POST'])
def book_ticket():
    # Get form data
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    image = request.files.get('image')  # Get the uploaded image file

    if not name or not phone or not email or not image:
        return jsonify({"message": "All fields are required."}), 400

    # Save the image to Firebase Storage
    try:
        image_filename = secure_filename(image.filename)
        blob = bucket.blob(f'bookings/{image_filename}')
        blob.upload_from_file(image)

        # Get the image's URL
        image_url = blob.generate_signed_url(expiration=3600)

        # Store booking data in Firestore, including image URL
        db.collection('bookings').add({
            'name': name,
            'phone': phone,
            'email': email,
            'image_url': image_url
        })

        return jsonify({"message": "Booking successful!"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error booking ticket. Please try again."}), 500

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        # Get data from the form
        category = request.form.get('category')
        event_name = request.form.get('eventName')
        date_time = request.form.get('dateTime')
        venue = request.form.get('venue')
        no_of_days = request.form.get('noOfDays')
        max_participants = request.form.get('maxParticipants')
        registration_fee = request.form.get('registrationFee')
        accommodation = request.form.get('accommodation')

        # Insert event data into Firestore
        try:
            db.collection('new_events').add({
                'category': category,
                'event_name': event_name,
                'date_time': date_time,
                'venue': venue,
                'no_of_days': no_of_days,
                'max_participants': max_participants,
                'registration_fee': registration_fee,
                'accommodation': accommodation
            })
            response = {"success": True}
        except Exception as e:
            response = {"success": False, "message": str(e)}
        
        return jsonify(response)
    
    return render_template('create_event.html')

# Upload documents
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    if 'uploadPAN' not in request.files or 'uploadAadhar' not in request.files:
        return jsonify({"success": False, "message": "Both PAN and Aadhar must be uploaded."})

    pan_file = request.files['uploadPAN']
    aadhar_file = request.files['uploadAadhar']
    brouser_file=request.files['uploadbrouser']

    # Upload PAN file to Firebase Storage
    pan_blob = bucket.blob(f'documents/PAN/{pan_file.filename}')
    pan_blob.upload_from_file(pan_file, content_type=pan_file.content_type)

    # Upload Aadhar file to Firebase Storage
    aadhar_blob = bucket.blob(f'documents/Aadhar/{aadhar_file.filename}')
    aadhar_blob.upload_from_file(aadhar_file, content_type=aadhar_file.content_type)

    brouser_blob = bucket.blob(f'documents/brousers/{brouser_file.filename}')
    brouser_blob.upload_from_file(brouser_file, content_type=brouser_file.content_type)

    return jsonify({"success": True, "message": "Documents uploaded successfully!"})

# Submit agreement
@app.route('/submit_agreement', methods=['POST'])
def submit_agreement():
    data = request.json

    organization_name = data.get('organizationName')
    organizer_email = data.get('organizerEmail')
    organizer_signature = data.get('organizerSignature')
    organizer_date = data.get('organizerDate')

    if all([organization_name, organizer_email, organizer_signature, organizer_date]):
        try:
            db.collection('agreements').add({
                'organization_name': organization_name,
                'organizer_email': organizer_email,
                'organizer_signature': organizer_signature,
                'organizer_date': organizer_date
            })
            return jsonify({"success": True, "message": "Agreement submitted successfully!"})
        except Exception as e:
            return jsonify({"success": False, "message": f"An unexpected error occurred: {str(e)}"})
    else:
        return jsonify({"success": False, "message": "All agreement fields must be filled."})

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_ref = db.collection('users').where('email', '==', email).limit(1).get()

        if user_ref:
            user = user_ref[0].to_dict()
            user_id = user_ref[0].id  # Firestore document ID
            stored_password = user['password']
            
            if stored_password == hash_password(password):
                session['user_id'] = user_id
                flash("Login successful!", "success")
                return redirect(url_for('after_login_page'))
            else:
                flash("Invalid email or password. Please try again.", "error")
        else:
            flash("No account found with this email. Please sign up.", "error")

    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user_ref = db.collection('users').where('email', '==', email).limit(1).get()

        if user_ref:
            flash("Email already exists. Please choose a different one.", "error")
            return redirect(url_for('signup'))

        hashed_password = hash_password(password)

        db.collection('users').add({
            'name': name,
            'email': email,
            'password': hashed_password
        })

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
