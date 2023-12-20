#!/bin/bash
./scripts/script.sh 5001 & ./scripts/script.sh 5002 & ./scripts/script.sh 5003 & ./scripts/script.sh 5004 &
./scripts/script.sh 5005 & python3 server.py localhost 5006

