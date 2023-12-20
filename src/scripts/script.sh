port=$1
if [ $port -eq 5001 ]
then
    echo 'ins\n0\na\nins\n1\nb\nins\n2\nc\nexit' | python3 client.py localhost $port
elif [ $port -eq 5002 ]
then
    echo 'ins\n0\nd\nins\n1\ne\nins\n2\nf\nexit' | python3 client.py localhost $port
elif [ $port -eq 5003 ]
then
    echo 'ins\n0\ng\nins\n1\nh\nins\n2\ni\nexit' | python3 client.py localhost $port
elif [ $port -eq 5004 ]
then
    echo 'ins\n0\nj\nins\n1\nk\nins\n2\nl\nexit' | python3 client.py localhost $port
else
    echo 'ins\n0\nm\nins\n1\nn\nins\n2\no\nexit' | python3 client.py localhost $port
fi
