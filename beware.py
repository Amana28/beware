from flask import Flask, render_template, redirect, url_for, abort, request, flash, session
from dotenv import load_dotenv
from __init__ import app, db, bcrypt
from forms import *
from model import *
import requests
import os

def configure():
    load_dotenv()

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/bewaremap")
def first_map():
    # default map is NY
    return render_template('bewaremap.html', latitude = 40.7128, longitude = 74.0060, url = "https://maps.googleapis.com/maps/api/js?key=" + os.getenv('API_KEY') + "&callback=initMap")

@app.route("/bewaremap", methods=['POST', 'GET'])
def beware_map():
    address = request.form["location"]
    params = {
        'key': os.getenv('API_KEY'),
        'address': address
    }
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        result = data['results'][0]
        location = result['geometry']['location']
        LAT = location['lat']
        LNG = location['lng']
    else:
        return "address is invalid"
    return render_template('bewaremap.html', latitude = LAT, longitude = LNG, url = "https://maps.googleapis.com/maps/api/js?key=" + os.getenv('API_KEY') + "&callback=initMap") 

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # checks if entries are valid
        email=form.email.data
        password=form.password.data
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash(f'Logging you in', 'success')
            session['username'] = user.username
            return redirect(url_for('profile'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# logout route
@app.route('/logout')
def logout():
     session.pop('username', None)
     return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global user
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        pwd_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")   
        user = User(username = form.username.data, email = form.email.data, password = pwd_hash)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash('username or email taken, try again')
            return render_template('register.html', title='Register', form=form)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/myprofile")
def profile():
    return render_template('profile.html') 

@app.route("/report")
def report():
    return render_template('report.html')

if __name__ == '__main__': 
    configure()
    app.run(debug=True, host="0.0.0.0")
