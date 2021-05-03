# AIMSBOT DISCORD

This project automates the process of logging into aims.iith.ac.in, further a discord bot here will assist you in navigating.
## Features of Discord Bot
* Calculates Overall CGPA.
* Checks if any new grades are released.
* Recommends swaps to Maximize your CGPA.

### How to use
main.py is the python file which needs to be excecuted and before that please fullfil the dependencies given in requirements.txt.

### How it works
* A discord bot in Discord New Application is created and given necessary permissions and store the TOKEN.
* Using Selenium we write a code to navigate in the url.
* To get information we Webscrap the urls.
* A Mixed-Integer Optimization problem is solved to maximize grade.
* Then finally a code is written for discord bot commands.
