from flask import Blueprint, redirect, url_for, session, request, abort
from flask_login import LoginManager, login_required, logout_user, login_user
from urllib.parse import urljoin, urlparse
from authlib.integrations.flask_client import OAuth
from extensions import db
from models import User, UserRole
from functools import wraps #decorator useful for creating decorator 
from sqlalchemy import select
import os
from datetime import datetime


auth = Blueprint('auth', __name__)
oauth = OAuth()
login_manager = LoginManager()

admin_emails = ['leer17@kgv.hk']
teacher_emails = []



google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    created = datetime.now()
)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# def login_required(f): 
#     """Checks if user is logged in"""
#     @wraps(f) #copies metadata from f to decorated_function
#     def decorated_function(*args, **kwargs): 
#         #this is a wrapper function and it's needed or else this check would 
#         # run everytime we decorate a function, not when we call the base function
#         if session.get('user_id') is None:
#             return redirect(url_for('index'))
#         return f(*args, **kwargs)
#     return decorated_function #we return decorated function so that we can run the base function

@auth.route('/login') #'auth' here specifies that this route belongs to the module auth
def login():
    next_url = request.args.get("state")
    if next_url and is_safe_url(next_url):
        session['next_url'] = next_url
    redirect_uri = url_for('auth.callback', _external=True) #sends user to the google login page via the callback function here
    return oauth.google.authorize_redirect(redirect_uri) #generates Google's authorization url

def is_safe_url(target): #checks if url is safe ~ copied from online
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
    ) 

@auth.route('/auth/callback') #where Google sends user back to on our site after login
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token['userinfo'] #extracts the authenticated user's profile information
    user = db.session.execute(select(User).where(User.google_sub_id == user_info['sub'])).scalar() 
    #sets the var user to the User in db where their google id matches the currently logged in google id
    if user_info['email'][user_info['email'].find('@')+1:] != "kgv.hk": #if used logged in with not kgv domain email
        return redirect(url_for('reject')) 
    if  user is None: #if user doesn't already exist, create new record in db
        user = User(
        google_sub_id=user_info['sub'],
        name=user_info['name'],
        email=user_info['email'],
        created = datetime.now()
        )
    if user_info['name'].find('[') != -1: #extracts the user's year group from the name cuz KGV has this format
        user.year_group = int(user_info['name'][user_info['name'].find('[')+1:user_info['name'].find('[')+3])
    if user_info['email'] in admin_emails: #if the user email is a recorded admin email
        user.role = UserRole.ADMIN
    elif user_info['email'] in teacher_emails: 
        user.role = UserRole.TEACHER
    else:
        user.role = UserRole.STUDENT
    db.session.add(user) #stages the new user record
    db.session.commit() #commits the new user record
    # session['user_id'] = user.id #stores the current user id in cookies to keep logged in during this session
    login_user(user)
    print("'Logged in successfully.'")
    next_url = session.pop('next_url', None)
    print(f"DEBUG: Redirecting to -> {next_url}")
    if next_url and is_safe_url(next_url): #prevents open redirect attack
        return redirect(next_url) #redirects user either to where they were going before login or home page
    return redirect(url_for('index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))