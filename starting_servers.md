# more details coming soon

## fixing rocketchat 

just a quick note on what i did (will write all this nicer another day)

- checking the dashboards on digital ocean and seeing memory drop

![image](https://user-images.githubusercontent.com/12017938/80652398-16b6aa80-8a78-11ea-89a6-3527a096c327.png)
(this was taken later in the day)

- ssh into the machine
- first i just tried a reboot: `reboot` in the console
- this didnt seems to work (actually it did but the app crashed again for some reason)
- next i tried resizing the droplet and also looking how to start and see what was running on the machine
- run the command `netstat -tulpn` to see what was running:

![image](https://user-images.githubusercontent.com/12017938/80651025-647de380-8a75-11ea-870d-2aa3152aa682.png)

- i knew that rocketchat (node process) should be running on port 3000 but wasnt..
- [this tutorial](https://rocket.chat/docs/installation/manual-installation/ubuntu/) was helpful for finding where to find rocketchat files (`/opt/Rocket.Chat`) and service were located... (the service wasnt in `/etc/systemd` like i was expecting... but `/lib/systemd/system/rocketchat.service`)

- running `systemctl status rocketchat` should show that the service isnt running.
- i ran `sudo systemctl enable rocketchat && sudo systemctl start rocketchat` and then check the status again to see it was good : 

![image](https://user-images.githubusercontent.com/12017938/80651645-8deb3f00-8a76-11ea-90b6-25a3238227f2.png)

and then check the active services again to see the node process on port 3000:

![image](https://user-images.githubusercontent.com/12017938/80651693-abb8a400-8a76-11ea-8f9c-a679e6953fb7.png)
