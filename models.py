"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    first_name = db.Column(db.String,
                           nullable=False)
    
    last_name = db.Column(db.String,
                          nullable=False)
    
    image_url = db.Column(db.String,
                          nullable=False,
                          default='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    title = db.Column(db.String,
                      nullable=False,
                      default='Untitled Post')
    
    content = db.Column(db.String)

    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=db.func.now())

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id',
                                      ondelete='CASCADE'),
                        nullable=False)
    
    user = db.relationship('User', backref='posts')

    tags = db.relationship('Tag', secondary='post_tags', backref='posts')

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    name = db.Column(db.String,
                     nullable=False,
                     unique=True)
    
   

class Post_Tag(db.Model):
    __tablename__ = 'post_tags'
    
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete='CASCADE'), primary_key=True)
    
    tag_id = db.Column(db.Integer, db.ForeignKey(
        'tags.id', ondelete='CASCADE'), primary_key=True)


def check_if_users_post(user_id=int, post_id=int):
    posts = User.query.get_or_404(user_id).posts
    for post in posts:
        if post.id == post_id:
            return True
    return False

def tag_in_posts_by_ids(tag_id, post_id):
    posts_with_tag = Tag.query.get(tag_id).posts
    for x in posts_with_tag:
        if x.id == post_id:
            return True
    return False