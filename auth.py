from flask import Blueprint, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from extensions import db
from models import User, UserRole
import os

auth = Blueprint('auth', __name__)
oauth = OAuth()

admin_emails = ['leer17@kgv.hk']
teacher_emails = []

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@auth.route('/login')
def login():
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
@auth.route('/auth/callback')
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token['userinfo']
    user = User.query.filter_by(google_sub_id=user_info['sub']).first()
    if user_info['email'][user_info['email'].find('@')+1:] != "kgv.hk":
        return redirect(url_for('reject')) 
    if  user is None:
        user = User(
        google_sub_id=user_info['sub'],
        name=user_info['name'],
        email=user_info['email']
        )
    if user_info['name'].find('[') != -1:
        user.year_group = int(user_info['name'][user_info['name'].find('[')+1:user_info['name'].find('[')+3])
    if user_info['email'] in admin_emails:
        user.role = UserRole.ADMIN
    elif user_info['email'] in teacher_emails:
        user.role = UserRole.TEACHER
    else:
        user.role = UserRole.STUDENT
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('index')) 


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))