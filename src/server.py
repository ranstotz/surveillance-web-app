# server.py
import os
import sys
import threading
import time
import zmq
import logging
import yaml

# flask stuff
from flask import Flask, render_template
from flask import Flask, url_for, request, redirect, send_from_directory, render_template, session, abort, Response, stream_with_context
from werkzeug.utils import secure_filename

# custom class
from pi_server import stream_handler

# flask config
app = Flask(__name__, static_folder="../static/dist",
            template_folder="../static")
app.secret_key = os.urandom(12)

# Prevent logging and message from hitting the terminal,
# can change for logging purposes.
f = open('/dev/null', 'w')
sys.stdout = f
sys.stderr = f

# connection to raspberry pi
connection_flag = False

# configuration data
config_data = get_config('../../config.yaml')

# =============================================================================
# routing
# =============================================================================


@app.route('/')
def home():
    """ Root of site. Creates a streaming connection upon login. """

    global connection_flag
    global config_data

    if not session.get('logged_in'):
        return render_template('login.html')
    else:

        try:
            server = stream_handler()
            server.connect_streaming_socket(
                '*', str(config_data['listening_port']))
        except:
            return render_template('video_in_use.html')

        connection_flag = True
        return Response(gen(server),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/login', methods=['POST'])
def do_admin_login():
    """ Admin login. """

    global config_data
    if request.form['password'] == config_data['password'] and request.form['username'] == config_data['username']:
        session['logged_in'] = True
    else:
        flash('wrong password')
    return home()


# =============================================================================
# functions
# =============================================================================


def gen(camera):
    """ This generator function is required to ensure connections are
    closed when the user closes the browser. It yields the byte frames
    if browser remains open. """

    global connection_flag

    while True:
        try:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            # flip connection flag to third, error option
            connection_flag = -1
            break


def message_handler():
    """ Message handler function to connect sockets via TCP with the Raspi. 
        This function is within its own thread and pings every 0.1 seconds
        to alert the Raspi listener if the connection is still required (aka
        send more frames or not). """

    global connection_flag
    global config_data

    one_message_sent = False

    connected = "connected"
    disconnected = "disconnected"
    try:
        message_socket = zmq.Context().socket(zmq.PUB)
        message_socket.connect(
            'tcp://' + str(config_data['connection_ip']) + ':' + str(config_data['connection_port']))
    except:
        pass

    while True:
        if connection_flag == True:
            if one_message_sent == False:
                try:
                    message_socket.send(connected)
                    one_message_sent = True
                except:
                    pass

        elif connection_flag == -1:
            try:
                message_socket.send(disconnected)
            except:
                pass
            connection_flag = False
            one_message_sent = False

        time.sleep(0.1)


def get_config(file_path):
    """ Returns configuration data in yaml file as a dict. """

    with open(file_path, 'r') as fp:
        return yaml.load(fp)

# =============================================================================


if __name__ == "__main__":

    # Thread the message handler that pings the Raspi whether the
    # connection is still valid.
    message_handler_t = threading.Thread(target=message_handler)
    message_handler_t.daemon = True
    message_handler_t.start()

    app.run(threaded=True)
