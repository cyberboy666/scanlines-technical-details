# setting up a streaming server

## background

based on [some threads](https://scanlines.xyz/t/streaming-server-intentions-and-ideas/82) on the forum we want to have a recurring performance event there. in an effort to have more control over the stream, to avoid using proprietary software / pushing non-free js&tracking cookies and to learn something new we decided to try setting this up ourself. 

## existing infrastructure

currently we are hosting the site on two digital-ocean droplets -> one for the forum and another for the chatroom. this configuration just ensures that the forum (the main focus) is always stable and we can use the second droplet for experimenting. (for example the auth-bridge runs on the chat-droplet, and im thinking of putting some kind of facebook-group intergration on there too...)

we want to have the streaming functionality set up on this second _chat_droplet_ too - this means we dont pay for an idle machine when nothing is streaming and that we can easily turn on streaming and expand the size of this virtual machine just for the duration of an event, if we need too.

## the approach

following closely [this video](https://www.youtube.com/watch?v=Y-9kVF6bWr4) which is based around [this guide](https://docs.peer5.com/guides/setting-up-hls-live-streaming-server-using-nginx/) the idea is to use this [rtmp module for nginx](https://github.com/sergey-dryabzhinsky/nginx-rtmp-module) to serve a stream over the web.

## installing / getting started

- i started in my user folder `cd /home/tim/`
- clone the module onto the server `git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git`
- installing nginx dependencies `sudo apt-get install build-essential libpcre3 libpcre3-dev libssl-dev zlib1g-dev`
- download latest nginx source (we need to compile this ourself to include the rtmp-module) `wget http://nginx.org/download/nginx-1.18.0.tar.gz`
- extract, remove tar and cd into folder
```
tar -xf nginx-1.18.0.tar.gz
rm nginx-1.18.0.tar.gz
cd nginx-1.18.0
```
- from here we can configure it including the rtmp module, and then build and install
```
./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
make
sudo make install
```

## nginx config

you should find the config file here `/usr/local/nginx/conf/nginx.conf` , first i deleted the default (it is already backed up in there incase you need it) `rm /usr/local/nginx/conf/nginx.conf` then created a new one `nano /usr/local/nginx/conf/nginx.conf` and pasted in the configuration from the guide i was following:

![image](https://user-images.githubusercontent.com/12017938/82033790-898d6b80-969d-11ea-927e-22213779eef3.png)

this is the config file we started with - i highlighted the parts i changed from the peer5 guide:

- setting the hls path
- disabling aio
- setting the access-logs (only if you want this - it helped me figure out the mapping)
- setting the root dir

in this file we can see two configurations - first is for the _rtmp_ , listening on __port 1935__ and buffering the hls stream. the second is a _http_ route on __port 8080__ which is used to serve the stream file. there are more configurations we can try out here but for now this we enough to get something going

- test the configuration `/usr/local/nginx/sbin/nginx -t` and then start nginx `/usr/local/nginx/sbin/nginx`

## open broadcaster software

the idea is for artists to send their performance to the streaming server using the _rtmp streaming protocol_. the best way to do this it seems is using [OBS STUDIO](https://obsproject.com/)

i downloaded the application, and in it started playing some media (a kind of [hello world](https://www.nytimes.com/1993/05/24/business/cult-film-is-a-first-on-internet.html) for art-streaming ?)

![image](https://user-images.githubusercontent.com/12017938/82035789-53052000-96a0-11ea-96d7-5090b0992913.png)

next step was to choose _settings -> stream_ and then set _service -> custom_ and to point to the streaming server ___rtmp://<server_ip>/show__ (show is the name we gave in the rtmp config above but this could be anything)

the streaming key is the name of the file that will be served on the front-end (this should be hard to guess to avoid stream hijacking - although still dont really get how this helps if it is served in client javascript anyway ??)

![image](https://user-images.githubusercontent.com/12017938/82035801-55677a00-96a0-11ea-8a83-75738bc54d2e.png)


for now just a dump so i can close some tabs:

- 
- 
- https://github.com/lebinh/ngxtop
- sudo ufw allow 1935
