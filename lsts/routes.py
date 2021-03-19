import datetime

import jwt
from flask import render_template, flash, redirect, url_for, request, abort

from lsts import app, bcrypt, db, mail
from lsts.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    AddItemForm,
    AddListForm,
    EditListForm,
    EditItemForm,
    ResetRequestForm,
    ResetPasswordForm,
)
from lsts.models import User, ItemList, Item
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/list")
@login_required
def show_list():
    if len(User.query.get(current_user.id).lists) < 1:
        return redirect(url_for("add_list"))
    return render_template("list.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in")
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            hs_password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created, you can now log in.")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.hs_password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            if next_page:
                return redirect(next_page)

            else:
                flash("You are now logged in!")
                return redirect(url_for("home"))
        else:
            flash("Login unsuccessful, please verify info")
    return render_template("login.html", title="Register", form=form)


@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("register"))
    logout_user()
    flash("You are logged out")
    return redirect(url_for("home"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", title="Account", form=form)


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        item = Item(
            name=form.item_name.data,
            category=form.category.data,
            note=form.note.data,
            list_id=request.args.get("list_id"),
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("show_list"))
    return render_template("add_item.html", form=form, title="Add Item")


@app.route("/add_list", methods=["GET", "POST"])
@login_required
def add_list():
    form = AddListForm()
    if form.validate_on_submit():
        item_list = ItemList(name=form.list_name.data, user_id=current_user.id)
        db.session.add(item_list)
        db.session.commit()
        return redirect(url_for("show_list"))
    return render_template("add_list.html", form=form, title="Add List")


@app.route("/delete_list", methods=["GET", "POST"])
@login_required
def delete_list():
    list_id = request.args.get("list_id")
    item_list = ItemList.query.get(list_id)

    if current_user.id != item_list.user_id:
        abort(403)

    db.session.execute("pragma foreign_keys=on")
    db.session.delete(item_list)
    db.session.commit()
    flash("List deleted")
    return redirect(url_for("show_list"))


@app.route("/delete_item", methods=["GET", "POST"])
@login_required
def delete_item():
    list_id = request.args.get("list_id")
    item_list = ItemList.query.get(list_id)

    item_id = request.args.get("item_id")
    item = Item.query.get(item_id)

    if current_user.id != item_list.user_id:
        abort(403)

    db.session.execute("pragma foreign_keys=on")
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted")
    return redirect(url_for("show_list"))


@app.route("/edit_list", methods=["GET", "POST"])
@login_required
def edit_list():
    item_list = ItemList.query.get(request.args.get("list_id"))
    if current_user.id != item_list.user_id:
        abort(403)

    form = EditListForm()

    if form.validate_on_submit():
        item_list.name = form.list_name.data
        db.session.commit()
        flash("List Updated")
        return redirect(url_for("show_list"))

    elif request.method == "GET":
        form.list_name.data = item_list.name
    return render_template("edit_list.html", title="Edit List", form=form)


@app.route("/edit_item", methods=["GET", "POST"])
@login_required
def edit_item():
    item_list = ItemList.query.get(request.args.get("list_id"))
    item = Item.query.get(request.args.get("item_id"))
    if current_user.id != item_list.user_id:
        abort(403)

    form = EditItemForm()

    if form.validate_on_submit():
        item.name = form.item_name.data
        item.category = form.category.data
        item.note = form.note.data
        db.session.commit()
        flash("Item Updated")
        return redirect(url_for("show_list"))

    elif request.method == "GET":
        form.item_name.data = item.name
        form.category.data = item.category
        form.note.data = item.note
    return render_template("edit_item.html", title="Edit List", form=form)


@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user:
            msg = Message(
                "Password Reset Request",
                sender="lsts.xyz@gmail.com",
                recipients=[form.email.data],
            )

            user_info = {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            }

            token = jwt.encode(
                user_info, app.config.get("SECRET_KEY"), algorithm="HS256"
            )

            msg.body = f"""To reset your password for lsts.xyz please click on the following link:{url_for('reset_password', token=token, _external=True)}
            
            If you did not request this reset, ignore it and the reset will expire."""
            mail.send(msg)

        flash("Request Processed - Check Your Email")
        return redirect(url_for("login"))

    return render_template("reset_request.html", form=form, title="Password Reset")


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        user_info = jwt.decode(
            token, app.config.get("SECRET_KEY"), algorithms=["HS256"]
        )
        user = User.query.get(user_info.get("user_id"))

    except jwt.DecodeError:
        flash("Error - Invalid Token")
        return redirect(url_for("home"))

    except jwt.ExpiredSignatureError:
        flash("Error - Token Expired")
        return redirect(url_for("home"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.hs_password = hashed_password
        db.session.commit()
        flash(f"Password Reset Successful")

        return redirect(url_for("login"))

    return render_template("reset_password.html", form=form, title="Password Reset")


@app.errorhandler(403)
def error_403(error):
    return render_template("403.html"), 403


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error_500(error):
    return render_template("500.html"), 500
