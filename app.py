"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, Post_Tag, check_if_users_post, tag_in_posts_by_ids
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
    tags = post.tags

    if check_if_users_post(user_id=user_id, post_id=post_id):
        post_creation_date = datetime.strftime(post.created_at, "%A, %B %d, %Y, %I:%M %p")
        return render_template('user_post_page.html', user=user, post=post, creation_date=post_creation_date, tags=tags)
    return redirect('/users')

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>', methods=['POST']) #Edit/Delete action
def action_to_post(user_id, post_id, post_title):
    if request.form['ACTION'] == 'edit':
        return redirect(f'/users/{user_id}/post/{post_id}/{post_title}/edit')
    elif request.form['ACTION'] == 'delete':
        Post.query.filter_by(id = post_id).delete()
        db.session.commit()
        return redirect(f'/users/{user_id}')
    else:
        return redirect('/users')

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>/edit') #Post editting page
def edit_post(user_id, post_id, post_title):
    user = User.query.get_or_404(user_id)
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    checked_tags = []
        
    if check_if_users_post(user_id=user_id, post_id=post_id):
        for tag in tags:
            if tag_in_posts_by_ids(tag_id=tag.id, post_id=post_id):
                checked_tags.append(tag.id)
        return render_template("user_post_editting_page.html", user=user,post=post, tags=tags, checked_tags=checked_tags)
    return redirect("/users")

@app.route('/users/<int:user_id>/post/<int:post_id>/<post_title>/edit', methods=['POST']) #Application of the post, content, tag and title changes
def apply_form_changes(user_id, post_id, post_title):
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    editting_post = Post.query.get_or_404(post_id)
    editting_post.tags.clear()
    tags = request.form.getlist('tag')

    if title:
        editting_post.title = title
        editting_post.content = content
    else:
        editting_post.title = 'Untitled Post'
        editting_post.content = content

    db.session.add(editting_post)
    db.session.commit()

    if tags:
        for x in tags:
            new_tag = Tag.query.filter(Tag.name == x).first()
            editting_post.tags.append(new_tag)

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
    tags = Tag.query.all()
    return render_template('user_post_creation_page.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/new-post', methods=['POST']) #Creation of new post
def submit_post(user_id):
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    tags = request.form.getlist('tag')
    post = None
    
    if title:
        post = Post(title=title, content=content, user_id=user_id)
    else:
        post = Post(content=content, user_id=user_id)

    db.session.add(post)
    db.session.commit()

    if tags:
        for x in tags:
            new_tag = Tag.query.filter(Tag.name == x).first()
            post.tags.append(new_tag)

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

    if image_url:
        new_user = User(first_name=first_name,last_name=last_name,image_url=image_url)
    else:
        new_user = User(first_name=first_name,last_name=last_name)
    
    db.session.add(new_user)
    db.session.commit()

    return redirect(f'/users/{new_user.id}')

@app.route('/tags') #The tags page
def tag_list():
    tags = Tag.query.all()
    return render_template('tag_list.html', tags=tags)

@app.route('/tags/<int:tag_id>') #Tag details page
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts
    return render_template('tag_details.html', tag=tag, posts=posts)

@app.route('/tags', methods=['POST']) #Creation of new tag
def create_tag():
    tag_name = request.form["tag_name"].strip()
    if tag_name and not Tag.query.filter(Tag.name == tag_name).all():
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(f'/tags/{new_tag.id}')

    return redirect('/tags')
    
@app.route('/tags/<int:tag_id>', methods=['POST']) #Edit/Delete action
def action_to_tag(tag_id):
     if request.form["ACTION"] == 'edit':
        return redirect(f'/tags/{tag_id}/edit')
     elif request.form["ACTION"] == 'delete':
        Tag.query.filter_by(id = tag_id).delete()
        db.session.commit()
        return redirect('/tags')
     else:
        return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit') #Tag editting page
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_edit.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=['POST']) #Application of changes to the tag
def apply_tag_changes(tag_id):
    editted_tag_name = request.form['tag_name'].strip()
    if editted_tag_name:
        editted_tag = Tag.query.get_or_404(tag_id)
        editted_tag.name = editted_tag_name
        db.session.add(editted_tag)
        db.session.commit()
        return redirect(f'/tags/{tag_id}')
    return redirect('/tags/<int:tag_id>/edit')