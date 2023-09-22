#!/bin/bash

echo -e "\033[0;31mInstalling figlet.\033[0m"
sudo apt-get install figlet

echo
figlet "Website Tracking"
echo

echo -e "\033[4;33mOwner Name: Paresh Maheshwari\033[0m"
echo -e "\033[4;33mGitHub ID: https://github.com/Paresh-Maheshwari\033[0m"

read -p $'\033[0;31mHave you changed the values in the .env file? (y/n) \033[0m' response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

if [ "$response" == "y" ]; then
    echo -e "\033[1;32mInstalling python3.\033[0m"
    sudo apt-get install python3-venv -y

    echo -e "\033[1;32mCreating virtual environment.\033[0m"
    python3 -m venv venv

    echo -e "\033[1;32mActivating virtual environment.\033[0m"
    source venv/bin/activate

    echo -e "\033[1;32mInstalling requirements.\033[0m"
    pip install -r requirements.txt

    echo -e "\033[1;32mCreating migrations.\033[0m"
    python manage.py makemigrations

    echo -e "\033[1;32mCreating database.\033[0m"
    python manage.py migrate

    echo -e "\033[1;32mCreating superuser.\033[0m"
    python manage.py createsuperuser

    echo -e "\033[1;32mStarting server. Go to server IP address on port 8000 to access the site.\033[0m"
    python manage.py runserver 0.0.0.0:8000
else
    echo -e "\033[1;32mPlease change the values in the .env file before running this script.\033[0m"
    nano .env
fi
