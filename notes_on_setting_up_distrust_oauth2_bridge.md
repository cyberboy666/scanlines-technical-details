to use a scanlines account as an identity provider for vidicon festival we wanted to set up [distrust](https://github.com/Parkour-Vienna/distrust) - which is a bridge between discourse-connect and an oauth2/open_id flow.

what following is an example / step-by-step setup  guide to how i set up a _distrust_ auth server:

## creating the server

i already use [digital ocean](https://www.digitalocean.com/) for a number of other online projects, so will just spin up a new droplet here:

![image](https://user-images.githubusercontent.com/12017938/195707458-d8702dd1-cc34-432f-96a7-0c5377d31f6a.png)

this is just for testing - will be teared down in some days - so provisioning a small machine is fine. im running ~~Ubuntu 22.04 x64~~. __Ubuntu 20.04.4 LTS__ (NOTE: i had two critical fails where i could not ssh into the machine - one before the distrust container was even pulled - so i decided to see if downgrading ubuntu helps with this)

once the droplet has been created (and password set) i copy the ip adress and go to [porkbun](https://porkbun.com/) who i use for domain registry. from here i can add a new __a record__ that points the subdomain _auth.cyberboy666.com_ to the ip of this droplet

![image](https://user-images.githubusercontent.com/12017938/195709188-582325eb-db89-4f84-ad93-cf188f5c5589.png)

now we can ssh into the droplet to configure it from there - open a terminal on your computer and put in:
```
ssh root@<droplet-ip>
```
and enter the droplet password when prompted. 

## nginx and letsencrypt

the first things i will set up on this new machine is [ngnix](https://nginx.org/en/) - this is a reverse-proxy that is used to route incoming traffic to the server to whichever interal application you want - i followed [this](https://www.digitalocean.com/community/tutorials/how-to-configure-nginx-as-a-reverse-proxy-on-ubuntu-22-04) guide from digital ocean:

```
sudo apt update
sudo apt install nginx -y
```

add nginx to the firewall and enable it

```
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

create the nginx configuration - make sure you replace any `<your-domain>` withthe name of the domain you are using (eg for me i would put in _auth.cyberboy666.com_):
```
sudo nano /etc/nginx/sites-available/<your-domain>
```

and then paste the following config in (you will see why we are routing all incoming traffic to port 3000 in a little bit):

```
server {
    listen 80;
    listen [::]:80;

    server_name <your-domain>;
        
    location /oauth2/ {
        proxy_pass http://127.0.0.1:3000;

        include proxy_params;
    }
}
```
we also only route traffic on the endpoint `oauth2` here to port 3000. this is to use nginx to reject any other requests eg from bots poking around. 

make a link of this to the _sites_enabled_ then test your config:
```
sudo ln -s /etc/nginx/sites-available/<your-domain> /etc/nginx/sites-enabled/
sudo nginx -t
```
if there are no problems the output will read:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

that means we can restart nginx: `sudo systemctl restart nginx` and test it is working by putting your domain name into a web-browser (http):

![image](https://user-images.githubusercontent.com/12017938/195729476-e7bbe91c-21a3-4baa-86b5-67af9b924744.png)


you should get a _ngnix_ bad-gateway with a little padlock to show the connection is unsecure.

next we will make it secure with [letsencrypt](https://letsencrypt.org/) - i followed [this](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04) guide from digital ocean. first we will make sure _snap_ is installed and then install and link certbot:

```
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

now lets obtain the SSL certificate for our domain and let it configure for nginx:

```
sudo certbot --nginx -d <your-domain>
```
you will be prompted to accept conditions and enter an email address then you should receive a message 
_Successfully received certificate_. we can also test now that the renewal process is set up correctly:

```
sudo certbot renew --dry-run
```

lets test this has worked by going to `<your-domain>` in a web-browser:
    
![image](https://user-images.githubusercontent.com/12017938/195716351-d83f4186-b977-41bd-ac52-f0ec7d8a1047.png)

horray for a _secure_ bad gateway !

## distrust config

we will run _distrust_ from the docker image - but still need to download and set up the config:
```
wget https://raw.githubusercontent.com/Parkour-Vienna/distrust/master/distrust.example.yml
mv distrust.example.yml distrust.yml
```

for the first part of the `distrust.yml` we need to enter the discourse-server and secret - server is just the full domain name (so in my case it would be `https://scanlines.xyz`) the secret is something you can generate (use a password manager for random secrets) - this needs to be set in the discourse admin settings:

![image](https://user-images.githubusercontent.com/12017938/195721425-3ac94a20-e9bd-4507-9412-43dc64e64621.png)

put this into your distrust config with `nano distrust.yaml` (use ctrl-x to save and quit nano)

next we need to create oidc secret and private key to put into _distrust.yaml_ - the secret needs to be exactly 32bytes. for this i used python secrets module to generate (and check byte length):
```
python3
>>>
import secrets
s=secrets.token_hex(16)
len(s.encode('utf-8'))
print(s)
```
next we need to generate an RSA private key (i called mine `distrust` and left passphase empty):
```
ssh-keygen -t rsa -m PEM

```
we need to ensure this key has _4 space indents_ for the yml file syntax - i just copied the key from `nano distrust` and pasted it into vscode where i added indent and copy/pasted back into `distrust.yml`

final step is to configure the clients. make sure the `test` part is replaced with your clients name. add/ create their secret and put in the callback url. i removed the `allowGroups` line for now

## install and run docker

last time i was installing lastest docker from docker repo - but after a critcal failure i will try again running whatever version comes with snap (20.10.14) i didnt want to waste too much time investigating the reason for those errors since this setup will be teared down in some days anyway:
    
```
sudo snap install docker
docker --version
```
now lets start the _distrust_ container (could replace `0.0.5` with `master` to ensure you are running latest):
```
docker run -d --name distrust -v $PWD/distrust.yml:/distrust.yml:Z -p 3000:3000 ghcr.io/parkour-vienna/distrust:0.0.5
```
if it worked you should see the container running when you type `docker container ls`:
```
CONTAINER ID   IMAGE                                   COMMAND       CREATED              STATUS              PORTS                                       NAMES
2256567f8d9f   ghcr.io/parkour-vienna/distrust:0.0.5   "/distrust"   About a minute ago   Up About a minute   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   distrust
```
if your container is not shown here you can see all containers with `docker container ls -A` - to see the logs for this container type in `docker logs distrust` (possible reason could be formating error in the config file)

we can test this is working by making a call to the distrust server by putting `<your-domain>/oauth2/auth`:

![image](https://user-images.githubusercontent.com/12017938/195731523-b9c221aa-6333-4a41-95bd-a3adb4dbe8f7.png)

the error now is not from _nginx_ but _distrust_ -> since we dont pass in a valid client_id. this means everything is up and running and ready to test my oauth2-client against !
