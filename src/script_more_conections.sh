#!/bin/bash
./script.sh 5001 & ./script.sh 5002 & ./script.sh 5003 & ./script.sh 5004 & ./script.sh 5005 &
python3 server.py localhost 5006 & python3 server.py localhost 5007 & python3 server.py localhost 5008 &
python3 server.py localhost 5009 & python3 server.py localhost 5010 &
