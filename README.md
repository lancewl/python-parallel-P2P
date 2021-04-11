# Python P2P System with Parallel Data Transfer

## Requirement

* Python 3.7 and above

## Installation

### [pip](https://pip.pypa.io/en/stable/)

```bash
pip install requirements.txt
```

### [pipenv](https://pipenv.kennethreitz.org/en/latest/#) 

Use pipenv to manage and install the Python packages.

```bash
pipenv install
```

## Usage

### Indexing Server Script

The `server.py` will start an indexing server for the P2P system.

```bash
Usage: server.py [OPTIONS]

Options:
  --port TEXT  Hosting port (default 5000)
  --help       Show this message and exit.
```

Example:

```bash
python server.py --port 5000
```

Above command will start the indexing server on port 5000.

### Peer Script

The `peer.py` will start a peer node in the P2P system.

```bash
Usage: peer.py [OPTIONS] PORT

Options:
  --dir TEXT     Serving directory relative to current directory
  --server TEXT  Indexing server address
  --help         Show this message and exit.
```

Example:

```bash
python peer.py --dir data1 50001
```

Above command will start a peer node and host on port 50001.

### Evaluation Scripts

The `eval2.sh` will evaluate the performance of QUERY action under different number of peers.

```bash
Usage: ./eval.sh [Peer Count]
```

The `eval3.sh` will evaluate the performance of downloading files from other peers under different file size.

```bash
Usage: ./eval.sh [File Size]
```
