# handgun_api

> This project is api of ['handgun'](https://github.com/LTKSK/handgun).

> This project need mongodb.

## setup

``` bash
# create virtualenviron
python -m virtualenv venv

# activate
.\venv\Scripts\activate.bat

# or, on Linux
source ./venv/Scripts/activate

# install modules
python -m pip install -r requirements.txt


# Please activate "mongodb" in your PC or Server.
# This application will access to mongodb by pymongo.

# and please check config/handgun_config.yml file.
# 'handgun_config.yml' has been described mongodb setting(now only described 'port' and 'host')
# default port is '27017'. default host is 'localhost'

# and run app.
python app.py

# then, you can use 'handgun'.
```