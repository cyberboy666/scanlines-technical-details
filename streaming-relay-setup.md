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

also need to create the folders where the stream files will go:
```
mkdir /nginx
mkdir /nginx/live
chown -R www-data:www-data /nginx
```

finally test the configuration `/usr/local/nginx/sbin/nginx -t` and then start nginx `/usr/local/nginx/sbin/nginx`

## add to firewall

we are using _ufw_ on this droplet. to allow streaming to it we need to allow the rtmp port here:

```
ufw allow 1935
```

## open broadcaster software

the idea is for artists to send their performance to the streaming server using the _rtmp streaming protocol_. the best way to do this it seems is using [OBS STUDIO](https://obsproject.com/)

i downloaded the application, and in it started playing some media (a kind of [hello world](https://www.nytimes.com/1993/05/24/business/cult-film-is-a-first-on-internet.html) for art-streaming ?)

![image](https://user-images.githubusercontent.com/12017938/82035789-53052000-96a0-11ea-96d7-5090b0992913.png)

next step was to choose _settings -> stream_ and then set _service -> custom_ and to point to the streaming server ___rtmp://<server_ip>/show__ (show is the name we gave in the rtmp config above but this could be anything)

the streaming key is the name of the file that will be served on the front-end (this should be hard to guess to avoid stream hijacking - although still dont really get how this helps if it is served in client javascript anyway ??)

![image](https://user-images.githubusercontent.com/12017938/82035801-55677a00-96a0-11ea-8a83-75738bc54d2e.png)

now i can press _start streaming_ in obs and if all is correct it should start streaming! from inside the droplet can check what is in the folders we just created: `ls /nginx/live` -> you should see some _.ts_ fragments and a _test.m3u8_ file (this file is the name of your streaming key)

to try and play this stream i opened up vlc player, and went to _open network_

![image](https://user-images.githubusercontent.com/12017938/82040310-b7c37900-96a6-11ea-8c64-42b8c7a3cae4.png)

this is where we use the http config on port 8080 in the nginx file above

![image](https://user-images.githubusercontent.com/12017938/82040645-328c9400-96a7-11ea-9812-b8c1e98c425f.png)

and there it is ! (the framerate for this test was very low but i think this was a problem on the obs side since it was saying _dropped frames: 85%_ or something -> need to configure this a bit i think, having never done a stream before)

## https and routing

this is the basics already set up ! however if we want to embed the stream on a https site we need to serve this streaming file also over https. if you are setting this streaming service up on a fresh machine then i would recommend following the video i linked above -> this shows setting a_records for a custom domain and installing _lets_encrypt_ to generate ssl certs and linking them in the nginx config.

for us however we already have a domain (_chat.scanlines.xyz_ ) pointing to this droplets ip and have ssl certs installed to serve over https. this is all being handled by _traefik_ listening on __port 43__. already when setting up the [auth-bridge](https://github.com/langolierz/auth-rocketchat-from-discourse) i had added a path_prefix rule to send all requests on the extension `/auth` to my flask-app on __port 5000__. for this i just added another path_prefix rule to send all requests on the `/live` extension to __port 8080__ which our nginx is listening on. (maybe it would be nice to route directly to the stream in _traefik_ and bypass the nginx http server, but this way we can explore some other intergrations for the nginx rtmp-module)

- to edit traefik route: `sudo nano /etc//traefik/traefik.toml`

![image](https://user-images.githubusercontent.com/12017938/82042006-6f598a80-96a9-11ea-80ff-240bc92c2f61.png)

## nginx monitoring

at this point i could see that _traefik_ was passing the request to _nginx_ but my attempt to access the stream over https at `https://chat.scanlines.xyz/live/hls/test.m3u8` would serve a (nginx) not found. the reason was because i originally had the stream file in the dir `/nginx/hls/test.m3u8` (as in the video i was following). this worked when accessing the nginx port directly (`<server0ip>:8080/hls/test.m3u8`) however it didnt work when passing the path extension from _traefik_ -> i didnt realise that the whole path was being passed through so _nginx_ was now looking for the file at `/live/hls/test.m3u8`. i fixed this by just renaming the folder that the stream saves to -> now it is in `/nginx/live/` and we dont need hls in the path at all.

however in order to figure this out i needed to find the nginx _access_logs_. these can be found in `/var/log/nginx/nginx-access.log`. a nice tool i found to view them is [ngxtop](https://github.com/lebinh/ngxtop) , which can be installed with `apt install python-pip; pip install ngxtop`, then started with `ngxtop -l /var/log/nginx/nginx-access.log`

![image](https://user-images.githubusercontent.com/12017938/82043399-d0825d80-96ab-11ea-8715-e13f0e43b41d.png)

from here i could easily see the problem with the path mismatch

## displaying the stream on our site

- videojs as player ?
- "custom theme component as a github repo and include the video.js source there, then "install from repo""
- wip
