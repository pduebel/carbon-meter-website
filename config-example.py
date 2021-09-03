from werkzeug.security import generate_password_hash

# dict of users, change 'username' and 'password' to desired
# username and password for site
users = { 'username': generate_password_hash('password')}