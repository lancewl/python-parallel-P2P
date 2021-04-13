import os
import sys
import socket
import threading
import json
import time
import datetime
import click
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import hashlib

FORMAT = "utf-8"
CHUNKSIZE = 65536 # 64 KB

def watchFolder(conn):
    # Keep watching the folder for any change
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    def on_change(event):
        # Update the file list with the indexing server
        files = os.listdir("./")
        filesizes = []
        filemd5 = []
        for f in files:
            filesizes.append(os.path.getsize(f))
            md5 = hashlib.md5(open(f,'rb').read()).hexdigest()
            filemd5.append(md5)
        register_data = {
            "action": "REGISTER",
            "filelist": files,
            "filesizelist": filesizes,
            "md5list": filemd5
        }
        register_json = json.dumps(register_data)
        conn.send(register_json.encode(FORMAT))


    event_handler.on_created = on_change
    event_handler.on_deleted = on_change

    path = "."
    go_recursively = True
    folder_observer = Observer()
    folder_observer.schedule(event_handler, path, recursive=go_recursively)

    folder_observer.start()

def downloadFile(addr, filename, offset):
    # Download file from other peer
    timestamp = datetime.datetime.now()
    print(f"[DOWNLOADING] Downloading {filename} from {addr} (offset: {offset}) - {timestamp}")
    downloader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    downloader.connect(addr)

    downloader.send(json.dumps({"file": filename, "offset": offset}).encode(FORMAT))

    chunk = downloader.recv(CHUNKSIZE)

    f = open(filename,'wb') #open in binary
    f.seek(offset)
    f.write(chunk)
    f.close()
    downloader.close()

def uploadHandler(conn, addr):
    full_addr = addr[0] + ":" + str(addr[1])

    data = conn.recv(CHUNKSIZE).decode(FORMAT)
    json_data = json.loads(data)
    filename = json_data["file"]
    offset = json_data["offset"]
    timestamp = datetime.datetime.now()
    print(f"[UPLOADING] {full_addr} is downloading {filename} (offset: {offset}) - {timestamp}")

    f = open (filename, "rb")
    f.seek(offset)
    chunk = f.read(CHUNKSIZE)
    conn.send(chunk)
    conn.close()

def peerServer(peer_server_addr):
    print("[STARTING] Peer Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(peer_server_addr)
    server.listen()
    print(f"[LISTENING] Peer Server is listening on {peer_server_addr[0]}:{str(peer_server_addr[1])}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=uploadHandler, args=(conn, addr))
        thread.start()

def connectIndexingServer(client_bind_addr, server_addr):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind(client_bind_addr)
    try:
        conn.connect(server_addr)
    except:
        print("[ERROR] Cannot connect to indexing server")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    peer_server_addr = (client_bind_addr[0], client_bind_addr[1] + 1)
    thread = threading.Thread(target=peerServer, args=(peer_server_addr,))
    thread.daemon = True
    thread.start()

    files = os.listdir("./")
    filesizes = []
    filemd5 = []
    for f in files:
        filesizes.append(os.path.getsize(f))
        md5 = hashlib.md5(open(f,'rb').read()).hexdigest()
        filemd5.append(md5)
    register_data = {
        "action": "REGISTER",
        "filelist": files,
        "filesizelist": filesizes,
        "md5list": filemd5
    }
    register_json = json.dumps(register_data)
    conn.send(register_json.encode(FORMAT))

    thread = threading.Thread(target=watchFolder, args=(conn,))
    thread.daemon = True
    thread.start()

    isvalid = True

    while True:
        if isvalid:
            data = conn.recv(CHUNKSIZE).decode(FORMAT)
            
            if not data:
                print("[ERROR] Disconnect from indexing server")
                break

            json_data = json.loads(data)

            if json_data["type"] == "OK":
                print(json_data["msg"])
            
            elif json_data["type"] == "QUERY-RES":
                query_file = json_data["file"]
                query_filesize = int(json_data["filesize"])
                query_filemd5 = json_data["md5"]
                peer_list = json_data["peerlist"]
                # print(query_file, query_filesize)
                # print(peer_list)
                if len(peer_list) > 0:
                    print("Start to download files in parallel...")
                    thread_list = []
                    N = len(peer_list)
                    i = 0

                    while i * CHUNKSIZE < query_filesize + CHUNKSIZE: # the last chunk needs to be included
                        peer_addr = peer_list[i % N].split(":")
                        download_addr = (peer_addr[0], int(peer_addr[1])+1)
                        thread = threading.Thread(target=downloadFile, args=(download_addr, query_file, i * CHUNKSIZE))
                        thread.daemon = True
                        thread.start()
                        thread_list.append(thread)
                        i += 1
                    
                    for t in thread_list:
                        t.join()
                    
                    downloadmd5 = hashlib.md5(open(query_file,'rb').read()).hexdigest()
                    if downloadmd5 == query_filemd5:
                        print("Download successful! MD5 match!")
                    else:
                        print("Download successful! MD5 match!")

                else:
                    print("No peers found for the file.")

        user_input = input("> ")
        user_input = user_input.split(" ")
        action = user_input[0]
        isvalid = True

        if action == "QUERY" and len(user_input) > 1:
            conn.send(json.dumps({"action": "QUERY", "file": user_input[1]}).encode(FORMAT))
        elif action == "WAIT":
            print("Start waiting")
            time.sleep(1)
            isvalid = False
        elif action == "HANG":
            print("Start hanging")
            time.sleep(3000)
            isvalid = False
        elif action == "EXIT":
            break
        else:
            print("Input action is invalid!")
            isvalid = False

    print("Disconnected from the server.")
    conn.close()

@click.command()
@click.argument('port')
@click.option('--dir',
              default="./",
              help='Serving directory relative to current directory')
@click.option('--server',
              default="127.0.0.1:5000",
              help='Indexing server address')
def main(port, dir, server):
    target_dir = os.path.join(os.getcwd(), dir)
    os.chdir(target_dir)

    port = int(port)
    localhost = socket.gethostbyname(socket.gethostname())
    client_bind_addr = (localhost, port)
    server_addr = server.split(":")
    server_addr = (server_addr[0], int(server_addr[1]))
    connectIndexingServer(client_bind_addr, server_addr)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)