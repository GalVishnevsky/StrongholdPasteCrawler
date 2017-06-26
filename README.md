### Installation

Tor docker installation:
```sh
$ sudo docker run -d -p 8118:8118 -p 9050:9050 rdsubhas/tor-privoxy-alpine
```
Open terminal in current folder

Build and running the docker:
```sh
$ sudo docker build -t stronghold-paste .
$ sudo docker run -d --net host stronghold-paste
```

The db show here:
```sh
127.0.0.1/db
```

The logs show here:
```sh
127.0.0.1/logs
```