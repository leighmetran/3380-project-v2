import re
from datetime import datetime
from backend.api import api_bp  

from flask import Flask, render_template, send_from_directory, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


app = Flask(__name__)
app.config['SECRET_KEY']= 'asklsh'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo= FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField('Upload')

@app.route('/uploads/<filename>')
def get_file(filename):    
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
    else:
        file_url= None    
    return render_template('.html', form=form, file_url=file_url)

if __name__=='__main__':
    app.run(debug=True)

@app.route("/")
def browse():
    items = [
        {
            "name": "White TOP Shirt",
            "category": "tops",
            "image_url": "/static/images/shirt.jpg",
            "tags": ["casual", "graphic"],
        },

        {
            "name": "Black Jeans",
            "category": "bottoms",
            "image_url": "/static/images/blk-jeans.webp",
            "tags": ["casual", "jeans"],
        },

        {
            "name": "Black Sneakers",
            "category": "shoes",
            "image_url": "/static/images/blk-sneaker.jpg",
            "tags": ["casual", "sneaker"],
        },

        {
            "name": "Psycho?",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020645.png",
            "tags": ["casual", "outfit", "graphic"],
        },

        {
            "name": "Purple Reign Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020712.png",
            "tags": ["casual", "graphic"],
        },

        {
            "name": "Abandonment Hoodie",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020736.png",
            "tags": ["jacket", "winter", "graphic"],
        },

        {
            "name": "Gratitude WWIC Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020801.png",
            "tags": ["casual", "graphic"],
        },

        {
            "name": "Wright Brothers Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020814.png",
            "tags": ["casual", "outfit"],
        },

        {
            "name": "Off WWIC Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020820.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "LUCKI Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020848.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "unLUCKI Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020853.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "Simone Green Tee",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020902.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "Purple Reign WWIC Short",
            "category": "bottoms",
            "image_url": "/static/images/Screenshot 2025-11-15 020917.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "WWIC V2 SHORT",
            "category": "bottoms",
            "image_url": "/static/images/Screenshot 2025-11-15 020926.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "WWIC V1 SHORT",
            "category": "bottoms",
            "image_url": "/static/images/Screenshot 2025-11-15 020931.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "The One Short",
            "category": "bottoms",
            "image_url": "/static/images/Screenshot 2025-11-15 020937.png",
            "tags": ["shorts", "outfit"],
        },

        {
            "name": "WWIC V1 LONG SLEEVE",
            "category": "tops",
            "image_url": "/static/images/Screenshot 2025-11-15 020951.png",
            "tags": ["custom", "outfit"],
        },

        {
            "name": "WHY WOULD I CAP",
            "category": "accessories",
            "image_url": "/static/images/Screenshot 2025-11-15 021033.png",
            "tags": ["hat", "rain"],
        },
    ]

    return render_template(
        "browse.html",
        items=items,
        item_count=len(items)
    )


# API routes
app.register_blueprint(api_bp, url_prefix="/api/v1")
