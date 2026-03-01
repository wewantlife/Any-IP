# Any-IP | English
The "Any-IP" utility helps you find out the IP address of a person who connects to your computer via Anydesk, and also shows approximate geolocation.

# Any-IP | Russia
Утилита " Any-IP " Помогает узнать айпи человека который подключается к вашему компьютеру через Anydesk, также показывает примерную геолокацию.

# Build
git clone https://github.com/wewantlife/Any-IP
cd Any-IP
pyinstaller --onefile --console --uac-admin --manifest=admin.manifest --name=Any-IP any-ip.py
