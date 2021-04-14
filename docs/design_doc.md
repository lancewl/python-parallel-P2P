# Design Doc

## Indexing Server

For the indexing server, I use `socket` which is a built-in module in `Python 3` to create connections between it and the peer nodes. At first, it will start listening on a specific port(can be set by passing argument). Whenever, a peer connect to the indexing server, it will create a thread by using `threading` module in `Python 3` to handle the connection with the peer so that the indexing server can handle multiple peer connections in the same time.

After the connection has been made between the indexing server and the peer node, they will start to send and receive message in `json` format. The indexing server will fisrt waiting for the peer node to send the information of their file list with file size and md5 to make a initial register. After receving the file information from the peer node, the indexing server will update the `peer_table`, `filesize_table` and `md5_table` which store the information of every peers that are currently connected to the P2P system. Then the indexing server will start to waiting the peer node to send any requests such as `UPDATE`, `QUERY`. If it receive an `QUERY` request, it will lookup the `peer_table` and return all ip address that contain the target file with the file size and md5 information.

To maintain a table for storing the information of every peers that are currently connected to the P2P system. I declare a global variable `peer_table` which is a `dictionary` in `Python` so that every connections in different threads can share the table with others. I also add a condtion lock to any operations that trying to access or modify the `peer_table` to make sure it works properly under multi-threading structure.

To make the server script more easily to use, I use [click](https://github.com/pallets/click) to create a user friendly command line interface. Users can simply run `python server.py --help` to see every options that can be passed into the server script and the default values.

### Possible Improvements

I use only a single `dictionary` to store the information of every peers. If there are many peers in the system, it might cause a lot of time on `QUERY` request since it needs to go through the table and find any matched file in peers. It's is possible to have a more efficient way to store the information such as two `dictionary`, one maps the peer to their file list and one maps the file to the peer ip address.

## Peer node

For the peer node, we need both clients and servers mechanism at the same time which can be divided to a client that responsible for connecting indexing server, a server that respondible for other peers to download files and serveral clients that try to download files from other peers. I acheive all this by `socket` and `threading`  which are built-in modules in `Python 3` to make all components work indivisually.

The peer script will first try to connect to the indexing server(can be specify by argument). Since the indexing server is necessary to our P2P system, the peer script keep running only if it successfully connects to the indexing server. After connect to the indexing server, it will send a `REGISTER` message to the indexing server with the information of local files and also create a server at the same time listenning to any request of files from other peers. After register with the indexing server, it will start a prompt and waiting for users to enter any instructions(supported instructions: `QUERY`, `WAIT`, `EXIT`). All invalid input will occur an error message and redirect to the prompt again.

`QUERY` instruction plays an important role in the peer script. What it mainly do is passing the filename that the user want to download to the indexing server and wait for response. After receive the ip address that hold the file, the peer script will divided the downloading task to sereval parts based on the `CHUNKSIZE`. It will created several threads to handle the downloading tasks and each handler threads will also get an offset indicates the chunk they are responsible to download.

To support an automatic update mechanism, I use `watchdog` python package. I create another thread and run an `oberver` that keep watching any changes in the hosting folder. It will send an `UPDATE` request to the indexing server whenever it detects any changes.

Due to the fact that the peer node needs at least a client(connecting indexing server) and a server(hosting files for other peers to download), a peer node needs two ports - A(for client) and B(for server). The problem is that for indexing server, it only knows the A port that the peer used to connect to the indexing server so the indexing server won't have any records of the B port. However, other peers need to know the B port from the indexing server to download files. To solve this issue, I make the relation of A and B to be B = A + 1. Port B will always equal to A + 1 so that the other peer nodes can easily calculate the port B by getting port A from indexing server.

To make the server script more easily to use, I use [click](https://github.com/pallets/click) to create a user friendly command line interface. Users can simply run `python peer.py --help` to see every options that can be passed into the peer script and the default values.

### Possible Improvements

I think the way I solve the double port issue might not be very ideal. It will casue some potential errors that multiple peer is trying to use the same port. Users also need to aware that don't start two peers with adjacent port. For example, start a peer on port 50000 and port 50001 will cause an error since that the peer with 50000 will also use 50001 at the same time. Maybe I should not bind a specific port to the client component. I can try to send the port information to the indexing server when register.
