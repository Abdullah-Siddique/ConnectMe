# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///connectme.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded profile pictures
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(255))  # Adjust the length as needed
    educational_background = db.Column(db.Text)   # Or specify the appropriate type
    chat_info = db.Column(db.String(255))  # For storing chat info

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        profession = request.form['profession']
        contact = request.form['contact']
        educational_background = request.form['educational_background']
        chat_info = ''

        if not all([name, password, profession, contact, educational_background]):
            flash('Please fill in all fields.')
            return redirect(url_for('register'))  # Redirect back to the registration page

        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_picture_filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename))

        new_user = User(name=name, password=password, profession=profession, contact=contact,
                        profile_picture=profile_picture_filename, educational_background=educational_background,
                        chat_info=chat_info)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name, password=password).first()
        if user:
            return redirect(url_for('dashboard', username=name, profession=user.profession, contact=user.contact))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard/<username>/<profession>/<contact>')
def dashboard(username, profession, contact):
    return render_template('dashboard.html', username=username, profession=profession, contact=contact)

@app.route('/professions')
def professions():
    all_users = User.query.all()
    return render_template('profession.html', users=all_users)

@app.route('/search_results', methods=['POST'])
def search_results():
    if request.method == 'POST':
        profession = request.form.get('profession')
        if profession:
            users = User.query.filter_by(profession=profession).all()
            return render_template('search_results.html', users=users, profession=profession)
        else:
            flash('Please enter a valid profession to search.')
    return redirect(url_for('professions'))

@app.route('/search_form')
def search_form():
    return render_template('search_form.html')

@app.route('/professions/<profession>')
def profession_users(profession):
    users = User.query.filter_by(profession=profession).all()
    return render_template('profession_users.html', users=users, profession=profession)

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        message = request.form.get('message')
        user.chat_info = f"Last message: {message}"
        db.session.commit()
        flash('Message sent successfully!')
        return redirect(url_for('user_profile', user_id=user_id))
    return render_template('profile.html', user=user)

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
def chat_with_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        message = request.form.get('message')
        user.chat_info = f"Last message: {message}"
        db.session.commit()
        flash('Message sent successfully!')
        return redirect(url_for('chat_with_user', user_id=user_id))
    return render_template('chat.html', user=user)

@app.route('/delete_profile/<int:user_id>', methods=['POST'])
def delete_profile(user_id):
    user = User.query.get_or_404(user_id)
    profession = user.profession
    db.session.delete(user)
    db.session.commit()
    flash('Profile deleted successfully.')
    return redirect(url_for('profession_users', profession=profession))

@app.route('/delete_profile_menu')
def delete_profile_menu():
    all_users = User.query.all()
    return render_template('delete_profile_menu.html', users=all_users)

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        data = request.json
        recipient_id = data.get('recipient_id')
        message = data.get('message')
        # Code to send message to the recipient user and update chat_info in the database
        return jsonify({'success': True})  # Placeholder response

if __name__ == '__main__':
    app.run(debug=True)

