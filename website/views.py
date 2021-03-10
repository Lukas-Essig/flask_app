import os
import secrets
import json
from PIL import Image, ExifTags
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Host, Traveller
from . import db
from website import app
from flask_mail import Message

views = Blueprint('views', __name__)

#home page

@views.route('/')
@views.route('/home')
def home():
    return render_template("index.html", user=current_user)

#find host page

@views.route('/find_host', methods=['GET', 'POST'])
@login_required
def find_host():
    hostvalue = Host.query.filter_by(user_id = current_user.id).first()
    travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
    page = request.args.get('page', 1, type=int)
    hosts = Host.query.order_by(Host.date.desc()).paginate(page=page, per_page=5)
    if travellervalue:
        if request.method == 'POST':
            return redirect(url_for('views.find_host'))
        return render_template("find_host.html", user=current_user, hosts=hosts)

    else:
        flash('You have to register as a traveller before accessing this page!', category='error')
        return redirect(url_for('views.account'))

@views.route('/search')
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    hosts = Host.query.order_by(Host.date.desc()).filter((Host.city==request.args.get('searchbar')) | (Host.title==request.args.get('searchbar')) | (Host.country==request.args.get('searchbar'))).paginate(page=page, per_page=5)
    travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
    if travellervalue:
        if request.method == 'POST':
            return redirect(url_for('views.find_host'))
        return render_template('find_host.html', hosts=hosts, user=current_user)
    else:
        flash('You have to register as a traveller before accessing this page!', category='error')
        return redirect(url_for('views.account'))

@views.route('/host:<int:host_id>')
@login_required
def specific_host(host_id):
    host = Host.query.get_or_404(host_id)
    travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
    if travellervalue:
        return render_template('specific_host.html', user=current_user, host=host)
    else:
        flash('You have to register as a traveller before accessing this page!', category='error')
        return redirect(url_for('views.account'))

#user page

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    i = Image.open(form_picture)
    im_thumb = crop_max_square(i).resize((150, 150), Image.LANCZOS)
    im_thumb.save(picture_path)

    return picture_fn

@views.route('/user', methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    hostvalue = Host.query.filter_by(user_id = current_user.id).first()
    travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
    on_off = request.form.get('on_off')

    if request.method == 'POST':
        if hostvalue:
            hostvalue.on_off = on_off
            db.session.commit()
            if hostvalue.on_off == "On":
                flash('You are now visible as a Host!', category='success')
            else:
                flash('You are now invisible for travellers!', category='success')
            return redirect(url_for('views.account'))

    return render_template("user.html", host1=hostvalue, traveller1=travellervalue, user=current_user, image_file=image_file)

#user page profile picture

@views.route('/update-profile-pic', methods=['GET', 'POST'])
@login_required
def update_profile_pic():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if request.method == 'POST':

        profile_pic = request.files['profile_pic']
        current_pic = current_user.image_file
        current_pic_path = os.path.join(app.root_path, 'static/profile_pics', current_pic)

        if profile_pic:
            current_pic = current_user.image_file
            current_pic_path = os.path.join(app.root_path, 'static/profile_pics', current_pic)
            if current_pic != "default.jpeg":
                os.remove(current_pic_path)
            picture_file = save_picture(profile_pic)
            current_user.image_file = picture_file
            db.session.commit()
            flash('Your Profile Picture was updated!', category='success')
            return redirect(url_for('views.account'))

    return render_template("user.html", user=current_user, image_file=image_file)


@views.route('/delete-profile-pic', methods=['GET', 'POST'])
@login_required
def delete_profile_pic():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if request.method == 'POST':
       
        current_pic = current_user.image_file
        current_pic_path = os.path.join(app.root_path, 'static/profile_pics', current_pic)
    
        current_pic = current_user.image_file
        current_pic_path = os.path.join(app.root_path, 'static/profile_pics', current_pic)
        if current_pic != "default.jpeg":
            os.remove(current_pic_path)
        default_pic = "default.jpeg"
        current_user.image_file = default_pic
        db.session.commit()
        flash('Your Profile Picture was deleted!', category='success')
        return redirect(url_for('views.account'))

    return render_template("user.html", user=current_user, image_file=image_file)


#contact page

@views.route('/contact')
def contact():
    return render_template("contact.html", user=current_user)

#contact host

@views.route('/send_contact_email:<int:host_user_id>', methods=['GET', 'POST'])
@login_required
def send_contact_email(host_user_id):
    from . import mail
    host = Host.query.get_or_404(host_user_id)
    user = User.query.filter_by(id=host_user_id).first()
    travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
    if travellervalue:
        msg = Message(current_user.firstname + ' would like to stay at your place!', sender='noreply@camp4free.com', recipients=[user.email])
        msg.html = render_template('contactemail' + '.html', user=current_user, traveller=travellervalue)
        mail.send(msg)
        return redirect (url_for('views.find_host'))
    else:
        flash('You have to register as a traveller before accessing this page!', category='error')
        return redirect(url_for('views.account'))