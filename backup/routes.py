from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from .models import db, User
from .forms import NickNameForm
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask_bootstrap import Bootstrap5

import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
Bootstrap5(app)


oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)


# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def home():
    return render_template('index.html')



@app.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v2/userinfo') 
    if resp.ok:
        user_info = resp.json()
        # Here, you'd typically create or update a user in your database
        # using the user_info
        for info in user_info:
            print(info)
        # Then log the user in:
        #login_user(user)  # Assuming you have a user object
    return redirect(url_for('index'))




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
            session['username'] = username
            session['oauth_token'] = token
            return redirect(url_for('nickname', username=username))
        else:
            login_user(user)
            session['username'] = username
            session['oauth_token'] = token
            flash('User logged in.', 'success')
            return redirect(url_for('home'))

    except Exception as e:
        app.logger.error(f"Authorization Error: {str(e)}")
        return "Error occurred during authorization!"



@app.route('/nickname', methods=['GET', 'POST'])
def nickname():
    form = NickNameForm()
    username = request.args.get('username')
    form.username.data = username

    if form.validate_on_submit():
        nickname = form.nickname.data
        print(f"{nickname}: {username}")
        new_user = User(
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






