# spntaBot

spnta is a telegram bot based on [Telepot](https://github.com/nickoala/telepot) & [Siarobo](https://github.com/siyanew/Siarobo) - http://telegram.me/spntaBot

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
```

Add the bot Token and your id in config.json as a sudo member.

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
