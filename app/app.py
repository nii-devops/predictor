from flask import Flask, redirect, render_template, url_for, flash, get_flashed_messages, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from wtforms import StringField, TextAreaField, SelectField, SubmitField, IntegerField, EmailField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from flask_bootstrap import Bootstrap5
import os
from authlib.integrations.flask_client import OAuth

import string
import random



weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 
         25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]


epl_teams = (
    ('---', "---"), 
    ('Arsenal', "ARS"), 
    ('Aston Villa', "AST"),
    ('Bournemouth', "BOU"), 
    ('Brentford', "BRE"), 
    ('Brighton', "BRI"), 
    ('Chelsea', "CHE"), 
    ('Crystal Palace', "CRY"), 
    ('Everton', "EVE"), 
    ('Fulham', "FUL"), 
    ('Ipswich Town', "IPS"), 
    ('Leicester City', "LEI"), 
    ('Liverpool', "LIV"), 
    ('Manchester City', "MNC"), 
    ('Manchester United', "MNU"), 
    ('Newcastle', "NEW"), 
    ('Nottingham Forest', "NFO"), 
    ('Southampton', "SOU"), 
    ('Tottenham', "TOT"), 
    ('West Ham', "WES"), 
    ('Wolves', "WOL")
)


class NickNameForm(FlaskForm):
    name        = StringField('Full Name', validators=[DataRequired()])
    nickname    = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "e.g. Oboy Siki"})  # Added placeholder
    username    = EmailField('Username', validators=[DataRequired(), Email()])
    submit      = SubmitField('Submit')


class LoginForm(FlaskForm):
    username    = EmailField('Email', validators=[DataRequired()])
    password    = PasswordField('Password', validators=[DataRequired()])
    submit      = SubmitField('SignIn')



class RegisterForm(FlaskForm):
    name        = StringField('Full Name', validators=[DataRequired()])
    nickname    = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "e.g. Oboy Siki"})
    username    = EmailField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    password_2  = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit      = SubmitField('SignUp')




def generate_secret_key():
    """Generate a random 32-character string."""

    invalid_chars = ['=' ,'#', ";", "'", '"', "(", ")", "[", "]", "{", "}"]

    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ""

    while len(secret_key) < 33:
        i = random.choice(characters)
        if i not in invalid_chars:
            secret_key += i
            
    
    # Read existing lines from .env file
    with open('.env', 'r') as env_file:
        lines = env_file.readlines()

    # Check if SECRET_KEY exists and replace it
    with open('.env', 'w') as env_file:
        secret_key_written = False  # Track if the secret key has been written
        for line in lines:
            if line.startswith('SECRET_KEY='):
                env_file.write(f'SECRET_KEY={secret_key}\n')  # Replace the existing key
                secret_key_written = True  # Mark that the key has been written
            else:
                env_file.write(line)  # Write unchanged lines
        
        if not secret_key_written:  # If SECRET_KEY was not found, append it
            env_file.write(f'SECRET_KEY={secret_key}\n')  # Append the new key

generate_secret_key()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Set the SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('LOCAL_DB_URI')#, 'sqlite:///site.db')  # Use environment variable or default to SQLite



db = SQLAlchemy()
db.init_app(app)

Bootstrap5(app)


from flask_login import UserMixin

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(30) )
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String())

    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ####################
# ### GOOGLE AUTH ####
# #####################

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template('index.html')



@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)



@app.route('/register')
def register():
    form = RegisterForm()
    return render_template('register.html', title='Register', form=form)



@app.route('/logout')
@login_required
def logout():
    user = current_user.fname
    logout_user()
    session.clear()
    flash(f"User {user} logged out.", 'success')
    return redirect(url_for('home'))





# Login for Google
@app.route('/login/google')
def google_login():
    try:
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        app.logger.error(f"Login Error: {str(e)}")
        return "Error occurred during login!"



# Authorize for Google
@app.route('/authorize/google')
def authorize_google():
    try:
        token = google.authorize_access_token()
        userinfo_endpoint = google.server_metadata.get('userinfo_endpoint')
        if not userinfo_endpoint:
            raise ValueError("User info endpoint not found in Google metadata.")
        
        resp = google.get(userinfo_endpoint)
        user_info = resp.json()  # use .json() to parse the response correctly
        for info in user_info:
            print(info)
        username = user_info.get('email')
        name = user_info.get('name')
        given_name = user_info.get('given_name')
        family_name = user_info.get('family_name')
        user_data = {
            'username': username,
            'name': name,
            'given_name': given_name,
            'family_name': family_name,
        }
        print(user_data)

        if not username:
            raise ValueError("Email not found in user information.")

        # Check if user exists or create a new one
        user = User.query.filter_by(username=username).first()
        if not user:
            session['name'] = name
            session['username'] = username
            session['oauth_token'] = token
            return redirect(url_for('nickname', username=username, name=name))
        else:
            login_user(user)
            flash('User logged in.', 'success')
            return redirect(url_for('home'))

    except Exception as e:
        app.logger.error(f"Authorization Error: {str(e)}")
        return "Error occurred during authorization!"



@app.route('/nickname', methods=['GET', 'POST'])
def nickname():
    form = NickNameForm()
    username = request.args.get('username')
    name = request.args.get('name')
    form.username.data = username
    form.name.data = name

    if form.validate_on_submit():
        nickname = form.nickname.data
        print(f"{nickname}: {username}")
        new_user = User(
            name=name,
            username=username,
            nickname=nickname
        )
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            flash("User logged in successfully.", "success")
            return redirect(url_for('home'))
        else:
            flash("User not found", 'danger')
    return render_template('nickname.html', title='Set Nickname', form=form)





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




