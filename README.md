# Surveillance Webapp

The goal of this project was to create a live streaming app from scratch using a Raspberry Pi and a cloud server. This repo is the server portion of the project.

The webapp accepts a data stream of raw JPEG images via a messaging queue (ZMQ) in Flask and displays the live frames in the browser. The connections are made made over TCP.

See docstrings for more information.
