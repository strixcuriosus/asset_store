# asset_store
RESTful asset store web API

## Setup
#### 1. clone this repo
```bash
git clone git@github.com:strixcuriosus/asset_store.git
cd asset_store
```
#### 2. There are at least two options for building and running the app: with Docker and in a local virtualenv.

##### OPTION A: running as a container with Docker:
prerequisite: have docker installed.
see https://www.docker.com/ for os specific docker installation instructions.
```bash
# from the top level asset_store directory of this repository
# make sure you see the Dockerfile
# optional check:
if [[ $(ls | grep Dockerfile) ]]; then echo 'ok'; else echo 'you are probably in the wrong directory. look for the Dockerfile'; fi
# build the docker image
docker build -t asset-store .
# run the asset-store binding to port 5000
docker run -p 5000:5000 asset-store
```

##### OPTION B: running locally in a virtualenv
prerequisite: virtualenv and virtualenvwrapper
```bash
pip install virtualenv
pip install virtualenvwrapper
export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```
now make a new virtualenv, install requirements, and run the app
```bash
# from the top level asset_store directory of this repository
mkvirtualenv asset_store # optionally, specify a python here with the -p flag
workon asset_store
pip install -r requirements.txt
python run.py
```

#### 3. Try out the API
Once the app is built and running with one of the above options, you should be able to navigate to http://localhost:5000 to find interactive swagger API documentation.

### Testing
#### with docker
```bash
# build the asset-store image if you have not already done so
docker build -t asset-store .
# run asset-store with a bash entrypoint
docker run -it --entrypoint=/bin/bash asset-store
# run tests inside of the container
nosetests
```

#### with virtualenv
```bash
workon asset_store
nosetests
```
