from flask import Flask, render_template_string, redirect, render_template
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user, AnonymousUserMixin
from flask_blogging import SQLAStorage, BloggingEngine

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = ""
app.config["BLOGGING_DISQUS_SITENAME"] = None
app.config["BLOGGING_SITENAME"] = 'This is the site name!!!'
app.config["BLOGGING_SITEURL"] = "http://localhost:1177"

# extensions
engine = create_engine('sqlite:////tmp/blog.db')
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)


# user class for providing authentication
class User(UserMixin):
    def __init__(self, name, email):
        self.id = name
        self.name = name
        self.email = email

    def get_name(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


class Guest(AnonymousUserMixin):
    pass


@login_manager.user_loader
@blog_engine.user_loader
def load_user(user_id):
    return User("izrik", "izrik@izrik.com")


# @app.route("/")
# def index():
#     return render_template("index.html")


@app.route("/login/")
def login():
    user = User("izrik", "izrik@izrik.com")
    login_user(user)
    return redirect("/")


@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=1177, use_reloader=True)
