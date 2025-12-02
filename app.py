from flask import Flask, render_template, send_from_directory, url_for, redirect, request, flash, make_response
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, SelectField, StringField
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from forms import LoginForm, RegistrationForm  # RegistrationForm is optional if you use it later
from models import db, ClothingItem, User
import os
import json
import random
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY']= 'asklsh'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///closet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# --- Form for uploads ---
class UploadForm(FlaskForm):
    name = StringField("Item Name")
    category = SelectField(
        "Category", 
        choices=[("tops","Tops"), ("bottoms","Bottoms"), ("shoes","Shoes"), ("accessories","Accessories"),("other", "Other")]
    )
    tags = StringField("Tags (comma separated)")
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField("Upload")

# --- Route to serve uploaded files ---
@app.route('/uploads/<filename>')

def get_file(filename):    
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

# --- Upload route ---
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    form = UploadForm()
    theme = request.cookies.get("theme", "light")
    if form.validate_on_submit():
        # Save the uploaded image file
        filename = photos.save(form.photo.data)

        # Process tags into a list
        tags_list = [t.strip() for t in form.tags.data.split(',')] if form.tags.data else []

        # Create a new ClothingItem linked to the current user
        new_item = ClothingItem(
            name=form.name.data,
            category=form.category.data,
            image_filename=filename,
            tags=json.dumps(tags_list),
            user_id=current_user.id  
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('browse'))

    return render_template('upload.html', form=form, theme=theme)

# --- Browse route ---
@app.route('/')
@login_required
def browse():
    theme = request.cookies.get("theme", "light")
    form = UploadForm() 
    items = ClothingItem.query.filter_by(user_id=current_user.id).all()
    # Build URL for images
    for item in items:
        item.image_url = url_for('get_file', filename=item.image_filename)
        try:
           item.tags_list = json.loads(item.tags) if item.tags else []
        except json.JSONDecodeError:
            item.tags_list = []

    return render_template(
        'browse.html',
        items=items,
        item_count=len(items),
        form=form,
        theme=theme
        )


@app.route("/set_theme/<mode>")
def set_theme(mode):
    if mode not in ("light", "dark"):
        mode = "light"
    resp = make_response(redirect(request.referrer or url_for("browse")))
    resp.set_cookie("theme", mode, max_age=86400)  
    return resp


# --- Delete Upload ---
@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = ClothingItem.query.get_or_404(item_id)

    # Make sure the logged-in user owns this item
    if item.user_id != current_user.id:
        flash("You can only delete your own items.", "danger")
        return redirect(url_for('browse'))

    try:
        # Delete image file from uploads folder
        image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], item.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete the item from the database
        db.session.delete(item)
        db.session.commit()
        flash(f"{item.name} has been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting item.", "danger")
        print(e)

    return redirect(url_for('browse'))


@app.route("/login", methods=["GET", "POST"])
def login():
    theme = request.cookies.get("theme", "light")
    if current_user.is_authenticated:
        return redirect(url_for("browse"))

    form = LoginForm()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.")
            return redirect(url_for("login"))

        login_user(user)

        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("browse")

        return redirect(next_page)

    return render_template("login.html", form=form, theme=theme)


# --- Logout route ---
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

# --- Runs the app, stores to the db --
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create tables if they don't exist
    app.run(debug=True)


@app.route("/register", methods=["GET", "POST"])
def register():
    theme = request.cookies.get("theme", "light")
    if current_user.is_authenticated:
        return redirect(url_for("browse"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("browse"))

    return render_template("register.html", form=form, theme=theme)

@app.route("/build-outfit")
@login_required
def build_outfit():
    # Get items by category
    tops = ClothingItem.query.filter_by(category="tops").all()
    bottoms = ClothingItem.query.filter_by(category="bottoms").all()
    shoes = ClothingItem.query.filter_by(category="shoes").all()
    other = ClothingItem.query.filter_by(category="other").all
    theme = request.cookies.get("theme", "light")

    # Add image_url to each item (same idea as in browse())
    for item in tops + bottoms + shoes:
        item.image_url = url_for('get_file', filename=item.image_filename)

# Now outfit.html can use item.image_url
    return render_template(
     "outfit.html",
        tops=tops,
        bottoms=bottoms,
        shoes=shoes,
        other=other,
        theme=theme
    )

@app.route("/generate-outfit")
@login_required
def generate_outfit():
    weather = request.args.get("weather", "").lower().strip()

    tops = ClothingItem.query.filter_by(user_id=current_user.id, category="tops").all()
    bottoms = ClothingItem.query.filter_by(user_id=current_user.id, category="bottoms").all()
    shoes = ClothingItem.query.filter_by(user_id=current_user.id, category="shoes").all()
    theme = request.cookies.get("theme", "light")

    for item in tops + bottoms + shoes:
        item.image_url = url_for("get_file", filename=item.image_filename)

    def filter_by_weather(items):
        if not weather:
            return items
        filtered = []
        for item in items:
            try:
                tags_list = json.loads(item.tags) if item.tags else []
            except json.JSONDecodeError:
                tags_list = []
            for tag in tags_list:
                if tag.lower().strip() == weather:
                    filtered.append(item)
                    break
        return filtered if filtered else items

    tops_for_choice = filter_by_weather(tops)
    bottoms_for_choice = filter_by_weather(bottoms)
    shoes_for_choice = filter_by_weather(shoes)

    def pick_one(items):
        return random.choice(items) if items else None

    top = pick_one(tops_for_choice)
    bottom = pick_one(bottoms_for_choice)
    shoe = pick_one(shoes_for_choice)

    if not (top and bottom and shoe):
        flash("You need at least one top, bottom, and pair of shoes to generate an outfit.", "warning")
        return redirect(url_for("build_outfit"))

    return render_template(
        "outfit.html",
        tops=tops,
        bottoms=bottoms,
        shoes=shoes,
        selected_top_id=top.id,
        selected_bottom_id=bottom.id,
        selected_shoes_id=shoe.id,
        theme=theme
    )

