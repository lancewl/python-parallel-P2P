#!/bin/bash
if [ -z "$1" ]
  then
    echo "Usage: ./eval.sh [Peer Count]"
    exit 0
fi

set -m

# How many peers
N=$1
OUT="../out/N$N/"
mkdir -p ${OUT}
rm ${OUT}*
rm -rf peer_folder*
./create_peer.sh 1 10 1m
for (( i=2; i<=$N; i++ ))
do
    cp -r peer_folder1 peer_folder${i}
done

SERVER='python ../src/server.py'
PEER='python ../src/peer.py'
MAIN='peer_folder_main'
mkdir -p ${MAIN}

# port base number
BASE=40000

# start the indexing server
echo "Starting indexing server!"
$SERVER > ${OUT}server.txt 2>&1 &

# start peers
echo "Starting peers!"
for (( i=1; i<=$N; i++ ))
do
    PORT=$(( $BASE + $i*2 ))
    echo -e "HANG\n" | $PEER ${PORT} --dir peer_folder${i} > ${OUT}p${i}.txt 2>&1 &
    pids[${i}]=$!
done

# run the main peer to download the files
# QUERY 10 files
echo "Starting main peers!"
ACT='WAIT\n'
for i in {1..10}
do
    ACT=$ACT"QUERY data${i}.txt\n"
done
ACT=$ACT'EXIT\n'

echo -e $ACT | $PEER $BASE --dir ${MAIN} > ${OUT}main.txt 2>&1 &
mainp=$!
wait $mainp

# kill all peers
for pid in ${pids[*]}; do
    kill -SIGINT $pid
done

echo "All peer is done!"
rm -rf peer_folder*
kill -SIGINT %1