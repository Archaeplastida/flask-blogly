"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thisisacoolproject1000'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def redirect_to_user_page():
    return redirect('/user')

@app.route('/user')
def user_list():
    """Shows list of users and a form to add a new user."""
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("user_details.html", user=user)

@app.route('/user/<int:user_id>', methods=['POST'])
def action_to_user(user_id):
    if request.form["ACTION"] == 'edit':
        return redirect(f'/user/{user_id}/edit')
    elif request.form["ACTION"] == 'delete':
        User.query.filter_by(id = user_id).delete()
        db.session.commit()
        return redirect('/user')
    else:
        return redirect('/user')

@app.route('/user/<int:user_id>/edit')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_edit.html', user=user)

@app.route('/user/<int:user_id>/edit', methods=['POST'])
def apply_user_changes(user_id):
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]

    editted_user = User.query.get_or_404(user_id)

    editted_user.first_name = first_name
    editted_user.last_name = last_name
    editted_user.image_url = image_url

    db.session.add(editted_user)
    db.session.commit()

    return redirect(f'/user/{user_id}')

@app.route('/user', methods=['POST'])
def create_user():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]
    new_user = None

    if not image_url:
        new_user = User(first_name=first_name,last_name=last_name)
    else:
        new_user = User(first_name=first_name,last_name=last_name,image_url=image_url)

    
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/user/{new_user.id}')