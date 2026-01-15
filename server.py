from flask import Flask, request, render_template, redirect, url_for, g, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time

# -------------------- Logger init --------------------
import logger

app = Flask(__name__)
app.secret_key = "secret-key"

# -------------------- SQLAlchemy config --------------------
# For Git Actions
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@postgres:5432/notebook"
# For localhost server
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost:5432/notebook"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------- Models --------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    notes = db.relationship("Note", backref="user", cascade="all, delete", lazy=True)


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    header = db.Column(db.String(255))
    image_data = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    tags = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------- DB init (wait for initialization) --------------------
with app.app_context():
    for i in range(10):
        try:
            db.create_all()
            break
        except Exception as e:
            print(f"DB not ready, retry {i+1}/10")
            time.sleep(2)
    else:
        raise RuntimeError("Database not available")


# -------------------- Logging --------------------
@app.before_request
def before_request():
    g.user = session.get("user_id")
    g.path = request.full_path
    g.method = request.method
    g.client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    app.logger.info(
        "method=%s, path=%s, client_ip=%s, user=%s",
        request.method, request.path, g.client_ip, g.user
    )


# -------------------- Routes --------------------
@app.route("/", methods=["GET"])
def hello():
    return render_template("main.html")


# User has to log in to use features like writing or checking notes
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            message = "Email and password cannot be empty"
            return render_template("login.html", message=message)

        user = User.query.filter_by(email=email).first()

        if user:
            # Log in
            if check_password_hash(user.password, password): # Correct email, password
                session["user_id"] = user.id
                session["email"] = user.email
                return redirect(url_for("hello"))  # redirect on /
            else: # Incorrect email, password
                message = "Wrong password"
        else:
            # Registration
            hashed_password = generate_password_hash(password)
            user = User(email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            session["email"] = user.email
            return redirect(url_for("hello"))  # redirect on /

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("hello")) # redirect on /


@app.route("/all_users")
def all_users():
    users = User.query.with_entities(User.email, User.password).all()
    return render_template("all_users.html", users=users)


@app.route("/delete_user", methods=["POST"])
def delete_user():
    email = request.form.get("email")
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for("all_users"))


@app.route("/note", methods=["GET", "POST"]) # Create a new note
@app.route("/note/<int:note_id>", methods=["GET", "POST"]) # Edit old note
def note(note_id=None):
    # log in to make notes
    if "user_id" not in session:
        return redirect(url_for("login"))

    image_data = ""
    text_note = ""
    note_header = ""
    tags = ""

    if request.method == "POST": # save note (after clicking Save button)
        image_data = request.form.get("imageData", "")
        text_note = request.form.get("textNote", "")
        note_header = request.form.get("noteHeader", "")

        tags_list = request.form.getlist("tags[]")
        tags = ",".join(tag.strip() for tag in tags_list if tag.strip())

        if note_id: # Edit old note
            note_obj = Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()
            if note_obj:
                note_obj.header = note_header
                note_obj.image_data = image_data
                note_obj.text = text_note
                note_obj.tags = tags
        else: # Save new note
            note_obj = Note(
                user_id=session["user_id"],
                header=note_header,
                image_data=image_data,
                text=text_note,
                tags=tags
            )
            db.session.add(note_obj)

        db.session.commit()
        return redirect(url_for("note", note_id=note_obj.id))

    if note_id: # load the note for editing (after clicking Edit button in /all_notes)
        note_obj = Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()
        if not note_obj:
            return redirect(url_for("all_notes"))

        note_header = note_obj.header
        image_data = note_obj.image_data
        text_note = note_obj.text
        tags = note_obj.tags

    return render_template(
        "note.html",
        image_data=image_data,
        text_note=text_note,
        note_header=note_header,
        note_id=note_id,
        tags=tags
    )


@app.route("/all_notes")
def all_notes():
    # log in to see all notes created by user
    if "user_id" not in session:
        return redirect(url_for("login"))

    search_query = request.args.get("q", "").strip()
    tags = request.args.getlist("tags[]")
    tags = [t.strip() for t in tags if t.strip()]

    query = Note.query.filter_by(user_id=session["user_id"])

    if search_query:
        query = query.filter(Note.header.ilike(f"%{search_query}%"))

    for tag in tags:
        query = query.filter(Note.tags.ilike(f"%{tag}%"))

    notes_db = query.order_by(Note.created_at.desc()).all()

    # AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        notes = [{
            "id": n.id,
            "header": n.header,
            "img": n.image_data,
            "text": n.text,
            "tags": n.tags
        } for n in notes_db]
        return jsonify(notes)

    # Not AJAX
    notes = [{
        "id": n.id,
        "header": n.header,
        "img": n.image_data,
        "text": n.text,
        "tags": n.tags
    } for n in notes_db]

    return render_template(
        "all_notes.html",
        notes=notes,
        search_query=search_query,
        tags=tags
    )


@app.route("/delete_note", methods=["POST"])
def delete_note():
    # log in to delete notes
    if "user_id" not in session:
        return redirect(url_for("login"))

    note_id = request.form.get("note_id")
    note_obj = Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()
    if note_obj:
        db.session.delete(note_obj)
        db.session.commit()

    return redirect(url_for("all_notes"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)