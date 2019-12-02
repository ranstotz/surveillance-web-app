import cv2
import numpy as np
import zmq
import base64
import time


class stream_handler(object):
    """ 
    The stream handler object handles all incoming stream data by
    subscribing to a message queue and return individual frames. 
    """

    def __init__(self):
        """ Constructor that initializes the ZMQ context and socket. """

        self.footage_socket = zmq.Context().socket(zmq.SUB)

    def connect_streaming_socket(self, ip, port):
        """ Connects to specified ip and port and subscribes to queue. """

        connection_address = 'tcp://' + ip + ':' + port
        self.footage_socket.bind(connection_address)
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

    def get_frame(self):
        """ Get jpeg frame from socket. Decode to base64. """

        try:
            frame = self.footage_socket.recv_string()
            img = base64.b64decode(frame)
            return img

        except:
            print "hit exception in get_frame"
            pass

    def write_stream(self):
        """ Method for debugging this class locally on Raspberry Pi before 
            deploying to the server. """

        connectionFlag = False
        count = 0
        while True:
            try:
                frame = self.footage_socket.recv_string()
                if connectionFlag == False:
                    print "Connection made. Now streaming.\n"
                    connectionFlag = True
                img = base64.b64decode(frame)
                npimg = np.fromstring(img, dtype=np.uint8)
                source = cv2.imdecode(npimg, 1)
                stream_path = "images/stream_" + str(count) + ".jpg"
                # write to file
                #cv2.imwrite(stream_path, source)
                # display stream
                #cv2.imshow("Stream", source)
                # cv2.waitKey(1)
                count += 1
                print "captured data"

            except KeyboardInterrupt:
                cv2.destroyAllWindows()
                break
