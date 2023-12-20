i=0
python3 server.py localhost 5006 &
while [ $i -lt 5 ]
do
  ./scripts/script.sh 5001 & ./scripts/script.sh 5002 & ./scripts/script.sh 5003 & ./scripts/script.sh 5004 &
  ./scripts/script.sh 5005 &
  i=$(( $i + 1 ))
done
python3 server.py localhost 5007 &
