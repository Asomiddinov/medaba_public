from enum import unique
import logging
from msilib import init_database
import pandas as pd
from flask_moment import Moment
import os
from flask import Flask, flash, redirect, render_template, request, json, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
import uuid as uuid

app = Flask(__name__)
# Adding CKEditor:
ckeditor = CKEditor(app)
CORS(app)
moment = Moment(app)
# Secret Key:
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Adding db:
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# New db:
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://sxojerlmbjeaon:08f31c564ecffc408a895cac1ebb4e63dfb7e7d650e912531cdec293985242dd@ec2-3-219-19-205.compute-1.amazonaws.com:5432/d241dubbcsh3b5'
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Initialize the DB:
db = SQLAlchemy(app)
migrate = Migrate(app, db)
boot = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class Users(db.Model, UserMixin):  # Create Model:
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    e = db.Column(db.String(120), nullable=False, unique=True)
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now())
    # Password staff:
    password_hash = db.Column(db.String(128))
    # Adding profile_pic to db.:
    profile_pic = db.Column(db.String(), nullable=True)
    # User can have many posts:
    posts = db.relationship("Posts", backref="poster")

    @property
    def password(self):
        raise AttributeError("password'ingiz bu emas!!!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):  # Create string:
        return "<Name %r>" % self.name


class Posts(db.Model):  # Creating Blog Post:
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255))
    # Foreign Key to link Users(refer too primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))


def create_app():
    app = Flask(__name__)
    with app.app_context():
        init_database()
    return app


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])  # Login Page:
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Checing the hash:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("👋🏻👋🏻👋🏻")
                return redirect(url_for("dashboard"))
            else:
                flash(
                    "Password yoki Login xato! Qayta urining yoki Admin'ga murojaat qiling!")
        else:
            flash("Bunaqa User topilmadi. Qayta urining!")
    return render_template("login.html", form=form)


@app.route("/dashboard", methods=["GET", "POST"])  # Dashboard Page:
def dashboard():
    form = UserForm()
    return render_template("dashboard.html", form=form)


@app.route("/logout", methods=["GET", "POST"])  # Logout Page:
def logout():
    logout_user()
    flash("Siz profile'dan chiqdingiz!")
    return redirect(url_for("login"))


@app.route("/date")  # JSON:
def current_date():
    services = {
        "Vrach1": "Uzi",
        "Vrach2": "MSCI"
    }
    f"<h1>Bugun: {datetime.now()}<h1>"
    return f"<h1>Bugun: {datetime.now()}<h1>"  # services
    # return


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registration', methods=["GET", "POST"])  # Registration page:
def reg():
    return render_template('reg.html')


@app.route('/regtable', methods=["POST"])  # Regtable page:
def regtable():
    sana = datetime.now()
    full_name = request.form.get("full_name")
    adress = request.form.get("adress")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    recommender = request.form.get("recommender")
    service = request.form.get("service")
    price = request.form.get("price")
    # Code for Barcode:
    mybar = str(sana.strftime("%Y%m%d%H%M%S"))
    # Hali bu yerga qo'shiladiganlari bor >>>
    return render_template('regtable.html',
                           mybar=mybar,
                           sana=sana,
                           full_name=full_name,
                           adress=adress,
                           phone=phone,
                           gender=gender,
                           recommender=recommender,
                           service=service,
                           price=price)


@app.route("/settings")  # Settings:
def settings():
    return render_template("settings.html")


# @login_required
@app.route("/user/add", methods=["GET", "POST"])  # Add User to database:
def add_user():
    # id = current_user.id
    # if id:
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashed Password:
            hashed_pw = generate_password_hash(
                form.password_hash.data, "sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         about_author=form.about_author.data, e=form.e.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.e.data = ""
        form.about_author.data = ""
        form.password_hash = ""
        flash("User Muvaffaqiyatli qo'shildi!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form, name=name, our_users=our_users)
    # else:
    #     flash("⛔⛔⛔❌❌❌")
    #     return redirect(url_for("dashboard"))


# Update Database Record of users:
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        # name_to_update.e = request.form["e"]
        name_to_update.about_author = request.form["about_author"]
        name_to_update.username = request.form["username"]
        name_to_update.profile_pic = request.files["profile_pic"]
        # Grab image name:
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set uuid:
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save that image:
        saver = request.files["profile_pic"]
        # Change it to a string to save to db:
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            saver.profile_pic.save(os.path.join(
                app.config["UPLOAD_FOLDER"]), pic_name)
            flash("Done!")
            logging.info("User muvaffaqiyatli qo'shildi!!!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Xatolik! Qayta urinib ko'ring!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route("/delete/<int:id>")  # Delete User from  database:
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        "<p>User muvaffaqiyatli o'chirildi!</p>"
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    except:
        "<p>Voy! O'chirish qismida muammo kuzatildi, qayta urinib ko'ring..!</p>"
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)


@app.route("/prices", methods=["GET", "POST"])  # Prices page:
def prices():
    # upl = request.form.get("upl")
    # data = pd.read_excel(upl)
    if request.method == "POST":
        a = request.form
        return render_template("prices.html", a == a)


@app.context_processor  # Pass stuff to Navbar: CONTEXT_PROCESSOR???
def base():
    form = SearchForm()
    return dict(form=form)


@app.route("/search", methods=["POST"])  # Search function:
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like("%" + post.searched + "%"))
        # posts = posts.filter(Posts.id.like("%" + post.searched + "%"))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Success! Muvaffaqiyat! Успех!")
    return render_template("name.html", name=name, form=form)


@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form:
        form.email.data = ""
        form.password_hash.data = ""
        # Lookup User by Email:
        pw_to_check = Users.query.filter_by(email=email).first()
        # Chek Hashed Password:
        passed = check_password_hash(pw_to_check.password_hash, password)
        flash("Success! Muvaffaqiyat! Успех!")
    return render_template("test_pw.html", email=email, password=password,
                           pw_to_check=pw_to_check, passed=passed, form=form)


@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data,
                     poster_id=poster, slug=form.slug.data)
        # Clearing the form:
        form.title.data = ""
        form.content.data = ""
        # form.author.data = ""
        form.slug.data = ""
        # Adding post data to db:
        db.session.add(post)
        db.session.commit()
        flash("Success! Muvaffaqiyat! Успех!")
    return render_template("add_post.html", form=form)


@app.route("/posts")
# @login_required
def posts():
    # Grab all the posts from the db:
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update db:
        db.session.add(post)
        db.session.commit()
        flash("Success! Muvaffaqiyat! Успех!")
        return redirect(url_for("post", id=post.id))
    if current_user.id == post.poster_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("You can't edit others' posts!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("!!!")
            # Grab all the posts from the db:
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            flash("Xatolik! Qayta urinib ko'ring!!! ☹")
            # Grab all the posts from the db:
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("You can't delete others' posts!!!")
        # Grab all the posts from the db:
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.errorhandler(404)  # Invalid URL
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)  # Internal server Error
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=1)
