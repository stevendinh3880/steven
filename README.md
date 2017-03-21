# Steven Project

## Installing `python3`
`apt install python3`

## Installing `pip` for `python3`
`apt install python3-pip`

## Installing virtual environment
`pip3 install virtualenv`

## `pip` tools more
`apt install python-pip`

## Upgrading `pip`
`pip install --upgrade pip`

## Create a project directory
`mkdir steven`
`cd steven`

## Setting up virtual environment
`virtualenv .venv`

## Activating the virual environment
`source .venv/bin/activate`

## Install python requirements
`pip install -r requirements_py.txt`

## Redis reference 
https://redis.io

## Installing `redis`
`apt install redis-server`

## Installing `redis` client and tools
`apt install redis-tools`

## Edit redis config to setup the memory
`vi /etc/redis/redis.conf`
Currently this VM is `512Mb` RAM so setting `redis` to use only `32Mb`
Check for the line 
`# maxmemory <bytes>`
replace with the following
`maxmemory 33554432`

## Restart `redis` service
`service redis-server restart` 
