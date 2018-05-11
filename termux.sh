#!/usr/bin/env bash


# Color variables
Red='\033[0;31m'
Green='\033[0;32m'
Orange='\033[0;33m'
Blue='\033[0;34m'
Purple='\033[0;35m'
Cyan='\033[0;36m'
BRed='\033[1;31m'
BGreen='\033[1;32m'
BOrange='\033[1;33m'
BBlue='\033[1;34m'
BPurple='\033[1;35m'
BCyan='\033[1;36m'
Default='\033[0m'


read -p "Do you want me to install Spnta Bot? (Y/N): "

case $REPLY in [yY])
	# Install Python
	echo -en "${Blue}The packages will be installed:${Default} ${NATIVE}\n${Cyan}Do you want to install the python (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
		pkg install python3.5
	fi
  
	echo -en "${Cyan}Do you want to pip packages (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
    		pip3 install pip -U
    		pip3 install telepot -U
    		pip3 install aiohttp
    		pip3 install beautifulsoup4
    		pip3 install youtube-dl
    		pip3 install pafy
    		pip3 install demjson
    		pip3 install redis
    		pip3 install pytz
    		pip3 install six
    		pip3 install requests --upgrade
    		pip3 install soundcloud
    		pip install pytesseract
    		pip3 install Image
    		pip3 install telethon
	fi
 

	echo -en "${Cyan}Do you want to download the tesseract-ocr libraries (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
		for ROCK in $ROCKS; do
			pkg install tesseract-ocr
			pkg install nano
		done
	fi

	echo -en "${Cyan}Do you want to download the redis libraries (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
		for ROCK in $ROCKS; do
			pkg install redis-server
		done
	fi

	if [ ! -d .git ]; then
		echo -en "${Green}Would you like to clone the source of acrcloud sdk python? (Y/N): ${Default}"
		read REPLY
		if [[ $REPLY == [yY] ]]; then
			echo -en "${Orange}Fetching latest acrcloud sdk python source code\n${Default}"
			git clone https://github.com/acrcloud/acrcloud_sdk_python && cd acrcloud_sdk_python && python setup.py install && cd ..
		fi
	fi


	echo -en "${BGreen}SpntaBot successfully installed! Change values in config file";;
	*) echo "Exiting...";;
esac
