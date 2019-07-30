
# Introduction

Here in this tutorial, we will create a very simple Python application that can be really useful in various business cases. It will be a simple application, because user can use it through the command prompt window. If you are not looking for fancy GUIs, you can construct your easy-peasy Python application right away and it can make your life a lot easier. You can give up preparing the same analysis over and over again, with different input parameters and save a great deal of your efforts in the long run.

I will rely on a single example throughout the tutorial and before diving deeper into it, I would like to talk about a business scenario where we need a simple currency exchange rate analysis to get things going with our daily operations at work.

Suppose, I am interested in getting an idea of where €/$ exchange rate can move in some future and I would like to simulate it daily using Geometric Brownian Motion(GBM). At the end, I can calculate my risk due to currency movements. So, what I need to do is the following.

1. Decide how far to go back in the past and get €/$ rate to calculate daily volatility to be used in GBM algorithm,
2. Decide how far into the future our simulations should go,
3. Decide how many different future scenarios we would like to have,
4. (optional) If I want to try different scenarios based on some daily volatility assumptions other than the historical one, I should be able to enter a daily volatility value manually

Above four decisions are input to our simulation algorithm and we want users to be able to appropriately provide them to our program and get the results. In our case, we have two output files:

1. Number of scenarios(supplied by the user) many simulated forward €/$ rates as xlsx, and
2. Line graph of the simulated rates over all the scenarios as png

In order to make this a stand-alone desktop application, first, we need to create a virtual python environment and install all the required packages that our program uses. Then, we can write the script, but the important thing here is to set our Desktop path(or a folder in Desktop) as the working directory in our code. So, all the operations take place on our Desktop or a user created folder on Desktop, and the user can have access to the output files.

Below, you can see the steps we will follow in the tutorial.

# Steps
1. Creating virtual python environment
2. Installing packages to the virtual environment
3. Writing the script
    3.1. Setting Desktop folder as the working directory
    3.2. Getting input from the user
    3.3. Retrieving exchange rate data from Quandl
    3.4. GBM Algorithm
    3.5. Plotting the simulated rates and creating .png
    3.6. Writing the scenarios into .xlsx using xlsxwriter
    3.7. Collecting the output files into a folder
    3.8. Re-initiating the program
4. Creating a shortcut on Desktop for the app
5. Example run
## 1. Creating virtual python environment

Before creating the virtual environment, you have to make sure that you have a working Python installation and it is in the Path. You can download it from https://www.python.org/downloads/ and during the installation you can add python to the Path variable by checking the appropriate box on the installation screen when it appears. If you have a python installation, but it is not in the path, you can add it by:
- Control Panel -> System and Security -> System -> Advanced System Settings -> Environment Variables (under Advanced tab) -> Select Path variable under System variables box -> Click Edit -> To the Variable value box, you need to copy and paste two directories:
1. C:\Python37-64 -> You can edit this with where your Python is installed
2. C:\Python37-64\Scripts

Then, python gets in the Path and we are ready to create a virtual environment.

Now, we need to create an empty folder to host our virtual environment. For this tutorial, I create a folder named PythonVEnvs on the desktop and inside it, I create another folder named Python_VEnv_FXsimulator (You can create it anywhere on your computer as long as you have access permission). We can create the virtual environment that is specific to our application, inside Python_VEnv_FXsimulator. For other projects, we can just create other folders and dump virtual environments into them. 
Open a command prompt window and type: 
python -m venv path_to_python_environment
You can find the documentation on https://docs.python.org/3/library/venv.html
![venv_cmd.PNG](attachment:venv_cmd.PNG)
Then, we have a clean virtual environment. Next task is to install required packages.
![venv_folder.PNG](attachment:venv_folder.PNG)

## 2. Installing packages to the virtual environment


```python

```
