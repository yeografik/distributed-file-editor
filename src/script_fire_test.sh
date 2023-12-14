
i=0
while [ $i -lt 5 ]
do
  ./script_multiple_input.sh 5001 & ./script_multiple_input.sh 5002 & ./script_multiple_input.sh 5003 & ./script_multiple_input.sh 5004 & ./script_multiple_input.sh 5005 &
  i=$(( $i + 1 ))
done
