from flask import Flask,render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
socketio=SocketIO(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat')
def chat():
    username = request.args.get('username')
    roomid = request.args.get('roomid')

    if username and roomid:
        return render_template("chat.html", username=username, roomid=roomid)
    else:
        return redirect(url_for('home'))

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} message has been received from {} in room {}".format(data['username'], data['roomid'], data['message'])) ##print in log
    socketio.emit('receive_message', data, room=data['roomid'])       ##send with event receive_message to room of concern
    ##now handle receive_message in script



@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room ".format(data['username'])) ##will also print date instead of simple print also prints time shows in terminal
    join_room(data['roomid'])##makes your client join specific room with inbuilt socket room fucntion
    socketio.emit('join_room_announcement', data)

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['roomid']))
    leave_room(data['roomid'])
    socketio.emit('leave_room_announcement', data, roomid=data['roomid'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
