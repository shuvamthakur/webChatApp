import flask
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pymongo.errors import DuplicateKeyError

from db import get_user, save_user

app = Flask(__name__)
app.secret_key = "something random we need for socketio"
socketio = SocketIO(app)
login_manager = LoginManager()  ##connecting login manager with app
login_manager.init_app(app)  ##init boiii
login_manager.login_view = 'login'


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat')
@login_required
def chat():
    username = request.args.get('username')
    roomid = request.args.get('roomid')

    if username and roomid:
        return render_template("chat.html", username=username, roomid=roomid)
    else:
        return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for(
            'home'))  ##if you're logged in then it will not go to login page if you type login it will go to home

    message = ''  ##empty string
    if request.method == 'POST':
        username = request.form.get('username')  ## taking things from post i guess
        password = request.form.get('password')
        email = request.form.get('email')
        try:
            save_user(username, email, password)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "USER EXISTS!"
    return render_template('signup.html', message=message)


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} message has been received from {} in room {}".format(data['username'], data['roomid'],
                                                                             data['message']))  ##print in log
    socketio.emit('receive_message', data, room=data['roomid'])  ##send with event receive_message to room of concern
    ##now handle receive_message in script


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room ".format(
        data['username']))  ##will also print date instead of simple print also prints time shows in terminal
    join_room(data['roomid'])  ##makes your client join specific room with inbuilt socket room function
    socketio.emit('join_room_announcement', data)


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['roomid']))
    leave_room(data['roomid'])
    socketio.emit('leave_room_announcement', data, roomid=data['roomid'])


@login_manager.user_loader
def load_user(username):
    return get_user(username)  ## defined in db.py gets user from db


@app.route('/login', methods=['GET', 'POST'])  ## when GET, returns HTML login page, when POST form submitted
def login():
    if current_user.is_authenticated:
        return redirect(url_for(
            'home'))  ##if you're logged in then it will not go to login page if you type login it will go to home

    message = ''  ##empty string
    if request.method == 'POST':
        username = request.form.get('username')  ## taking things from post i guess
        password_input = request.form.get('password')

        user = get_user(username)  ## create var

        if user and user.check_password(password_input):  ##check if authenticated and pass only if
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to Login'
            return render_template('login.html',
                                   message=message)  ## in login there is message space and we pass the message now
    return flask.render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    socketio.run(app, debug=True)
