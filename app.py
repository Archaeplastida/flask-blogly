"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, check_if_users_post
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thisisacoolproject1000'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/') #Root to homepage redirection route
def redirect_to_user_page():
    return redirect('/users')

@app.route('/users') #The main page
def user_list():
    """Shows list of users and a form to add a new user."""
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/users/<int:user_id>') #User details
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter(Post.user_id == user_id).all()
    return render_template("user_details.html", user=user, posts=posts)

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>') #Shows the post in more detail
def show_post(user_id, post_id, post_title):
    user = User.query.get_or_404(user_id)
    post = Post.query.get_or_404(post_id)

    if check_if_users_post(user_id=user_id, post_id=post_id):
        post_creation_date = datetime.strftime(post.created_at, "%A, %B %d, %Y, %I:%M %p")
        return render_template('user_post_page.html', user=user, post=post, creation_date=post_creation_date)
    return redirect('/users')

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>', methods=['POST'])
def action_to_post(user_id, post_id, post_title):
    if request.form['ACTION'] == 'edit':
        return redirect(f'/users/{user_id}/post/{post_id}/{post_title}/edit')
    elif request.form['ACTION'] == 'delete':
        Post.query.filter_by(id = post_id).delete()
        db.session.commit()
        return redirect(f'/users/{user_id}')
    else:
        return redirect('/users')

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>/edit')
def edit_post(user_id, post_id, post_title):
    user = User.query.get_or_404(user_id)
    post = Post.query.get_or_404(post_id)
    if check_if_users_post(user_id=user_id, post_id=post_id):
        return render_template("user_post_editting_page.html", user=user,post=post)
    return redirect("/users")

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>/edit', methods=['POST'])
def apply_form_changes(user_id, post_id, post_title):
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    editting_post = Post.query.get_or_404(post_id)

    if title:
        editting_post.title = title
        editting_post.content = content
    else:
        editting_post.title = 'Untitled Post'
        editting_post.content = content

    db.session.add(editting_post)
    db.session.commit()

    return redirect(f'/users/{user_id}/post/{post_id}/{editting_post.title}')


@app.route('/users/<int:user_id>', methods=['POST']) #User action: edit/delete/new_post
def action_to_user(user_id):
    if request.form["ACTION"] == 'edit':
        return redirect(f'/users/{user_id}/edit')
    elif request.form["ACTION"] == 'delete':
        User.query.filter_by(id = user_id).delete()
        db.session.commit()
        return redirect('/users')
    elif request.form["ACTION"] == 'new-post':
        return redirect(f'/users/{user_id}/new-post')
    else:
        return redirect('/users')

@app.route('/users/<int:user_id>/edit') #User editting page
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_edit.html', user=user)

@app.route('/users/<int:user_id>/new-post') #NEW POST creation page
def new_post_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_post_creation_page.html', user=user)

@app.route('/users/<int:user_id>/new-post', methods=['POST']) #Creation of new post
def submit_post(user_id):
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    post = None
    
    if title:
        post = Post(title=title, content=content, user_id=user_id)
    else:
        post = Post(content=content, user_id=user_id)

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{user_id}/post/{post.id}/{post.title}')


#Make a route to show the post and its contents

@app.route('/users/<int:user_id>/edit', methods=['POST']) #Application of user profile edits
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

    return redirect(f'/users/{user_id}')

@app.route('/users', methods=['POST']) #Creation of new user
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

    return redirect(f'/users/{new_user.id}')