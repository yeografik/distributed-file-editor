
i=0
while [ $i -lt 5 ]
do
  ./script.sh 5001 & ./script.sh 5002 & ./script.sh 5003 & ./script.sh 5004 & ./script.sh 5005 &
  i=$(( $i + 1 ))
done
