# spntaBot v 1.5.3

spnta is a telegram bot based on [Telepot](https://github.com/nickoala/telepot) & [Siarobo](https://github.com/siyanew/Siarobo) - http://telegram.me/spntaBot


#### spntaBot on Telegram:

- [`@spntaBot`](https://telegram.me/spntaBot)
	- **_channel_**: [`@CRUEL_Project`](https://telegram.me/CRUEL_Project).
* * *

## How to Run ?
First of all install Python >= 3.5 and then install `pip3`.
```
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python3.5
sudo apt-get install python3-pip
```
OR Compile with Source:
```
wget https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz
tar xfz Python-3.5.*
cd Python-3.5.*
./configure --with-ensurepip=install
make
sudo make install
```
Run These commands for Resolving the dependencies.

```
sudo pip3 install pip -U
sudo pip3 install telepot -U
sudo pip3 install aiohttp
sudo pip3 install beautifulsoup4
sudo pip3 install youtube-dl
sudo pip3 install pafy
sudo pip3 install demjson
sudo pip3 install redis
sudo pip3 install pytz
sudo pip3 install six
sudo pip3 install requests --upgrade
sudo pip3 install soundcloud
```

install and start redis-server :
```
sudo apt install redis-server
sudo service redis-server start
```

## Setup

**First of all, take a look at your bot settings**

> * Make sure privacy is disabled (more info can be found by heading to the [official Bots FAQ page](https://core.telegram.org/bots/faq#what-messages-will-my-bot-get)). Send `/setprivacy` to [@BotFather](http://telegram.me/BotFather) to check the current status of this setting.


**in `Terminal`:**

```git clone https://github.com/MOHAMADKHOSHNAVA/spntaBot; cd spntaBot```


**Edite `config.json`:**

> * Set `token` to the authentication token that you received from [`@BotFather`](http://telegram.me/BotFather).
>
> * Set `sudo_members` as a JSON array containing your numerical Telegram ID. Other superadmins can be added too. It is important that you insert the numerical ID and NOT a string.
>


make a screen!
```
screen -S spntaBot
python3 bot.py
```
Ctrl + A + D !

## How to Stop ?
```
screen -r spntaBot
```
Ctrl + C !



### Please
please feel free to ask any questions here by issues or on telegram via [@cruel](https://telegram.me/cruel/)
