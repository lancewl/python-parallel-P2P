#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]
  then
    echo "Usage: ./create_peer.sh [Peer Count] [File Count] [File Size]"
    exit 0
fi

N=$1
F=$2
S=$3

for (( i=1; i<=$N; i++ ))
do
    mkdir "peer_folder$i"
    cd "peer_folder$i"
    for (( j=1; j<=$F; j++ ))
    do
        mkfile $S "data$j.txt"
    done
    cd ..
done