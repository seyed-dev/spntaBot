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
		sudo add-apt-repository ppa:fkrull/deadsnakes
		sudo apt-get update
		sudo apt-get install python3.5
		sudo apt-get install python3-pip
	fi
  
	echo -en "${Cyan}Do you want to pip packages (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
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
    sudo pip install pytesseract
    sudo pip3 install Image
  fi
 

	echo -en "${Cyan}Do you want to download the tesseract-ocr libraries (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
		for ROCK in $ROCKS; do
			sudo apt-get install tesseract-ocr
		done
  fi

	echo -en "${Cyan}Do you want to download the redis libraries (Y/N): ${Default}"
	read REPLY
	if [[ $REPLY == [yY] ]]; then
		for ROCK in $ROCKS; do
			sudo apt install redis-server
      sudo service redis-server start
		done
  fi

	if [ ! -d .git ]; then
		echo -en "${Green}Would you like to clone the source of acrcloud sdk python? (Y/N): ${Default}"
		read REPLY
		if [[ $REPLY == [yY] ]]; then
			echo -en "${Orange}Fetching latest acrcloud sdk python source code\n${Default}"
			git clone https://github.com/acrcloud/acrcloud_sdk_python && cd acrcloud_sdk_python && python3 setup.py install && cd ..
		fi
  fi


	echo -en "${BGreen}SpntaBot successfully installed! Change values in config file and run ${BRed}./launch.sh${BGreen}.${Default}";;
	*) echo "Exiting...";;
esac
