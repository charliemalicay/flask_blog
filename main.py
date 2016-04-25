from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from config import DevConfig
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from random import random, randint
from sqlalchemy import func
from flask_wtf import Form
from wtforms import StringField, TextAreaField, TextField, PasswordField, validators
from wtforms.validators import DataRequired, Length


app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)


################################MODELS##########################################
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User '{}'>".format(self.username)

tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.Text)
    publish_date = db.Column(db.DateTime())
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag '{}'>".format(self.name)

class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

class Note(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime())

    def __repr__(self):
        return "<Note '{}'>".format(self.name)

################################FORMS##########################################

class PostForm(Form):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])


class CommentForm(Form):
    name = StringField('Title', validators=[DataRequired(), Length(max=120)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])

class RegistrationForm(Form):
    username = TextField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('New Password', validators=[DataRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(
            username=self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown username')
            return False
        """
        if not user.password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        """
        self.user = user
        return True


################################SIMPLIFY VIEWS##########################################
def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).order_by('total DESC').limit(5).all()

    return recent, top_tags

################################LOGIN REQUIRED##########################################
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
################################ROUTES/VIEWS##########################################
@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template(
        'index.html',
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post("Title")
        new_post.title = form.title.data
        new_post.text = form.text.data
        new_post.publish_date = datetime.now()
        new_post.user_id = randint(1, 5)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/')

    return render_template(
        'create.html',
        form=form
    )

@app.route('/post/<int:post_id>', methods=('GET', 'POST'))
@login_required
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.now()
        db.session.add(new_comment)
        db.session.commit()

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    author = User.query.get_or_404(post.user_id)

    return render_template(
        'post.html',
        post=post,
        author=author,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form

    )

@app.route('/tag/<string:name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )

@app.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(u'Successfully logged in as %s' % form.user.username)
        session['user_id'] = form.user.id
        session['logged_in'] = True
        return redirect(url_for('home'))

    return render_template(
        'login.html',
        form=form
    )

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()