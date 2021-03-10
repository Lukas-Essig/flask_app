import os
from . import db, app
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Host, Traveller
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message

auth = Blueprint('auth', __name__)

#login page

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.account"))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email.lower()).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("views.account"))
            else:
                flash('That doesn‘t seem to be right. Try again!', category='error')
        else:
            flash('Are you sure you have been here before? This Email doesn‘t exist.', category='error')

    return render_template("login.html", user=current_user)

#logout

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#sign up page

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("views.account"))
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        age = request.form.get('age')
        gender = request.form.get('gender')
        countryresidence = request.form.get('countryresidence')
        language1 = request.form.get('language1')
        language2 = request.form.get('language2')
        language3 = request.form.get('language3')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        password1 = request.form.get ('password1')
        password2 = request.form.get ('password2')

        user = User.query.filter_by(email=email.lower()).first()
        if len(firstname) < 2:
            flash('You seem to have a very short name... Maybe too short?', category='error')
        if len(surname) < 2:
            flash('You seem to have a very short name... Maybe too short?', category='error')
        elif user:
            flash('This Email already exists.', category='error')
        elif len(email) < 4:
            flash('You seem to have a very short Email... Maybe too short?', category='error')
        elif password1 != password2:
            flash('Your passwords don‘t match.', category='error')
        elif len(password1) < 8:
            flash('Please type at least 8 characters for your password!', category='error')
        else: 
            new_user = User(firstname=firstname.capitalize(),surname=surname.capitalize(), age=age, gender=gender, countryresidence=countryresidence, language1=language1, language2=language2, language3=language3, email=email.lower(), phonenumber=phonenumber, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.account'))

    return render_template("signup.html", user=current_user)

#update user page

@auth.route('/updateuser', methods=['GET', 'POST'])
@login_required
def updateuser():
    firstname = request.form.get('firstname')
    surname = request.form.get('surname')
    age = request.form.get('age')
    gender = request.form.get('gender')
    countryresidence = request.form.get('countryresidence')
    language1 = request.form.get('language1')
    language2 = request.form.get('language2')
    language3 = request.form.get('language3')
    email = request.form.get('email')
    phonenumber = request.form.get('phonenumber')

    if request.method == 'POST':
            user = User.query.filter_by(email=email).first()
            if len(firstname) < 2:
                flash('You seem to have a very short name... Maybe too short?', category='error')
            elif user and email != current_user.email:
                flash('This Email already exists.', category='error')
            elif len(email) < 4:
                flash('You seem to have a very short Email... Maybe too short?', category='error')
            else: 
                current_user.firstname = firstname.capitalize()
                current_user.surname = surname.capitalize()
                current_user.age = age
                current_user.gender = gender
                current_user.countryresidence = countryresidence
                current_user.language1 = language1
                current_user.language2 = language2
                current_user.language3 = language3
                current_user.email = email.lower()
                current_user.phonenumber = phonenumber
                db.session.commit()
                flash('Account updated!', category='success')
                return redirect(url_for('views.account'))

    return render_template("updateuser.html", user=current_user)

#delete user account

@auth.route("/user/delete_user", methods=['POST'])
@login_required
def delete_user():
    traveller = Traveller.query.filter_by(user_id=current_user.id).first()
    host = Host.query.filter_by(user_id=current_user.id).first()
    user = User.query.filter_by(id=current_user.id).first()
    if traveller:
        db.session.delete(traveller)
    if host:
        db.session.delete(host)
    db.session.delete(user)
    db.session.commit()
    flash('Your Account has been deleted! We hope to see you again soon...', category='success')
    return redirect(url_for('views.home'))

#host register

@auth.route('/host_sign_up', methods=['GET', 'POST'])
@login_required
def host():
    if request.method == 'POST':
        title = request.form.get('title')
        country = request.form.get('country')
        street = request.form.get('street')
        housenumber = request.form.get('housenumber')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        maximumpeople = request.form.get('maximumpeople')
        h_tent = request.form.get('h_tent')
        h_car = request.form.get('h_car')
        h_cartrailer = request.form.get('h_cartrailer')
        h_motorhome = request.form.get('h_motorhome')
        h_toilet = request.form.get('h_toilet')
        h_shower = request.form.get('h_shower')
        h_washingmachine = request.form.get('h_washingmachine')
        h_water = request.form.get('h_water')
        h_trash = request.form.get('h_trash')
        h_note = request.form.get('h_note')

        if len(housenumber) > 6:
            flash('Check your house number!')
        elif len(zipcode) > 10:
            flash('Check your Zip Code!')
        else:
            new_host = Host(title=title, country=country, street=street.capitalize(), housenumber=housenumber, city=city.capitalize(), state=state.capitalize(), zipcode=zipcode, maximumpeople=maximumpeople, h_tent=h_tent, h_car=h_car, h_cartrailer=h_cartrailer, h_motorhome=h_motorhome, h_toilet=h_toilet, h_shower=h_shower, h_washingmachine=h_washingmachine, h_water=h_water, h_trash=h_trash, h_note=h_note, user_id=current_user.id)
            db.session.add(new_host)
            db.session.commit()
            flash('You are now a Host!', category='success')
            return redirect(url_for('views.account'))
    return render_template("host.html", user=current_user)

#update host page

@auth.route('/updatehost', methods=['GET', 'POST'])
@login_required
def updatehost():
    hostvalue = Host.query.filter_by(user_id = current_user.id).first()
    title = request.form.get('title')
    country = request.form.get('country')
    street = request.form.get('street')
    housenumber = request.form.get('housenumber')
    city = request.form.get('city')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    maximumpeople = request.form.get('maximumpeople')
    h_tent = request.form.get('h_tent')
    h_car = request.form.get('h_car')
    h_cartrailer = request.form.get('h_cartrailer')
    h_motorhome = request.form.get('h_motorhome')
    h_toilet = request.form.get('h_toilet')
    h_shower = request.form.get('h_shower')
    h_washingmachine = request.form.get('h_washingmachine')
    h_water = request.form.get('h_water')
    h_trash = request.form.get('h_trash')
    h_note = request.form.get('h_note')

    if request.method == 'POST':

        if len(housenumber) > 6:
            flash('Check your house number!')
        elif len(zipcode) > 10:
            flash('Check your Zip Code!')
        else:
            hostvalue.title = title
            hostvalue.country = country
            hostvalue.street = street.capitalize()
            hostvalue.housenumber = housenumber
            hostvalue.city = city.capitalize()
            hostvalue.state = state.capitalize()
            hostvalue.zipcode = zipcode
            hostvalue.maximumpeople = maximumpeople
            hostvalue.h_tent = h_tent
            hostvalue.h_car = h_car
            hostvalue.h_cartrailer = h_cartrailer
            hostvalue.h_motorhome = h_motorhome
            hostvalue.h_toilet = h_toilet
            hostvalue.h_shower = h_shower
            hostvalue.h_washingmachine = h_washingmachine
            hostvalue.h_water = h_water
            hostvalue.h_trash = h_trash
            hostvalue.h_note = h_note
            db.session.commit()
            flash('Host informations updated!', category='success')
            return redirect(url_for('views.account'))
    return render_template("updatehost.html", user=current_user, host1=hostvalue)

#delete host account

@auth.route("/user/delete_host", methods=['POST'])
@login_required
def delete_host():
    host = Host.query.filter_by(user_id=current_user.id).first()
    db.session.delete(host)
    db.session.commit()
    flash('Your Host Account has been deleted!', category='success')
    return redirect(url_for('views.account'))

#traveller register

@auth.route('/traveller_sign_up', methods=['GET', 'POST'])
@login_required
def traveller():
    if request.method == 'POST':
        t_tent = request.form.get('t_tent')
        t_car = request.form.get('t_car')
        t_cartrailer = request.form.get('t_cartrailer')
        t_motorhome = request.form.get('t_motorhome')
        numberofpeople = request.form.get('numberofpeople')
        t_toilet = request.form.get('t_toilet')
        t_shower = request.form.get('t_shower')
        t_washingmachine = request.form.get('t_washingmachine')
        t_water = request.form.get('t_water')
        t_trash = request.form.get('t_trash')
        t_note = request.form.get('t_note')

        
        if len(numberofpeople) > 2:
            flash("That's too many people!")
        else:
            new_traveller = Traveller(t_tent=t_tent, t_car=t_car, t_cartrailer=t_cartrailer, t_motorhome=t_motorhome, numberofpeople=numberofpeople, t_toilet=t_toilet, t_shower=t_shower, t_washingmachine=t_washingmachine, t_water=t_water, t_trash=t_trash, t_note=t_note, user_id=current_user.id)
            db.session.add(new_traveller)
            db.session.commit()
            flash('You are now a Traveller!', category='success')
            return redirect(url_for('views.account'))

    return render_template("traveller.html", user=current_user)

#update traveller page

@auth.route('/updatetraveller', methods=['GET', 'POST'])
@login_required
def updatetraveller():
        travellervalue = Traveller.query.filter_by(user_id = current_user.id).first()
        t_tent = request.form.get('t_tent')
        t_car = request.form.get('t_car')
        t_cartrailer = request.form.get('t_cartrailer')
        t_motorhome = request.form.get('t_motorhome')
        numberofpeople = request.form.get('numberofpeople')
        t_toilet = request.form.get('t_toilet')
        t_shower = request.form.get('t_shower')
        t_washingmachine = request.form.get('t_washingmachine')
        t_water = request.form.get('t_water')
        t_trash = request.form.get('t_trash')
        t_note = request.form.get('t_note')

        
        if request.method == 'POST':
            if len(numberofpeople) > 2:
                flash("That's too many people!")
            else:
                travellervalue.t_tent = t_tent
                travellervalue.t_car = t_car
                travellervalue.t_cartrailer = t_cartrailer
                travellervalue.t_motorhome = t_motorhome
                travellervalue.numberofpeople = numberofpeople
                travellervalue.t_toilet = t_toilet
                travellervalue.t_shower = t_shower
                travellervalue.t_washingmachine = t_washingmachine
                travellervalue.t_water = t_water
                travellervalue.t_trash = t_trash
                travellervalue.t_note = t_note
                db.session.commit()
                flash('Traveller informations updated!', category='success')
                return redirect(url_for('views.account'))

        return render_template("updatetraveller.html", user=current_user, traveller1=travellervalue)

#delete traveller account

@auth.route("/user/delete_traveller", methods=['POST'])
@login_required
def delete_traveller():
    traveller = Traveller.query.filter_by(user_id=current_user.id).first()
    db.session.delete(traveller)
    db.session.commit()
    flash('Your Traveller Account has been deleted!', category='success')
    return redirect(url_for('views.account'))

#reset password

def send_reset_email(user):
    from . import mail
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@camp4free.com', recipients=[user.email])
    msg.body = f'''Hi from Camp4Free, if you recently made the request to change your password, please visit the following link:
    {url_for('auth.reset_token', token=token, _external=True)}
    If you did not make this request then you can ignore this email and no changes will be made. In case this happens more often, please contact us on info.camp4free@gmail.com.
    '''
    mail.send(msg)
                
@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.account'))

    email = request.form.get('email')
    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("An email has been sent to you!", category='success')
            return redirect(url_for('auth.login'))
        else:
            flash("This email does not exist. Please Sign up first.", category='error')
            return redirect(url_for('auth.reset_request'))
    return render_template('reset_request.html', user=current_user)
    
@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.account'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', category='error')
        return redirect(url_for('auth.reset_request'))
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    if request.method == 'POST':
        if password1 != password2:
            flash('Your passwords don‘t match.', category='error')
        elif len(password1) < 8:
            flash('Please type at least 8 characters for your password!', category='error')
        else: 
            password = generate_password_hash(password1, method='sha256')
            user.password = password
            db.session.commit()
            flash('Password changed!', category='success')
            return redirect(url_for('auth.login'))
    return render_template('reset_token.html', user=current_user)