from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.users_model import User
from flask_app.models.messages_model import Message
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/register', methods=['post'])
def register_user():
    if not User.validate(request.form):
        return redirect('/')
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    user_data = {
        **request.form,
        'password': pw_hash
    }
    id = User.create_user(user_data)

    session['email'] = request.form['email']
    session['id'] = id
    return redirect('/wall')


@app.route('/login', methods=['post'])
def login_user():
    user = User.get_one_by_email(request.form)
    if not user:
        flash("Invalid credentials.", "login")
        return redirect('/')
    elif not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid credentials.", "login")
        return redirect('/')
    
    session['email'] = user.email
    session['id'] = user.id
    
    return redirect('/wall')

@app.route('/wall')
def wall():
    if 'email' not in session:
        return redirect('/')
    current_user = Message.get_messages_by_recipient({'email':session['email']})
    other_users = User.get_all_but_one({'email':session['email']})
    sent_messages = Message.get_sent_messages({'sender_id':session['id']})
    return render_template('wall.html', current_user = current_user, other_users=other_users, sent_messages=sent_messages)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/sendmessage/<int:sender_id>/<int:recipient_id>', methods=['post'])
def send_message(sender_id, recipient_id):
    if not Message.validate_message(request.form):
        return redirect('/wall')

    message_data = {
        'sender_id':sender_id,
        'recipient_id':recipient_id,
        'message_text':request.form['message_text']
    }
    Message.create_message(message_data)
    flash("Message Sent!", "message")
    return redirect('/wall')

@app.route('/deletemessage/<int:id>')
def delete_message(id):
    Message.delete_message({'id':id})
    return redirect('/wall')
