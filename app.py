from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import base64
import cv2
import numpy as np
import csv

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Change this to a secure key in production
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dummy user database (replace with a real database in production)
users = {}

# CSV file to store user data
CSV_FILE = 'users.csv'

# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Patient ID', 'Patient Name', 'Age', 'Gender', 'Height (cm)', 'Weight (kg)', 'Mobile Number', 'Location', 'Image'])

# Welcome route
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose another.', 'error')
        else:
            users[username] = {'password': password}
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

# Profile route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update user profile information
        users[session['username']].update({
            'patient_id': request.form['patient_id'],
            'patient_name': request.form['patient_name'],
            'age': request.form['age'],
            'gender': request.form['gender'],
            'height': request.form['height'],
            'weight': request.form['weight'],
            'mobile_number': request.form['mobile_number'],
            'location': request.form['location']
        })
        return redirect(url_for('instructions'))
    
    return render_template('profile.html')

# Instructions route
@app.route('/instructions')
def instructions():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('instructions.html')

# Camera route
@app.route('/camera', methods=['GET', 'POST'])
def camera():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get the base64 image data from the form
        image_data = request.form['image']
        image_data = image_data.split(',')[1]  # Remove the "data:image/png;base64," prefix
        
        # Decode the base64 image data
        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Save the image
        filename = f"{session['username']}_capture.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, image)
        
        # Update the user's image in the database
        users[session['username']]['image'] = filename
        
        # Save user data to CSV
        user = users[session['username']]
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                user.get('patient_id', ''),
                user.get('patient_name', ''),
                user.get('age', ''),
                user.get('gender', ''),
                user.get('height', ''),
                user.get('weight', ''),
                user.get('mobile_number', ''),
                user.get('location', ''),
                filename
            ])
        
        return redirect(url_for('thank_you'))
    
    return render_template('camera.html')

# Report route
@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users[session['username']]
    return render_template('report.html', user=user)

# Thank You route
@app.route('/thank_you')
def thank_you():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('thank_you.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)
