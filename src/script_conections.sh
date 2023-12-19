#!/bin/bash
./script.sh 5001 & ./script.sh 5002 & ./script.sh 5003 &
python3 server.py localhost 5006 & python3 server.py localhost 5007 & python3 server.py localhost 5008 &
