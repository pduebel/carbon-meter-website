# carbon-meter-website

A simple Flask web app to display electricity and carbon data recorded by Raspberry Pi as part of [pi-carbon-energy-meter](https://github.com/pduebel/pi-carbon-energy-meter 'pi-carbon-energy-meter repository') project.

**Related Repository:** [pi-carbon-energy-meter](https://github.com/pduebel/pi-carbon-energy-meter 'pi-carbon-energy-meter repository')

## Overview

This web app is an optional part of the [pi-carbon-energy-meter](https://github.com/pduebel/pi-carbon-energy-meter 'pi-carbon-energy-meter repository') project for displaying the data collected. It accepts the database posted by the Raspberry Pi as a json and displays the carbon and electricity consumption data using Google Charts. There are buttons to change the timeframe over which to display the data (day, week, month, year) and beneath the chart displays the total carbon produced and electricity consumed for that period. It also selects and displays the most recent grid carbon intensity value in the database.

The rate of electricity consumption (in kW) accepted as a separate post request and displayed on the same page. This is to allow the value to be updated more frequently - useful for experimentation turning defvices/appliances on and off and being able to see how this influences power consumption more quickly. Note that the electricity usage data is not updated dynamically so will require a page refresh.

![image](https://user-images.githubusercontent.com/56090238/132638098-e709c3cc-a1c9-462f-b5b8-072d090db91a.png)

## Set up

Perhaps the easiest way to set up this web app is to host it using Heroku, which allows you to do this for free, so this is the method that is detailed below. Before beginning the process head over to [Heroku](https://id.heroku.com/login 'Heroku login/signup page') to set up an account.

To start with ensure that you have git installed, the process is dependent on your OS so see this [Github Guide to installing git](https://github.com/git-guides/install-git 'How to install git') for details on how to do so. Once you have git installed you are able to install the Heroku CLI, again this OS dependent so go to the [Heroku CLI documentation](https://devcenter.heroku.com/articles/heroku-cli 'Heroku CLI documentation') for details on how to do this.

Once you have both git and the Heroku CLI installed, make sure that you are logged into the Heroku CLI with your account using the following command in the terminal:
```
heroku login
```
Then, clone the repository and open the directory using:
```
git clone https://github.com/pduebel/carbon-meter-website.git
cd carbon-meter-website
```
Before deploying the app, first set up a config file containing the username and password you want to use for the site. To do this open the `config-example.py` file in the main directory and change `'username'` and `'password'` to your desired username and password (you will also need to update the config file of the [pi-carbon-energy-meter](https://github.com/pduebel/pi-carbon-energy-meter 'pi-carbon-energy-meter repository') project with this username and password). Then save the file as `config.py` in the main directory and commit the changes using:
```
git add *
git commit -m "add config file"
```

Next, deploy the app by creating an app on Heroku and pushing the code to it using the following commands:
```
heroku create
git push heroku main
```
Note that the command `heroku create` will assign a random name to your app but you can specify your own name by passing it to the command e.g. `heroku create example-name`.

Finally, you can open your newly created web app by using:
```
heroku open
```
Use the url of the web app in the config file of the [pi-carbon-energy-meter](https://github.com/pduebel/pi-carbon-energy-meter 'pi-carbon-energy-meter repository') repository. 

For more detailed documentation on deploying the app with Heroku please see the documnetation for [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true 'Getting Started on Heroku with Python').

### A note on Heroku and SQLite

This web app uses a SQLite database which Heroku describes as "a bad fit for running on Heroku". This is because SQLite runs in memory, and backs up its data store in files on disk. This is an issue because Heroku's file system is cleared periodically, which means the whole SQLite database is cleared every 24 hours.

Despite this the web app still uses SQLite for two reasons. Firstly, the alternative is to use the Heroku Postgres service, which only offers about 10,000 rows of data for the free tier, so if using with this web app you would likely have to pay. Secondly, the data for the web app is primarily stored on the Raspberry Pi that collects it, with data getting posted every 15 minutes. This means that despite the SQLite database from the web app being cleared down every 24 hours, within 15 minutes it will have been replaced.

Visit the Heroku Dev Centre for more information on [SQLite on Heroku](https://devcenter.heroku.com/articles/sqlite3 'SQLite on Heroku')
