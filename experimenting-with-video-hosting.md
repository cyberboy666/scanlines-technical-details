
# exploration into peertube

![image](https://user-images.githubusercontent.com/12017938/83358884-e9129900-a376-11ea-84ef-f79f693a224b.png)

i started thinking about alternatives to youtube/vimeo for online video hosting. a few reasons for this:

- on scanlines (since its about av) presumably we want to share video sometimes. right now the forum doesnt support video uploads, one would need to go and upload it somewhere else first (compared to the convenience of facebook where they handle this)
- i would like to have my videos hosted somewhere online with less tracking, advertising , corporate control. maybe some others would too ?
- feeling empowered by the success of our self-hosted forum, chatroom and streaming server ! maybe videos is a logical next step for video-artists ?
- people often complain about the compression algorithms etc with uploading videos. self-hosting may give some more control here (not sure)

one concern i had was that the amount of diskspace needed to host videos for even a small community might become quite expensive. at digital ocean you pay $10 a month for 100Gb. depending on the use this could be used up quite fast. a model like this would only really work if a group of people were financially committed to it from the beginning (which im not really interested in orginising rn)

however static object storage like s3 is cheaper than provisioning diskspace on a virtual machine. if this was compatible and performant enough then it could make it affordable even just as a place to host my own videos (cheaper than a single vimeo pro account !)

## the plan

i had been reading about [peertube](https://joinpeertube.org/) - a free and decentralized alternative to video platforms like youtube. it is federated with [ActivityPub](https://en.wikipedia.org/wiki/ActivityPub) to communicate not just between different peertube servers , but also other networks in the [fediverse](https://fediverse.party/). 

it looks like peertube [can be used](https://docs.joinpeertube.org/#/admin-remote-storage) with remote storage, by using FUSE / [s3fs](https://github.com/s3fs-fuse/s3fs-fuse) , an application for mounting s3 buckets, and treating them like harddrives. i want to try mounting a [wasabi](https://wasabi.com/) bucket (which is compatable with s3) because they offer 1Tb of storage for ~$5per month.

# setting up peertube

![image](https://user-images.githubusercontent.com/12017938/83357896-a6998e00-a36f-11ea-8261-9ab3e42e9f1b.png)

- first i created a new digital ocean droplet (with ubuntu18.04.3) - choosing the cheapest ($5 per month) machine with 1Gb CPU/RAM and 25Gb SSD. 
- then added a new subdomain pointing to this droplets ip
- next `ssh` into the droplet and begin installing the peertube depedancies:

- download and install node and yarn: 
```
curl -sL https://deb.nodesource.com/setup_10.x | bash -
sudo apt install -y nodejs
curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install -y yarn
yarn --version
```

- next ffmpeg, database and other dependancies:
```
sudo apt install -y ffmpeg nginx-full certbot python3-certbot-nginx postgresql postgresql-contrib redis-server
ffmpeg -version # Should be >= 3.x
g++ -v # Should be >= 5.x
```

- now start postgres and redis:
```
sudo systemctl start redis-server 
sudo systemctl start postgresql
sudo systemctl enable redis-server
sudo systemctl enable postgresql
```

- create peertube user/password and postgres user and password - _the default postgres username and password is __peertube__ -   i would just use these to get started_:
```
sudo useradd -m -d /var/www/peertube -s /bin/bash -p peertube peertube
sudo passwd peertube
sudo -u postgres createuser -P peertube
sudo -u postgres createdb -O peertube -E UTF8 -T template0 peertube_prod

# add postgres extensions:
sudo -u postgres psql -c "CREATE EXTENSION pg_trgm;" peertube_prod
sudo -u postgres psql -c "CREATE EXTENSION unaccent;" peertube_prod
```
- now that we have the dependancies we can start with the _peertube_ code itself:
```
# get version
VERSION=$(curl -s https://api.github.com/repos/chocobozzz/peertube/releases/latest | grep tag_name | cut -d '"' -f 4) && echo "Latest Peertube version is $VERSION"
# create dir
cd /var/www/peertube && sudo -u peertube mkdir config storage versions && cd versions
# download code
sudo -u peertube wget -q "https://github.com/Chocobozzz/PeerTube/releases/download/${VERSION}/peertube-${VERSION}.zip"
# unzip
sudo -u peertube unzip peertube-${VERSION}.zip && sudo -u peertube rm peertube-${VERSION}.zip
# link version to lastest
cd ../ && sudo -u peertube ln -s versions/peertube-${VERSION} ./peertube-latest
# use yarn to collect packages:
cd ./peertube-latest && sudo -H -u peertube yarn install --production --pure-lockfile
```

- now we can create and configure the _config_ file:
```
cd /var/www/peertube && sudo -u peertube cp peertube-latest/config/production.yaml.example config/production.yaml
nano /var/www/peertube/config/production.yaml
```

![image](https://user-images.githubusercontent.com/12017938/83358209-3d674a00-a372-11ea-9f70-6c9be9059511.png)

there are lots of settings in this file. the main thing you need to set now is the _hostname_ to what you used for you registar earlier. you should come back here and tweak some things later (for example the SMTP server to send emails). if you didnt use _peertube_ as db name and password can update this here too.

- next is to setup the nginx webserver:

```
sudo cp /var/www/peertube/peertube-latest/support/nginx/peertube /etc/nginx/sites-available/peertube
sudo ln -s /etc/nginx/sites-available/peertube /etc/nginx/sites-enabled/peertube
nano /etc/nginx/sites-available/peertube
```

![image](https://user-images.githubusercontent.com/12017938/83358367-43a9f600-a373-11ea-980f-9c38b5d847ee.png)

it is worth taking a look inside the nginx config file also - just to have some idea what is happening. you should now comment out the _ssl_certificate_ and _ssl_certificate_key_ lines in here. you will notice there are a few places where the domain is `peertube.example.com` , this needs to be updated to the _hostname_ you set eariler. to save doing this manually you can run this command (where `$DOMAIN_NAME` is replaced with your domain):

```
sed -i "s/peertube.example.com/"$DOMAIN_NAME"/g" /etc/nginx/sites-available/peertube
```

- next we will install the letsencrypt certs for https:

```
sudo systemctl stop nginx
sudo certbot --authenticator standalone --installer nginx --post-hook "systemctl start nginx"
```

this will ask for an email and some options (like redirect for http). after this open the nginx config again ( `nano /etc/nginx/sites-available/peertube` ) and uncomment the two  _ssl_ lines from earlier.

_nginx_ should be running now. you can check the syntax with `sudo nginx -t` ; if you open your _hostname_ in a browser you should see the nginx landing page.

- it is a good idea to enable the firewall:
```
sudo ufw status
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

- some fine tuning of TCP
```
sudo cp /var/www/peertube/peertube-latest/support/sysctl.d/30-peertube-tcp.conf /etc/sysctl.d/
sudo sysctl -p /etc/sysctl.d/30-peertube-tcp.conf
```

- copy the systemd file to start peertube on boot, and (finally) __start peertube__ ! _note - once you start it you can not change the domain name so be sure it is how you want it , or be prepared to do all of this again_

```
sudo cp /var/www/peertube/peertube-latest/support/systemd/peertube.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable peertube
sudo systemctl start peertube
```

now take a look into the logs, you should see a bunch of info including:
- that the mail client is not set
- user creation and password for _root_ account (admin)
- the server is listening on __localhost:9000__

```
sudo journalctl -feu peertube
```

if all went well you should be able toe reach _peertube_ through your chosen domain name. by logging in as root with the password in the logs above you can access the admin panel and play around with some different settings there.

# setting up external static object storage

first i created an account on wasabi. from here you can create and download your _accesskey_ and _secret_.

next on the droplet i installed s3fs from source because was having some problems with the version i tried from the package mananger. maybe first you could try it with `sudo apt install s3fs` and to check the version. otherwise from source (for V1.86 commit:0cb057d):

```
cd /usr/src/
sudo apt-get install build-essential git libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool
sudo apt-get install pkg-config libssl-dev
git clone https://github.com/s3fs-fuse/s3fs-fuse
cd s3fs-fuse/
./autogen.sh
./configure --prefix=/usr --with-openssl
make
sudo make install
```

then i created a file for my key and secret:

- `nano /etc/passwd-s3fs`
- in this file put your key and secret seperated by a colon: `<accesskey>:<secret>`
- update permissions: `chmod 600 /etc/passwd-s3fs`

_NOTE: this next part differs from the [instructions from peertube](https://docs.joinpeertube.org/#/admin-remote-storage). i tried it this way but couldnt get it to work. mounting the s3 drive seemed to overwrite the link between folders and viceversa. so any way i tried it just didnt work. maybe someone will show me how it is meant to be done_

![image](https://user-images.githubusercontent.com/12017938/83361000-b623d180-a385-11ea-87ec-8026cd74e5a3.png)

my workaround: 

- create a bucket for each of the folders we want to store on _wasabi_: __videos__ , __redundancy__ , __streaming-playlists__
- make these buckets public in the settings (i needed to request public bucket feature from support on a trial account)
- make a policy for each bucket that makes every item in it public also:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::scanlines-videos/*"
    }
  ]
}
```

now back in the droplet, mount the buckets (take care of the bucket name and the _region_ in the url is same as your buckets):
```
s3fs scanlines-videos /var/www/peertube/storage/videos -o passwd_file=/etc/passwd-s3fs -o url=https://s3.eu-central-1.wasabisys.com -o allow_other -o use_path_request_style -o uid=1000 -o gid=1000

s3fs scanlines-redundancy /var/www/peertube/storage/__redundancy__ -o passwd_file=/etc/passwd-s3fs -o url=https://s3.eu-central-1.wasabisys.com -o allow_other -o use_path_request_style -o uid=1000 -o gid=1000

s3fs scanlines-streaming-playlists /var/www/peertube/storage/streaming-playlists -o passwd_file=/etc/passwd-s3fs -o url=https://s3.eu-central-1.wasabisys.com -o allow_other -o use_path_request_style -o uid=1000 -o gid=1000
```

you can test the mount with the command `mount` - at the bottom the _s3fs_ can be seen. you can also test it by creating a file in one of these folders and seeing it in the wasabi console.

![image](https://user-images.githubusercontent.com/12017938/83361131-a5279000-a386-11ea-89c2-244a065065a7.png)

finally you can try uploading a video in the peertube app. you should see the file both in the `/var/www/peertube/storage/videos` folder on the droplet and in the wasabi manager.

![image](https://user-images.githubusercontent.com/12017938/83361206-4b739580-a387-11ea-8916-fbccf1e1f082.png)

the video should play in peertube, but there is one more step - updating the _nginx_ conf to serve the video directly from the bucket (rather than through the mount point):

open the config ( `nano /etc/nginx/sites-available/peertube` ) and near the bottom , above the existing static rewrite and below the `root /var/www/peertube/storage;` setting add these lines:

```
set $cdn https://s3.eu-central-1.wasabisys.com;
rewrite ^/static/webseed/(.*)$ $cdn/scanlines-videos/$1 redirect;
rewrite ^/static/redundancy/(.*)$ $cdn/scanlines-redundancy/$1 redirect;
rewrite ^/static/streaming-playlists/(.*)$ $cdn/scanlines-streaming-playlists/$1 redirect;
```

(take care that the bucket names and region match what is in wasabi)

![image](https://user-images.githubusercontent.com/12017938/83361301-1582e100-a388-11ea-8f83-9bbb36f15431.png)

- (check nginx `nginx -t` and) restart: `sudo systemctl restart nginx`

now double check that the video still plays in peertube. 

![image](https://user-images.githubusercontent.com/12017938/83361366-c4272180-a388-11ea-980c-40298abc62fb.png)

