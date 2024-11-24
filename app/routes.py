from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, oauth, login_manager
from app.forms import (LoginForm, RegisterForm, NickNameForm, SelectWeekForm, FixtureForm, PredictionForm,
                       UserPredictionForm, EditUserForm, PasswordForm, UserEmailForm)
from app.models import *
import os
from datetime import datetime, timedelta
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets



accounts = [
    {'full_name': 'John Smith', 'email': 'john.smith@example.com', 'nickname': 'Johnny', 'password': 'Password123'}, 
    {'full_name': 'Emily Johnson', 'email': 'emily.johnson@example.com', 'nickname': 'EmJay', 'password': 'Securepass45'}, 
    {'full_name': 'Michael Brown', 'email': 'michael.brown@example.com', 'nickname': 'MikeB', 'password': 'Mike1234'}, 
    {'full_name': 'Sarah Davis', 'email': 'sarah.davis@example.com', 'nickname': 'SassySarah', 'password': 'Sarahrocks98'}, 
    {'full_name': 'David Miller', 'email': 'david.miller@example.com', 'nickname': 'Davey', 'password': 'Dmiller007'},
    {'full_name': 'Jessica Wilson', 'email': 'jessica.wilson@example.com', 'nickname': 'Jessie', 'password': 'Jessie4321'}, 
    {'full_name': 'Christopher Garcia', 'email': 'chris.garcia@example.com', 'nickname': 'ChrisG', 'password': 'Chrispass456'}, 
    {'full_name': 'Amanda Martinez', 'email': 'amanda.martinez@example.com', 'nickname': 'Mandy', 'password': 'Mandy786'}, 
    {'full_name': 'Daniel Hernandez', 'email': 'daniel.hernandez@example.com', 'nickname': 'DannyH', 'password': 'Dannyrocks123'}, 
    {'full_name': 'Laura Moore', 'email': 'laura.moore@example.com', 'nickname': 'Laurie', 'password': 'Laura5678'}, 
    {'full_name': 'James Taylor', 'email': 'james.taylor@example.com', 'nickname': 'JTaylor', 'password': 'Jamesbond2021'}, 
    {'full_name': 'Olivia Anderson', 'email': 'olivia.anderson@example.com', 'nickname': 'Livvy', 'password': 'Olivia@Home'}, 
    {'full_name': 'Matthew Thomas', 'email': 'matthew.thomas@example.com', 'nickname': 'MattT', 'password': 'Mathpass1'}, 
    {'full_name': 'Sophia Jackson', 'email': 'sophia.jackson@example.com', 'nickname': 'Sophie', 'password': 'Sophieisgreat'}, 
    {'full_name': 'Andrew White', 'email': 'andrew.white@example.com', 'nickname': 'AndyW', 'password': 'Andyw234'}, 
    {'full_name': 'Isabella Harris', 'email': 'isabella.harris@example.com', 'nickname': 'Bella', 'password': 'Bella567'}, 
    {'full_name': 'Ethan Martin', 'email': 'ethan.martin@example.com', 'nickname': 'E-Mart', 'password': 'Ethanmartinpass'}, 
    {'full_name': 'Mia Thompson', 'email': 'mia.thompson@example.com', 'nickname': 'Mimi', 'password': 'Miathomp123'}, 
    {'full_name': 'William Garcia', 'email': 'william.garcia@example.com', 'nickname': 'WillG', 'password': 'Willie123'}, 
    {'full_name': 'Ava Martinez', 'email': 'ava.martinez@example.com', 'nickname': 'Avie', 'password': 'Avaava22'}
            ]


teams_names = {
    'ARS': 'Arsenal', 
    'AST': 'Aston Villa', 
    'BOU': 'Bournemouth', 
    'BRE': 'Brentford', 
    'BRI': 'Brighton', 
    'CHE': 'Chelsea', 
    'CRY': 'Crystal Palace', 
    'EVE': 'Everton', 
    'FUL': 'Fulham', 
    'IPS': 'Ipswich Town', 
    'LEI': 'Leicester City', 
    'LIV': 'Liverpool', 
    'MNC': 'Manchester City', 
    'MNU': 'Manchester United', 
    'NEW': 'Newcastle', 
    'NFO': 'Nottingham Forest', 
    'SOU': 'Southampton', 
    'TOT': 'Tottenham', 
    'WES': 'West Ham', 
    'WOL': 'Wolves'
    }



def reverse_team_names():
    reversed_names = {}
    for i,j in teams_names.items():
        reversed_names[j] = i
    return reversed_names 



def register_routes(app):

    google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
    )


    @app.before_request  # Use before_request to apply to the entire app
    def session_management():
        session.permanent = True  # Set the session as permanent
        session.modified = True   # Update session with each request

        # If the user is logged in, check session expiry
        if current_user.is_authenticated:
            if 'last_activity' in session:
                # Ensure last_activity is timezone-aware
                last_activity = session['last_activity'].replace(tzinfo=datetime.now().tzinfo)
                idle_time = timedelta(minutes=10)  # Idle time limit
                if datetime.now() - last_activity > idle_time:
                    # If idle time exceeded, log out user and clear session
                    logout_user()
                    session.clear()
                    return redirect(url_for('login'))  # Redirect to login page

            # Update last activity time if session is still active
            session['last_activity'] = datetime.now()  # This will be timezone-aware



    @app.route('/')
    def home():
        return render_template('index.html')

    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            new_user = User(
                name=form.name.data,
                nickname=form.nickname.data,
                username=form.username.data,
                password=form.password.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.password == form.password.data:
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            flash('Invalid credentials.', 'danger')
        return render_template('login.html', title='Login', form=form)



    @app.route('/logout')
    @login_required
    def logout():
        user = current_user.name
        logout_user()
        session.clear()
        flash(f'User {user} logged out.', 'success')
        return redirect(url_for('home'))


    import secrets

    """
    @app.route('/login/google')
    def google_login():
        try:
            # Generate a nonce and store it in the session
            session['nonce'] = secrets.token_urlsafe(16)
            redirect_uri = url_for('authorize_google', _external=True)
            return google.authorize_redirect(redirect_uri)
        except Exception as e:
            app.logger.error(f"Login Error: {str(e)}")
            return "Error occurred during login!"

    """

    @app.route('/login/google')
    def google_login():
        try:
            # Generate a nonce and store it in the session
            session['nonce'] = secrets.token_urlsafe(16)
            #redirect_uri = url_for('authorize_google', _external=True)
            redirect_uri = os.getenv('REDIRECT_URI')
            return google.authorize_redirect(redirect_uri)
        except Exception as e:
            app.logger.error(f"Login Error: {str(e)}")
            return "Error occurred during login!"




    """
    
    # Login for Google
    @app.route('/login/google')
    def google_login():
        try:
            redirect_uri = url_for('authorize_google', _external=True)
            return google.authorize_redirect(redirect_uri)
        except Exception as e:
            app.logger.error(f"Login Error: {str(e)}")
            return "Error occurred during login!"
    """

    """
    @app.route('/authorize/google')
    def authorize_google():
        try:
            token = google.authorize_access_token()

            # Retrieve the nonce from the session
            nonce = session.pop('nonce', None)
            if not nonce:
                raise ValueError("Nonce is missing from session.")

            userinfo_endpoint = google.server_metadata.get('userinfo_endpoint')
            if not userinfo_endpoint:
                raise ValueError("User info endpoint not found in Google metadata.")

            # Parse the ID token and verify the nonce
            id_token = token.get('id_token')
            google.parse_id_token(id_token, nonce)

            resp = google.get(userinfo_endpoint)
            user_info = resp.json()
            username = user_info.get('email')
            name = user_info.get('name')
            profile_picture = user_info.get('picture')  # Retrieve the profile picture

            if not username:
                raise ValueError("Email not found in user information.")

            # Check if user exists or create a new one
            user = User.query.filter_by(username=username).first()
            if not user:
                session['name'] = name
                session['username'] = username
                session['oauth_token'] = token
                session['profile_picture'] = profile_picture  # Store profile picture in session
                return redirect(url_for('nickname', username=username, name=name))
            else:
                login_user(user)
                flash('User logged in.', 'success')
                return redirect(url_for('home'))

        except Exception as e:
            app.logger.error(f"Authorization Error: {str(e)}")
            return "Error occurred during authorization!"


    """ 

    @app.route('/authorize/google')
    def authorize_google():
        try:
            token = google.authorize_access_token()

            # Retrieve the nonce from the session
            nonce = session.pop('nonce', None)
            if not nonce:
                raise ValueError("Nonce is missing from session.")

            userinfo_endpoint = google.server_metadata.get('userinfo_endpoint')
            if not userinfo_endpoint:
                raise ValueError("User info endpoint not found in Google metadata.")

            # Parse the ID token and verify the nonce
            id_token = token.get('id_token')
            google.parse_id_token(id_token, nonce)

            resp = google.get(userinfo_endpoint)
            user_info = resp.json()
            username = user_info.get('email')
            name = user_info.get('name')

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
        form.name.data = request.args.get('name')
        form.username.data = request.args.get('username')

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()  # Ensure to fetch the first user
            if not user:
                # Handle the image upload
                if not form.picture.data:
                    new_user = User(
                    name=form.name.data,
                    nickname=form.nickname.data,
                    username=form.username.data,
                    #picture=filename  # Save the filename in the database
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user)
                    flash('User registered successfully.', 'success')
                    return redirect(url_for('home'))
                else:
                    # Generate a random string for the filename
                    random_string = secrets.token_hex(8)  # Generate a random string
                    filename = secure_filename(f"{random_string}_{form.picture.data.filename}")  # Secure the filename
                    form.picture.data.save(os.path.join('app/static/img/profile_pictures', filename))  # Save the image

                    new_user = User(
                        name=form.name.data,
                        nickname=form.nickname.data,
                        username=form.username.data,
                        picture=filename  # Save the filename in the database
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    login_user(new_user)
                    flash('User registered successfully.', 'success')
                    return redirect(url_for('home'))
            flash(f"User {form.username.data} already exists")
            return redirect(url_for('login'))
        return render_template('nickname.html', title='Set Nickname', form=form)


    """
    @app.route('/nickname', methods=['GET', 'POST'])
    def nickname():
        form = NickNameForm()
        form.name.data = request.args.get('name')
        form.username.data = request.args.get('username')

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data)
            if not user:
                new_user = User(
                    name=form.name.data,
                    nickname=form.nickname.data,
                    username=form.username.data,
                    picture=form.picture.data
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                flash('User registered successfully.', 'success')
                return redirect(url_for('home'))
            flash(f"User {form.username.data} already exists")
            return redirect(url_for('login'))
        return render_template('nickname.html', title='Set Nickname', form=form)
   
    """


    @app.route('/profile')
    @login_required
    def profile():
        currentUser = User.query.filter_by(id=current_user.id).first()
        if not currentUser:
            flash('User does not exist', 'danger')
            return redirect(url_for('home'))
        all_scores = []
        points = 0
        position = None
        rank_id = None
        users = User.query.all()
        for user in users:
            score = sum(score.points for score in Score.query.filter_by(user_id=user.id).all())
            item = {user.id: score}
            all_scores.append(item)
        sorted_scores = sorted(all_scores, key=lambda x: list(x.values())[0], reverse=True)
        print(sorted_scores)

        for i,j in enumerate(sorted_scores):
            for key,val in j.items():
                if int(key) == currentUser.id:
                    points = val
                    rank_id = i+1
        if str(rank_id)[-1] == '1':
            position = f"{rank_id}st"
        elif str(rank_id)[-1] == '2':
            position = f"{rank_id}nd"
        elif str(rank_id)[-1] == '3':
            position = f"{rank_id}rd"
        else:
            position = f"{rank_id}th"

        return render_template('profile.html', title='Profile', user=currentUser, position=position, points=points)



    @app.route('/select-matchweek', methods=['GET', 'POST'])
    def match_week():
        form = SelectWeekForm()

        if form.validate_on_submit():

            week_number = form.week.data
            # Ensure week_number is an integer
            try:
                week_number = int(week_number)  # Convert to integer
            except ValueError:
                flash("Invalid week number!", category='warning')
                return render_template('match_week.html', title='Select Week', form=form)

            # Check if the week_number already exists
            if not Week.query.filter_by(week_number=week_number).first():
                week = Week(
                    week_number=week_number
                )
                db.session.add(week)
                db.session.commit()  # Define message
                flash(f'Week {week_number} created successfully!', 'success')
                return redirect(url_for('fixtures'))
            else:
                flash(f'Week {week_number} already exists!', 'warning')
        else:
            message = None  # Define message as None if form is not submitted
        return render_template('match_week.html', title='Select Week', form=form)  # Pass message to template



    @app.route('/fixture', methods=['GET', 'POST'])
    @login_required
    def fixtures():
        form = FixtureForm()
        
        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        if weeks:
            form.game_week.data = max(week.week_number for week in weeks)
        #form.game_week.choices = [(week.week_number, f"Week {week.week_number}") for week in weeks]

        if form.validate_on_submit():  # Check if the form is submitted and valid
            week = form.game_week.data
            # Ensure week is an integer
            try:
                week = int(week)  # Convert to integer
            except ValueError:
                flash("Invalid week selection!", category='warning')
                return render_template('fixtures.html', title='Home', form=form)

            # valid_teams = ['ARS', 'AST', 'BOU', 'BRE', 'BRI', 'CHE', 'CRY', 'EVE', 'FUL', 'IPS',
            #     'LEI', 'LIV', 'MNC', 'MNU', 'NEW', 'NFO', 'SOU', 'TOT', 'WES', 'WOL']  # Define your list of valid teams here

            # Validate that home and away teams are in the valid_teams list
            for i in range(1,11):
                if form[f'home_{i}'].data not in teams_names.values() or form[f'away_{i}'].data not in teams_names.values():
                    flash(f"Invalid team selection for match {i}!", category='warning')
                    return render_template('fixtures.html', title='Home', form=form)

            fixture_data = {
                "match_1": f"{form.home_1.data}-{form.away_1.data}",
                "match_2": f"{form.home_2.data}-{form.away_2.data}",
                "match_3": f"{form.home_3.data}-{form.away_3.data}",
                "match_4": f"{form.home_4.data}-{form.away_4.data}",
                "match_5": f"{form.home_5.data}-{form.away_5.data}",
                "match_6": f"{form.home_6.data}-{form.away_6.data}",
                "match_7": f"{form.home_7.data}-{form.away_7.data}",
                "match_8": f"{form.home_8.data}-{form.away_8.data}",
                "match_9": f"{form.home_9.data}-{form.away_9.data}",
                "match_10": f"{form.home_10.data}-{form.away_10.data}",
            }
            # Check if the fixture already exists for the given week_id
            existing_fixture = Fixture.query.filter_by(week_id=week).first()
            if existing_fixture:
                flash(f'Fixtures for week {week} already exist!', 'warning')
                return redirect(url_for('home'))  # Redirect if it exists

            new_fixture = Fixture(
                week_id=week,
                matches=fixture_data
            )  # Create a new Fixture instance
            db.session.add(new_fixture)  # Add to the session
            db.session.commit()  # Commit the session
            
            flash(f'Week {week} fixtures created successfully!', 'success')  # Flash a success message
            return redirect(url_for('home'))  # Redirect to the fixtures page
        return render_template('fixtures.html', title='Create Fixture', form=form)


    
    @app.route('/predict', methods=['GET', 'POST'])
    @login_required
    def predict():
        form = PredictionForm()

        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        if weeks:
            form.game_week.data = max(week.week_number for week in weeks)

        week = form.game_week.data
        try:
            week = int(week)  # Convert to integer if possible
        except (TypeError, ValueError):
            flash("Invalid week number provided!", category='danger')
            return redirect(url_for('prediction_week'))

        # Create empty lists for home and away teams
        home_teams = []
        away_teams = []

        # Query the Fixture table for the specified week
        fixture_data = Fixture.query.filter_by(week_id=week).first()
        if fixture_data:
            data = fixture_data.matches
            for key, val in data.items():
                home, away = val.split('-')
                home_teams.append(home)
                away_teams.append(away)

            # Populate the form with home and away teams
            for i in range(len(home_teams)):
                if i < 10:  # Ensure we don't exceed the form fields
                    form[f'home_{i + 1}'].data = home_teams[i]
                    form[f'away_{i + 1}'].data = away_teams[i]

        # When form is submitted
        if form.validate_on_submit():
            game_week = week
            prediction_data = {}
            for i in range(1, 11):  # Iterate from 1 to 10 to populate predicted scores into a JSON-formatted text
                prediction_data[f"{form[f'home_{i}'].data}-{form[f'away_{i}'].data}"] = {
                    "home": f"{form[f'home_{i}_score'].data}",
                    "away": f"{form[f'away_{i}_score'].data}"
                }
            # Write/Save data to database
            prediction = Prediction(
                week_id             = game_week,
                user_id             = current_user.id,
                user_predictions    = prediction_data
            )
            db.session.add(prediction)
            db.session.commit()
            flash(f"Predictions for Game Week {game_week} submitted.", 'success')
            return redirect(url_for('home'))
        return render_template('predict.html', title='Predict Results', form=form, week=week)

    

    @app.route('/results', methods=['GET', 'POST'])
    # @login_required
    def results():
        form = PredictionForm()

        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        if weeks:  # Check if there are any weeks
            form.game_week.data = max(week.week_number for week in weeks)  # Set the highest week_number

        # Get and validate the week parameter
        week = form.game_week.data

        try:
            week = int(week)  # Convert to integer if possible
        except (TypeError, ValueError):
            flash("Invalid week number provided!", category='danger')
            return redirect(url_for('prediction_week'))

        # Create empty lists for home and away teams
        home_teams = []
        away_teams = []

        # Query the Fixture table for the specified week
        fixture_data = Fixture.query.filter_by(week_id=week).first()
        if fixture_data:
            data = fixture_data.matches
            for key, val in data.items():
                home, away = val.split('-')
                home_teams.append(home)
                away_teams.append(away)

            # Populate the form with home and away teams
            for i in range(len(home_teams)):
                if i < 10:  # Ensure we don't exceed the form fields
                    form[f'home_{i + 1}'].data = home_teams[i]
                    form[f'away_{i + 1}'].data = away_teams[i]

        if form.validate_on_submit():
            game_week = form.game_week.data
            results_data = {}
            for i in range(1, 11):  # Iterate from 1 to 10 to populate predicted scores into a JSON-formatted text
                results_data[f"{form[f'home_{i}'].data}-{form[f'away_{i}'].data}"] = {
                    "home": f"{form[f'home_{i}_score'].data}",
                    "away": f"{form[f'away_{i}_score'].data}"
                }
            # Write/Save data to database
            results = Result(
                week_id = game_week,
                results = results_data
            )
            db.session.add(results)
            db.session.commit()
            flash(f"Results for Game Week {game_week} submitted.", 'success')
            score()
            return redirect(url_for('home'))

        return render_template('results.html', title='Enter Results', form=form, week=week)



    @app.route('/show-fixtures', methods=['GET' ,'POST'])
    def get_fixtures():
        form = SelectWeekForm()
        keys = []
        matches = []
        if form.validate_on_submit():
            wk = form.week.data
            fixture_data = Fixture.query.filter_by(week_id=wk).first()
            if fixture_data:
                data = fixture_data.matches
                print(data)
                for key, val in data.items():
                    matches.append(val)
                return render_template('get_fixtures.html', keys=keys, matches=matches, week=wk)  # Return the JSON response

        return render_template('get_fixtures.html', title='Test Data', form=form)



    @app.route('/get-user-data', methods=['GET' ,'POST'])
    def get_user():
        form = UserEmailForm()
        
        if form.validate_on_submit():
            email = form.email.data
            user = User.query.filter_by(email=email).first()

            if user:
                user_id = user.id
                name = user.name
                user_email = user.email
                return render_template('get_user.html', id=user_id, name=name, email=user_email)  # Return the JSON response

        return render_template('get_user.html', title='Find User', form=form)



    @app.route('/get-user-predictions', methods=['GET' ,'POST'])
    def get_user_predictions():
        form = UserPredictionForm()  
        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        form.week.choices = [(week.week_number, f"Week {week.week_number}") for week in weeks]

        if form.validate_on_submit():
            week = form.week.data
            username = form.email.data

            try:
                week = int(week)  # Convert to integer if possible
            except (TypeError, ValueError):
                flash("Invalid week number provided!", category='danger')
                return redirect(url_for('get_predictions'))
            user = User.query.filter_by(username=username).first()
            user_prediction = Prediction.query.filter_by(user_id=user.id, week_id=week).first()
            data = user_prediction.user_predictions
            matches = {}
            if user_prediction:
                user_id = user.id
                name = user.name
                user_email = user.email
                num = 1
                for key,val in data.items():
                    ht,at = key.split("-")
                    matches[f"Match {num}"] = {
                            ht: val["home"],
                            at: val["away"]
                        }
                    num += 1
                print(matches)
                return render_template('get_user_predictions.html', id=user_id, name=name, week=week, matches=matches, email=user_email)  # Return the JSON response

        return render_template('get_user_predictions.html', title='User Predictions', form=form)



    @app.route('/get-predictions', methods=['GET' ,'POST'])
    def get_predictions():
        form = SelectWeekForm() 
        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        form.week.choices = [(week.week_number, f"Week {week.week_number}") for week in weeks]

        # New code to set the highest week_number in the form
        if weeks:  # Check if there are any weeks
            form.week.data = max(week.week_number for week in weeks)  # Set the highest week_number

        if form.validate_on_submit():
            week = form.week.data

            try:
                week = int(week)  # Convert to integer if possible
            except (TypeError, ValueError):
                flash("Invalid week number provided!", category='danger')
                return redirect(url_for('get_predictions'))
            
            team_names = reverse_team_names()

            match_list = ["Name"]
            match_data = Fixture.query.filter_by(week_id=week).first()
            matches = match_data.matches
    
            for key, val in matches.items():
                h_team, a_team = val.split("-")
                h_team = team_names[h_team]
                a_team = team_names[a_team]
                match_list.append(f"{h_team}-{a_team}")

            full_scores = {}
            print(full_scores)

            users_data = User.query.order_by(User.name).all()
            for user in users_data:
                user_pred = Prediction.query.filter_by(week_id=week, user_id=user.id)#.first()
                if user_pred and week == 1:  # Check if user predictions exist
                    name = user.name
                    user_scores = []  # Ensure this is initialized as a list
                    for key, val in user_pred[0].user_predictions.items():
                        home_team, away_team = key.split("-")
                        home_team = team_names[home_team]
                        away_team = team_names[away_team]
                        score = f"{val['home']}-{val['away']}"
                        user_scores.append(score)  # Ensure scores are appended correctly
                    # Clear user_scores only after processing all predictions for the user
                    full_scores[name] = user_scores  # This should work as intended
            print(full_scores)
            return render_template('get_predictions.html', matches=match_list, scores=full_scores, week=week)

        return render_template('get_predictions.html', form=form)  # Pass predictions to the template



    @app.route('/get-results', methods=['GET' ,'POST'])
    def get_results():
        form = SelectWeekForm()
        
        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        form.week.choices = [(week.week_number, f"Week {week.week_number}") for week in weeks]

        if form.validate_on_submit():
            week = form.week.data            
            try:
                week = int(week)  # Convert to integer if possible
            except (TypeError, ValueError):
                flash("Invalid week number provided!", category='danger')
                return redirect(url_for('get_predictions'))

            match_results = Result.query.filter_by(week_id=week).first()
            data = match_results.matches
            results = {}
            if match_results:
                num = 1
                for key,val in data.items():
                    ht,at = key.split("-")
                    results[f"Match {num}"] = {
                            ht: val["home"],
                            at: val["away"]
                        }
                    num += 1
                print(results)
                return render_template('get_results.html', week=week, results=results)  # Return the JSON response
        return render_template('get_results.html', title='Weekly Results', form=form)



    @app.route('/generate-scores', methods=['GET' ,'POST'])
    def score():
        weeks = Week.query.order_by(Week.week_number).all()  # Retrieve week numbers
        if weeks:
            week = max(week.week_number for week in weeks)

        try:
            week = int(week)  # Convert to integer if possible
        except (TypeError, ValueError):
            flash("Invalid week number provided!", category='danger')
            return redirect(url_for('get_predictions'))
            
        #Check if the selected week's score already exists
        if Score.query.filter_by(week_id=week).first():
            flash(f"Week {week} scores exist axist!")

        week_results = Result.query.filter_by(week_id=week).first()
        # Organize result into json
        results     = {"master": week_results.results}    
        # New code to convert user_predictions to a list of dictionaries
        user_predictions = Prediction.query.filter_by(week_id=week).all()  # Get all user predictions for the week

        # Compare user predictions with results and assign scores
        for prediction in user_predictions:
            user_score = prediction.user_predictions
            match_results = results["master"]  # Access the results
            user_points = 0
            print(user_points)
            for match, score in user_score.items():
                # Check if the match exists in the results
                if match in match_results:
                    # Compare scores and assign points
                    if match_results[match]["home"] == score["home"] and match_results[match]["away"] == score["away"]:
                        points = 5  # Exact match
                    elif (match_results[match]["home"] > match_results[match]["away"] and score["home"] > score["away"]) or \
                        (match_results[match]["home"] < match_results[match]["away"] and score["home"] < score["away"]) or \
                        (match_results[match]["home"] == match_results[match]["away"] and score["home"] == score["away"])  :
                        points = 3  # Correct outcome
                    else:
                        points = 0  # No points

                    user_points += points

            final_user_score = Score(
                week_id = week,
                user_id = prediction.user_id,
                points = user_points
            )
            db.session.add(final_user_score)
            db.session.commit()
            user_points = 0       
        flash(f"Scores for Week {week} computed and saved successfully!", "success")
        return redirect(url_for('home'))



    @app.route('/leaderboard', methods=['GET', 'POST'])
    #@login_required
    def leaderboard():
        scores = {}
        user_data = User.query.all()
        for user in user_data:
            score = 0
            user_score = Score.query.filter_by(user_id=user.id).all()
            for sc in user_score:
                score += sc.points
                scores[user.name] = {user.username: score}
            print(f"{user.name}: {score}")
            score = 0
        #print(scores)
        sorted_scores = dict(sorted(scores.items(), key=lambda item: list(item[1].values())[0], reverse=True))
        return render_template('leaderboard.html', scores=sorted_scores)



    @app.route('/admin-dashboard', methods=['get', 'post'])
    def admin():
        users = User.query.order_by(User.id).all()
        # New code to get table names
        inspector = inspect(db.engine)  # Create an inspector object
        table_names = inspector.get_table_names()  # Get the list of table names
        return render_template('admin_panel.html', title='Admin Panel', users=users, tables=table_names)



    @app.route('/toggle_role/<int:user_id>', methods=['POST'])
    def toggle_role(user_id):
        user = User.query.get_or_404(user_id)
        is_admin = request.form.get('is_admin')  # 'on' if checked, None if unchecked
        if is_admin:  # If the checkbox is checked, set is_admin to True
            user.is_admin = True
        else:  # If the checkbox is unchecked, set is_admin to False
            user.is_admin = False
        db.session.commit()
        return redirect(url_for('admin'))



    @app.route('/databases', methods=['get', 'post'])
    def database():
        users = User.query.all()
        
        # New code to get table names
        inspector = inspect(db.engine)  # Create an inspector object
        table_names = inspector.get_table_names()  # Get the list of table names
        for t in table_names:
            print(t)
        return render_template('admin_panel.html', title='Admin Panel', users=users, tables=table_names)  # Pass table names to the template



    @app.route('/clear-table', methods=['get', 'post'])
    def clear_table():
        # Get the table name from the query parameters
        table_name = request.args.get('table_name')  # Get the table name from the href link
        if table_name and table_name in db.Model.metadata.tables:
            # Delete all records from the specified table
            db.session.query(db.Model.metadata.tables[table_name]).delete()
            db.session.commit()  # Commit the changes to the database
            flash(f"All records from the table '{table_name}' have been deleted.", 'success')
        else:
            flash(f"Table '{table_name}' does not exist.", 'danger')
        return redirect(url_for('admin'))  # Redirect back to the admin page



    @app.route('/drop-table', methods=['get', 'post'])
    def drop_table():
        table_name = request.args.get('table_name')  # Get the table name from the query parameters
        
        if table_name:
            try:
                # Use raw SQL to drop the table
                db.session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))  # Removed CASCADE
                db.session.commit()  # Commit the changes to the database
                flash(f'Table {table_name} dropped successfully.', 'success')
            except Exception as e:
                flash(f'Error dropping table {table_name}: {str(e)}', 'danger')
        return redirect(url_for('admin'))  # Redirect to the admin panel or appropriate page



    @app.route('/drop-table', methods=['get', 'post'])
    def clear_weeks():
        # Delete all records from the Week table
        db.session.query(Week).delete()
        db.session.commit()  # Commit the changes to the database
        flash("All records from the Week table have been deleted.", 'success')
        return redirect(url_for('home'))  # Redirect back to the admin page


    @app.route('/create-bulk-accounts')
    def create_accounts():
        users = accounts
        for user in users:
            name = user['full_name']
            username = user['email']
            nickname = user['nickname']
            password = user['password']
            if not User.query.filter_by(username=username).first():
                new_user = User(
                    name=name,
                    username=username,
                    nickname=nickname,
                    password=password
                )
                db.session.add(new_user)
                db.session.commit()
            flash(f'User {username} exists!', 'danger')
        flash("Completed", 'success')
        return redirect(url_for('admin'))


    @app.route('/edit-account', methods=['get', 'post'])
    def edit_account():
        form = EditUserForm()
        user_id = request.args.get('user_id')

        # Fetch the user by ID
        user = User.query.filter_by(id=user_id).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('admin_panel'))  # Redirect to an appropriate page

        if request.method == 'GET':
            form.name.data = user.name
            form.username.data = user.username
            form.nickname.data = user.nickname
        
        # Handle form submission
        if form.validate_on_submit():
            user.name = form.name.data
            user.username = form.username.data
            user.nickname = form.nickname.data

            try:
                db.session.commit()  # Save changes to the database
                flash(f"User account updated successfully.", "success")
                return redirect(url_for('admin'))  # Redirect to a user list or appropriate page
            except Exception as e:
                db.session.rollback()  # Rollback if there's an error
                flash(f"An error occurred {e}.", "danger")
            
        return render_template('edit_user.html', form=form)
    

    @app.route('/reset-password', methods=['get', 'post'])
    def reset_password():
        form = PasswordForm()
        user_id = request.args.get('user_id')
        
        user = User.query.filter_by(id=user_id).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('admin'))

        if request.method == 'GET':
            form.name.data = user.name

        if form.validate_on_submit():
            user.password = generate_password_hash(password=form.password.data, method='scrypt', salt_length=8)
            try:
                db.session.commit()
                flash("Password reset successfully.", "success")
                return redirect(url_for('admin'))  # Redirect to a user list or appropriate page
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}.", "danger")
                return redirect(url_for('admin'))
        return render_template('admin_panel.html', title='Admin Panel', form=form)
                



    @app.route('/delete-account', methods=['get', 'post'])
    def delete_account():
        user_id = request.args.get('user_id')

        # Fetch the user by ID
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('admin_panel'))  # Redirect to an appropriate page
        name = user.nickname

        if user.id == 1 or user.is_admin:
            flash(f"Admin account can NOT be deleted!", 'danger')
            return redirect(url_for('admin'))
        db.session.delete(user)
        db.session.commit()
        flash(f"User account for {name} deleted!", 'success')

        return redirect(url_for('admin'))






