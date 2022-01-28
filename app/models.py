from app import db, login
from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

##### Import db and create users #####
# >>> from app import db
# >>> from app.models import User, Post
# >>> u = User(username='Keb', email='keb1@gmail.com')
# >>> db.session.add(u)
# >>> db.session.commit()
# >>> u = User(username='Test', email='test@gmail.com')
# >>> db.session.add(u)
# >>> db.session.commit()
# >>> users = User.query.all()
# >>> users
# [<User Keb>, <User Test>]
# >>> for u in users:
# ...     print(u.id, u.username, u.email)
# ...
# 1 Keb keb1@gmail.com
# 2 Test test@gmail.com
# >>> u = User.query.get(1)
# >>> u
# <User Keb>

##### Make a post #####
# >>> p = Post(body='First!', author=u)
# >>> db.session.add(p)
# >>> db.session.commit()
# >>> u.posts.all()
# [<Post: First!>]
# >>> u = User.query.get(2)
# >>> u.posts.all()
# []
# >>> posts = Post.query.all()
# >>> for p in posts:
# ...     print(p.id, p.author.username)
# ...
# 1 Keb
# >>> User.query.order_by(User.username.desc()).all()
# [<User Test>, <User Keb>]
# >>> # Query users sorted by username descending

##### Wipe DB #####
# >>> users = User.query.all()
# >>> for u in users:
# ...     db.session.delete(u)
# ...
# >>> posts = Post.query.all()
# >>> for p in posts:
# ...     db.session.delete(p)
# ...
# >>> db.session.commit()

#### USER FOLLOWING ####
# >>> user1 = User.query.get(1)
# >>> user2 = User.query.get(2)
# >>>
# >>> user1
# <User Kev>
# >>> user2
# <User keving>
# >>> user1.followed.append(user2)
# >>> db.session.commit
# <bound method commit of <sqlalchemy.orm.scoping.scoped_session object at 0x0000020D7F102910>>
# >>> db.session.commit()
# >>> user1.followed.all()
# [<User keving>]
# >>> user1.followed.remove(user2)
# >>> db.session.commit()
# >>> user1.followed.all()

followers = db.Table(
	'followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
			followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc()) # combine user's own posts w/ followers

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post: {}>'.format(self.body)