#!/bin/bash
echo "Starting server at port 8000"

THREADS=1 # Set the number of threads here
PORT=8000 # Set the port here

gunicorn -w $THREADS -b 0.0.0.0:$PORT main:app