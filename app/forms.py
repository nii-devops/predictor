from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError




teams = ['ARS', 'AST', 'BOU', 'BRE', 'BRI', 'CHE', 'CRY', 'EVE', 'FUL', 'IPS',
         'LEI', 'LIV', 'MNC', 'MNU', 'NEW', 'NFO', 'SOU', 'TOT', 'WES', 'WOL']

weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 
         25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]


epl_teams = (
    #('---', "---"), 
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
    picture     = FileField('Upload Profile Picture (Optional)', render_kw={"placeholder": "Optional"})
    submit      = SubmitField('Submit')


class PredictResultWeekForm(FlaskForm):
    week = IntegerField('Week Number', validators=[DataRequired()])
    submit = SubmitField('Submit')


class NameForm(FlaskForm):
    name        = StringField('Name', validators=[DataRequired()])#, render_kw=[{"Placeholder": "e.g. DannyBoy"}])
    email       = StringField('Email', validators=[DataRequired()])
    submit      = SubmitField('Submit')


class UserEmailForm(FlaskForm):
    email       = EmailField('Email Address', validators=[Email()])  # Add your weeks here
    submit      = SubmitField('Submit')


class UserPredictionForm(FlaskForm):
    week        = SelectField('Game Week', validators=[DataRequired()], coerce=int)    
    email       = EmailField('Email Address', validators=[Email()])  # Add your weeks here
    submit      = SubmitField('Submit')


class SelectWeekForm(FlaskForm):
    week        = SelectField('Select Week', choices=weeks)  # Add your weeks here
    submit      = SubmitField('Submit')


class ScoreWeekForm(FlaskForm):
    week        = SelectField('Game Week', validators=[DataRequired()], coerce=int)   
    submit      = SubmitField('Submit')


class PredictionWeekForm(FlaskForm):
    week        = SelectField('Select Week', choices=weeks)  # Add your weeks here
    submit      = SubmitField('Submit')


class LoginForm(FlaskForm):
    username    = EmailField('Email', validators=[DataRequired()])
    password    = PasswordField('Password', validators=[DataRequired()])
    submit      = SubmitField('Signin')



class RegisterForm(FlaskForm):
    name        = StringField('Full Name', validators=[DataRequired()])
    nickname    = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "e.g. Oboy Siki"})
    username    = EmailField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    password_2  = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit      = SubmitField('Signup')



class EditUserForm(FlaskForm):
    name        = StringField('Full Name', validators=[DataRequired()])
    nickname    = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "e.g. Oboy Siki"})
    username    = EmailField('Email', validators=[DataRequired(), Email()])
    submit      = SubmitField('Update')


class PasswordForm(FlaskForm):
    name        = StringField('Full Name', validators=[DataRequired()])
    password    = PasswordField('Password', validators=[DataRequired()])
    password_2  = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit      = SubmitField('Reset')



class FixtureForm(FlaskForm):
    teams = epl_teams

    # def (form, field):
    #     if field.data not in teams:
    #         raise ValidationError('Team name must be a alphanumeric string.')
        
        
    game_week = IntegerField('Game Week', validators=[DataRequired()], render_kw={'readonly': True})

    home_1 = SelectField('Match 1 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 1')] + list(teams), render_kw={"placeholder": "Home 1"})
    away_1 = SelectField('Match 1 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 1')] + list(teams), render_kw={"placeholder": "Away 1"})
    
    home_2 = SelectField('Match 2 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 2')] + list(teams))
    away_2 = SelectField('Match 2 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 2')] + list(teams))
    
    home_3 = SelectField('Match 3 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 3')] + list(teams))
    away_3 = SelectField('Match 3 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 3')] + list(teams))

    home_4 = SelectField('Match 4 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 4')] + list(teams))
    away_4 = SelectField('Match 4 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 4')] + list(teams))

    home_5 = SelectField('Match 5 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 5')] + list(teams))
    away_5 = SelectField('Match 5 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 5')] + list(teams))

    home_6 = SelectField('Match 6 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 6')] + list(teams))
    away_6 = SelectField('Match 6 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 6')] + list(teams))

    home_7 = SelectField('Match 7 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 7')] + list(teams))
    away_7 = SelectField('Match 7 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 7')] + list(teams))

    home_8 = SelectField('Match 8 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 8')] + list(teams))
    away_8 = SelectField('Match 8 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 8')] + list(teams))

    home_9 = SelectField('Match 9 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 9')] + list(teams))
    away_9 = SelectField('Match 9 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 9')] + list(teams))

    home_10 = SelectField('Match 10 Home Team', validators=[DataRequired()], choices=[('---', 'Home Team 10')] + list(teams))
    away_10 = SelectField('Match 10 Away Team', validators=[DataRequired()], choices=[('---', 'Away Team 10')] + list(teams))

    submit  = SubmitField('Submit')



class PredictionForm(FlaskForm):
    #game_week = SelectField('Game Week', validators=[DataRequired()], coerce=int)  # Expect an integer value
    def validate_positive_score(form, field):
        if (field.data is not None and field.data < 0) or field.data is None:
            raise ValidationError('Score must be a positive integer.')

    game_week = IntegerField('Game Week', validators=[DataRequired()])    

    home_1 = StringField('Match 1 Home Team', validators=[DataRequired()])
    home_1_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_1 = StringField('Match 1 Away Team', validators=[DataRequired()])
    away_1_score = IntegerField('Away Score', validators=[validate_positive_score])
    
    home_2 = StringField('Match 2 Home Team', validators=[DataRequired()])
    home_2_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_2 = StringField('Match 2 Away Team', validators=[DataRequired()])
    away_2_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_3 = StringField('Match 3 Home Team', validators=[DataRequired()])
    home_3_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_3 = StringField('Match 3 Away Team', validators=[DataRequired()])
    away_3_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_4 = StringField('Match 4 Home Team', validators=[DataRequired()])
    home_4_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_4 = StringField('Match 4 Away Team', validators=[DataRequired()])
    away_4_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_5 = StringField('Match 5 Home Team', validators=[DataRequired()])
    home_5_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_5 = StringField('Match 5 Away Team', validators=[DataRequired()])
    away_5_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_6 = StringField('Match 6 Home Team', validators=[DataRequired()])
    home_6_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_6 = StringField('Match 6 Away Team', validators=[DataRequired()])
    away_6_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_7 = StringField('Match 7 Home Team', validators=[DataRequired()])
    home_7_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_7 = StringField('Match 7 Away Team', validators=[DataRequired()])
    away_7_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_8 = StringField('Match 8 Home Team', validators=[DataRequired()])
    home_8_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_8 = StringField('Match 8 Away Team', validators=[DataRequired()])
    away_8_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_9 = StringField('Match 9 Home Team', validators=[DataRequired()])
    home_9_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_9 = StringField('Match 9 Away Team', validators=[DataRequired()])
    away_9_score = IntegerField('Away Score', validators=[validate_positive_score])

    home_10 = StringField('Match 10 Home Team', validators=[DataRequired()])
    home_10_score = IntegerField('Home Score', validators=[validate_positive_score])
    away_10 = StringField('Match 10 Away Team', validators=[DataRequired()])
    away_10_score = IntegerField('Away Score', validators=[validate_positive_score])

    submit = SubmitField('Submit')

    

class ResultsForm(FlaskForm):
    def validate_positive_score(form, field):
        if (field.data is not None and field.data < 0) or field.data is None:
            raise ValidationError('Score must be a positive integer.')

    game_week = IntegerField('Game Week', validators=[DataRequired()])    

    home_1 = StringField('Match 1 Home Team', validators=[DataRequired()])
    home_1_score = IntegerField('Home Score')
    away_1 = StringField('Match 1 Away Team', validators=[DataRequired()])
    away_1_score = IntegerField('Away Score')
    
    home_2 = StringField('Match 2 Home Team', validators=[DataRequired()])
    home_2_score = IntegerField('Home Score')
    away_2 = StringField('Match 2 Away Team', validators=[DataRequired()])
    away_2_score = IntegerField('Away Score')

    home_3 = StringField('Match 3 Home Team', validators=[DataRequired()])
    home_3_score = IntegerField('Home Score')
    away_3 = StringField('Match 3 Away Team', validators=[DataRequired()])
    away_3_score = IntegerField('Away Score')

    home_4 = StringField('Match 4 Home Team', validators=[DataRequired()])
    home_4_score = IntegerField('Home Score')
    away_4 = StringField('Match 4 Away Team', validators=[DataRequired()])
    away_4_score = IntegerField('Away Score')

    home_5 = StringField('Match 5 Home Team', validators=[DataRequired()])
    home_5_score = IntegerField('Home Score')
    away_5 = StringField('Match 5 Away Team', validators=[DataRequired()])
    away_5_score = IntegerField('Away Score')

    home_6 = StringField('Match 6 Home Team', validators=[DataRequired()])
    home_6_score = IntegerField('Home Score')
    away_6 = StringField('Match 6 Away Team', validators=[DataRequired()])
    away_6_score = IntegerField('Away Score')

    home_7 = StringField('Match 7 Home Team', validators=[DataRequired()])
    home_7_score = IntegerField('Home Score')
    away_7 = StringField('Match 7 Away Team', validators=[DataRequired()])
    away_7_score = IntegerField('Away Score')

    home_8 = StringField('Match 8 Home Team', validators=[DataRequired()])
    home_8_score = IntegerField('Home Score')
    away_8 = StringField('Match 8 Away Team', validators=[DataRequired()])
    away_8_score = IntegerField('Away Score')

    home_9 = StringField('Match 9 Home Team', validators=[DataRequired()])
    home_9_score = IntegerField('Home Score')
    away_9 = StringField('Match 9 Away Team', validators=[DataRequired()])
    away_9_score = IntegerField('Away Score')

    home_10 = StringField('Match 10 Home Team', validators=[DataRequired()])
    home_10_score = IntegerField('Home Score')
    away_10 = StringField('Match 10 Away Team', validators=[DataRequired()])
    away_10_score = IntegerField('Away Score')

    submit = SubmitField('Submit')





