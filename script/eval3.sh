#!/bin/bash
if [ -z "$1" ]
  then
    echo "Usage: ./eval.sh [File Size]"
    exit 0
fi

set -m

F=$1
N=4
OUT="../out/eval3/SIZE$F/"
mkdir -p ${OUT}
rm ${OUT}*
./create_peer.sh $N 5 ${F}

SERVER='python ../server/server.py'
PEER='python ../peer/peer.py'


# QUERY and Download 100 times
ACT='WAIT\n'
for i in {1..100}
do
    ACT=$ACT'QUERY data1.txt\n2\n'
done
ACT=$ACT'WAIT\n'

# start the indexing server
$SERVER > ${OUT}server.txt 2>&1 &

for (( i=1; i<=$N; i++ ))
do
    echo -e $ACT | $PEER 500${i}0 --dir peer_folder${i} > ${OUT}p${i}.txt 2>&1 &
    pids[${i}]=$!
done

# wait for all peers
for pid in ${pids[*]}; do
    wait $pid
done

echo "All peer is done!"
rm -rf peer_folder*
kill -SIGINT %1