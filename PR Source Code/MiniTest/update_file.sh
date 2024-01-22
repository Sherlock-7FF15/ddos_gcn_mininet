#!/bin/bash


PORTS=( 
"60159"
"60160" "60161" "60189" "60204" "60008" "60009" "60010" "60011" "60012" "60013" "60014" "60015" "60016" "60017" "60018" "60019" "60020" "60021" "60022" "60023" "60024" "60025" "60026" "60027" "60029" "60030" "60031" "60032" "60033" "60034" "60035" "60036" "60037" "60038" "60039" "60041" "60042" "60043" "60044" "60045" "60046" "60047" "60048" "60049" "60050" "60051" "60052"
)
for PORT in "${PORTS[@]}"; do
    COMMAND="sshpass -p 'anrgrpi' scp -o StrictHostKeyChecking=no -r -P $PORT /home/pi/Documents/MiniTest/inference.py pi@anrg-picluster1.usc.edu:~/Documents/MiniTest/"
    echo "Running command with port $PORT: $COMMAND"
    eval "$COMMAND"
done
