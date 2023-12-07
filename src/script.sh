port=$1
if [ $port -eq 5001 ] 
then
    echo -e 'ins\n0\na\nins\n1\nb\nins\n2\nc\nexit' | python3 app.py localhost $port
else
    echo -e 'ins\n0\nd\nins\n1\ne\nins\n2\nf\nexit' | python3 app.py localhost $port
fi
