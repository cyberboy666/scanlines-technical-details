# embedded chat window for discourse

[paloma](https://github.com/doubleobelisk) created an embedded chat window for the scanlines forum (discourse) that lets you open up to and use also the scanlines chat (rocket.chat) 

![Screenshot from 2021-07-19 23-55-11](https://user-images.githubusercontent.com/12017938/126156331-f4af8361-5832-4ae4-992b-d88bd9db7c48.png)

this was added to discourse as a __theme component__ ,which can be reached under _customize_ in the admin panel

![Screenshot from 2021-07-19 23-58-05](https://user-images.githubusercontent.com/12017938/126156584-7637b134-1a2a-433d-8de5-5226a155dc6c.png)

here is the code from inside this component (only made for _destop_):

### css

```
.collapsible {
    height: 570px;
    width: 500px;
    float: right;
    position:fixed;
    bottom: -540px;
    right: 0;
    z-index:10000;
}

.active_chat {
    position:fixed;
    bottom:0;
}

.chat_header {
    height: 20px;
    width: 478px;
    position:relative;
    padding: 5px 10px;
    background-color:white;
    border: 1px solid black;
    text-align:left;
    color:black;
}

.chat_header a {
    color:black;
}

.chatbutton.active {
    -webkit-box-shadow: none;
	-moz-box-shadow: none;
	box-shadow: none;
}

.chatbutton {
    outline:none;
    float:right;
    position: absolute;
    right: 5px;
    border:none;
    background: none;
}

.chat_container {
    width: 498px;
    height: 537px;
    border: 1px solid black;
    border-top: none;
    background:#2f343d;
}


.chat_embed {
    width: 100%;
    height: 100%;
    border-style:none;
}

```

### \</body>

```
<div class="collapsible">

<div class="chat_header">
<a href="https://chat.scanlines.xyz" target="_blank">chat.scanlines.xyz</a>
<button type="button" class="chatbutton">show</button>
</div>

<div class="chat_container">
</div>

</div>

<script>
var coll = document.getElementsByClassName("chatbutton");
var i;
var content_toggle = true;
document.getElementsByClassName("chat_container").innerHTML='';

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
      var x = this.parentElement.parentElement.classList.toggle("active_chat");
      var content = this.parentElement.nextElementSibling;
      content_toggle = !content_toggle
    if (content_toggle == false) {
        this.innerHTML = 'hide'
        content.innerHTML = '<iframe src="https://chat.scanlines.xyz/channel/general" class="chat_embed"></iframe>';
    } else {
        this.innerHTML = 'show'
        content.removeChild(content.firstChild);
    }
  });
}
</script>
```
