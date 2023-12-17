#!/bin/bash
./script.sh 5001 & ./script.sh 5002 & python3 server.py localhost 5003 & ./script.sh 5004 & ./script.sh 5005 &
sleep 0.5
./script.sh 5003 &
