# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:18:56 2019

@author: umut.yildiz
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import quandl
import os
import xlsxwriter
import datetime

# Change working directory to the related folder
drctry = os.path.join(os.environ['USERPROFILE'], 'Desktop')
os.chdir(drctry)

output_files = []

# Get the inputs from user
#while True:
#    try:
#        hist_1_input = input("\nWrite 'exit' to quit!\nFormat for the date: YYYY-MM-DD\nEnter the Historical Start Date: ")
#        if hist_1_input == "exit":
#            exit()
#        else:
#            hist_1 = pd.to_datetime(hist_1_input + " 00:00:00", format="%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
#        break
#    except ValueError:
#        print("\nENTER A VALID DATE !\n")
#
#while True:
#    try:
#        fwd_2_input = input("\nWrite 'exit' to quit!\nFormat for the date: YYYY-MM-DD\nEnter the Forward End Date: ")
#        if fwd_2_input == "exit":
#            exit()
#        else:
#            fwd_2 = pd.to_datetime(fwd_2_input + " 00:00:00", format="%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
#        break
#    except ValueError:
#        print("\nENTER A VALID DATE !\n")
#        
#while True:
#    try:
#        scen_size = input("\nWrite 'exit' to quit!\nNumber of scenarios should be an integer !\nEnter the Number of Scenarios you want to run: ")
#        if scen_size == "exit":
#            exit()
#        elif float(scen_size) / int(scen_size) == 1:
#            scen_size = int(scen_size)
#            break
#    except ValueError:
#        print("\nENTER A INTEGER !\n")
#        
#while True:
#    try:
#        implied_volatility = input("\nWrite 'exit' to quit!\nFor automatic volatility calculation, write \'omit\' !\n" +
#                                "Implied Volatility value should be given as a percentage in decimal format, e.g. 0.01 !\n" + "Enter the Implied Volatility: ")
#        if implied_volatility == "exit":
#            exit()
#        elif implied_volatility == 'omit':
#            implied_volatility_check = False
#            break
#        elif type(implied_volatility) is float:
#            implied_volatility_check = True
#            implied_volatility = float(implied_volatility)
#            break
#    except ValueError:
#        print("\nENTER A VALID IMPLIED VOLATILITY !\n")

hist_1 = '2019-07-01'
fwd_2 = '2019-08-30'
scen_size = 10
implied_volatility = 'omit'
implied_volatility_check = False

# Input Parameters
hist_start = pd.to_datetime(hist_1, format = "%Y-%m-%d")
hist_end = pd.to_datetime(pd.to_datetime('today').strftime("%Y-%m-%d"), format = "%Y-%m-%d") - pd.Timedelta('1 days')

start =  pd.to_datetime(pd.to_datetime('today').strftime("%Y-%m-%d"), format = "%Y-%m-%d")
end = pd.to_datetime(fwd_2, format = "%Y-%m-%d")

# Get the USD Data
#USDdata(as a pandas DataFrame) should include daily FX rates in two columns -> Date: the day and USD: the rate as float

eur_usd = quandl.get("ECB/EURUSD", authtoken="py3UYy43X9dTYJb7X6es", start_date = hist_start.strftime("%Y-%m-%d"))

#USDdata = (eur_try * (1 / eur_usd)).reset_index()
USDdata = (1 / eur_usd).reset_index()
USDdata.columns = ['Date', 'USD']

USDdata["Date"] = pd.to_datetime(USDdata["Date"], format = "%Y-%m-%d")
print("\nUSD Data Retrieved - Information:\n")
print(USDdata.info())
print("--------------------------------------------------------------------------------")

returns = (USDdata.loc[1:, 'USD'] - USDdata.shift(1).loc[1:, 'USD']) / USDdata.shift(1).loc[1:, 'USD']

print("\n\no-o-o-o-o-o-o-o-o-o-o-o PROGRAM INITIATED o-o-o-o-o-o-o-o-o-o-o-o\n")
# Geometric Brownian Motion

# Parameter Definitions
# So    :   initial exchange rate (yesterday's exchange rate)
# dt    :   time increment -> a day in our case
# T     :   end of the time horizon
# N     :   number of periods in the time horizon -> T/dt
# t     :   array for time increments [dtime, dtime*2, dtime*3, .. , dtime*N]
# mu    :   mean of historical daily returns
# sigma :   standard deviation of historical daily returns
# W     :   array for brownian path
# b     :   array for brownian increments

# Parameter Assignments
So = USDdata["USD"].values[USDdata.shape[0]-1]
dt = 1
T = pd.Series(pd.date_range(start, end)).map(lambda x: 1 if x.isoweekday() in range(1,6) else 0).sum()
N = T / dt
t = np.arange(dt, T + dt, dt)
mu = np.mean(returns) * (1 / dt)
sigma = [implied_volatility * np.sqrt(1 / dt) if implied_volatility_check else np.std(returns) * np.sqrt(1 / dt)][0]
b = {str(scen): np.random.normal(0, 1, int(N)) * np.sqrt(dt) for scen in range(1, scen_size + 1)}
W = {str(scen): b[str(scen)].cumsum() for scen in range(1, scen_size + 1)}

print("\n-> GBM is progressing !")
# GBM Algorithm
drift = (mu - 0.5 * sigma**2) * t
diffusion = {str(scen): sigma * W[str(scen)] for scen in range(1, scen_size + 1)}
S = np.array([So * np.exp(drift + diffusion[str(scen)]) for scen in range(1, scen_size + 1)]) 
S = np.hstack((np.array([[So] for scen in range(scen_size)]), S))

# Plotting the simulations
plt.figure(figsize = (20,10))
for i in range(scen_size):
    plt.title("Daily Volatility: " + str(sigma / np.sqrt(1 / dt)))
    plt.plot(np.arange(1, N + 2), S[i, :])
    plt.ylabel('USD Rate, (€/$)')

print("\n-> Simulation results and graph are being created !")
figure_name = "FX_Sim_Graph_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + ".png"
output_files.append(figure_name)
plt.savefig(drctry + "\\" + figure_name)

# Create a sequence of dates between start and end that includes also the weekends
# Weekend FX rates will be equal to the most recent weekday FX rate
S_wknd = np.copy(S)

all_fwd_dates = pd.Series(pd.date_range(start, end))
wknd_check = all_fwd_dates.map(lambda x: 1 if x.isoweekday() in range(6,8) else 0)
wknd_indices = wknd_check[wknd_check == 1].index

for i in wknd_indices:
    S_wknd = np.insert(S_wknd, i, S_wknd[:,i-1], axis = 1)

excel_name = "Daily_FX_Simulations_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + ".xlsx"
output_files.append(excel_name)
workbook = xlsxwriter.Workbook(drctry + "\\" + excel_name)
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, "Scenario")
worksheet.write_column(1, 0, np.arange(1, scen_size + 1))
worksheet.write_row(0, 1, pd.Series(pd.date_range(hist_end, end)).map(lambda x: x.strftime("%Y-%m-%d")))

col = 1
for row, data in enumerate(S_wknd):
    worksheet.write_row(row + 1, col, data)

workbook.close()

# %% GATHER ALL THE FOLDERS CREATED INTO ANOTHER FOLDER

cur_time = "From_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + "_RunDate_" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
os.makedirs(drctry + "\\" + cur_time)

for carry in output_files:
    os.rename(drctry + "\\" + carry, drctry + "\\" + cur_time + "\\" + carry)

print("\n\no-o-o-o-o-o-o-o-o-o-o-o CODE RUN COMPLETED o-o-o-o-o-o-o-o-o-o-o-o")

pydir = os.path.dirname(os.path.realpath(__file__))
print(pydir)

while True:
    run_again = input("\nDo you want to run the program again ? (yes / no): ")
    if run_again == "yes":
        os.system(pydir + '\\Scripts\\python.exe ' + pydir + '\\FXSimulator.py')
        break
    elif run_again == "no":
        break
    