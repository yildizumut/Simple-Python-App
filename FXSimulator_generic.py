# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:18:56 2019

@author: umut.yildiz
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from forex_python.converter import CurrencyRates
import quandl
import os
import xlsxwriter
import datetime as dt

# Change working directory to the related folder
drctry = os.path.join(os.environ['USERPROFILE'], 'Desktop')
os.chdir(drctry)

output_files = []

# Get the inputs from user
while True:
    try:
        hist_1_input = input("\nWrite 'exit' to quit!\nFormat for the date: YYYY-MM-DD\nEnter the Historical Start Date: ")
        if hist_1_input == "exit":
            exit()
        else:
            hist_1 = pd.to_datetime(hist_1_input + " 00:00:00", format="%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        break
    except ValueError:
        print("\nENTER A VALID DATE !\n")

while True:
    try:
        fwd_2_input = input("\nWrite 'exit' to quit!\nFormat for the date: YYYY-MM-DD\nEnter the Forward End Date: ")
        if fwd_2_input == "exit":
            exit()
        else:
            fwd_2 = pd.to_datetime(fwd_2_input + " 00:00:00", format="%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        break
    except ValueError:
        print("\nENTER A VALID DATE !\n")
        
while True:
    try:
        scen_size = input("\nWrite 'exit' to quit!\nNumber of scenarios should be an integer !\nEnter the Number of Scenarios you want to run: ")
        if scen_size == "exit":
            exit()
        elif float(scen_size) / int(scen_size) == 1:
            scen_size = int(scen_size)
            break
    except ValueError:
        print("\nENTER A INTEGER !\n")
        
while True:
    try:
        implied_volatility = input("\nWrite 'exit' to quit!\nFor automatic volatility calculation, write \'omit\' !\n" +
                                "Implied Volatility value should be given as a percentage in decimal format, e.g. 0.01 !\n" + "Enter the Implied Volatility: ")
        if implied_volatility == "exit":
            exit()
        elif implied_volatility == 'omit':
            implied_volatility_check = False
            break
        elif type(implied_volatility) is float:
            implied_volatility_check = True
            implied_volatility = float(implied_volatility)
            break
    except ValueError:
        print("\nENTER A VALID IMPLIED VOLATILITY !\n")
        
# Input Parameters
hist_start = pd.to_datetime(hist_1, format = "%Y-%m-%d")
hist_end = pd.to_datetime(pd.to_datetime('today').strftime("%Y-%m-%d"), format = "%Y-%m-%d") - pd.Timedelta('1 days')

start =  pd.to_datetime(pd.to_datetime('today').strftime("%Y-%m-%d"), format = "%Y-%m-%d")
end = pd.to_datetime(fwd_2, format = "%Y-%m-%d")

hist_range = pd.Series(pd.date_range(hist_start, hist_end)).map(lambda x: x if x.isoweekday() in range(1,6) else 0)
hist_range = hist_range[hist_range != 0].reset_index(drop = True)

fwd_range = pd.Series(pd.date_range(start, end)).map(lambda x: x if x.isoweekday() in range(1,6) else 0)
fwd_range = fwd_range[fwd_range != 0].reset_index(drop = True)

full_range = pd.Series(pd.date_range(hist_start, end)).map(lambda x: x if x.isoweekday() in range(1,6) else 0) # only gets weekdays
full_range = full_range[full_range != 0].reset_index(drop = True)

# Get the USD Data
#USDdata(as a pandas DataFrame) should include daily FX rates in two columns -> Date: the day and USD: the rate as float

#rate_list = [CurrencyRates().get_rate('USD', 'TRY', d) for d in hist_range]
#USDdata = pd.DataFrame({"Date": hist_range, "USD": rate_list})

eur_try = quandl.get("ECB/EURTRY", authtoken="py3UYy43X9dTYJb7X6es", start_date = hist_start.strftime("%Y-%m-%d"))
eur_usd = quandl.get("ECB/EURUSD", authtoken="py3UYy43X9dTYJb7X6es", start_date = hist_start.strftime("%Y-%m-%d"))

#USDdata = (eur_try * (1 / eur_usd)).reset_index()
USDdata = (1 / eur_usd).reset_index()
USDdata.columns = ['Date', 'USD']

USDdata["Date"] = pd.to_datetime(USDdata["Date"], format = "%Y-%m-%d")
print("\nUSD Data Retrieved - Information:\n")
print(USDdata.info())
print("--------------------------------------------------------------------------------")

#USDdata = pd.DataFrame({"Date": USDdata.apply(lambda x: x["Date"] if x["Date"] in full_range.to_list() else 0, axis = 1),
#            "USD": USDdata.apply(lambda x: x["USD"] if x["Date"] in full_range.to_list() else 0, axis = 1)})
#USDdata = USDdata[USDdata["Date"] != 0].reset_index(drop = True)

#history_usd = USDdata[(USDdata["Date"]>=hist_start) & (USDdata["Date"]<=hist_end)].reset_index(drop = True)

# GBM Exact Solution

# Parameters
#
# So:     initial exchange rate
# mu:     returns (drift coefficient)
# sigma:  volatility (diffusion coefficient)
# W:      brownian motion
# T:      time period
# N:      number of increments

def Brownian(seed, N):
    #np.random.seed(seed)                         
    dtime = 1./N                                            # time step
    b = np.random.normal(0., 1., int(N))*np.sqrt(dtime)     # brownian increments
    W = np.cumsum(b)                                        # brownian path
    return W, b

def GBM(So, mu, sigma, W, N):    
    t = np.linspace(0.,1.,N+1)
    S = []
    S.append(So)
    for i in range(1,int(N+1)):
        drift = (mu - 0.5 * sigma**2) * t[i]
        diffusion = sigma * W[i-1]
        S_temp = So*np.exp(drift + diffusion)
        S.append(S_temp)
    return S, t

def daily_return(x):
    returns = []
    for i in range(0, len(x)-1):
        today = x[i+1]
        yesterday = x[i]
        daily_return = (today - yesterday)/yesterday
        returns.append(daily_return)
    return returns

#def Brownian(seed, N):
#    #np.random.seed(seed)                         
#    dtime = N/N                                            # time step
#    b = np.random.normal(0., 1., int(N))*np.sqrt(dtime)     # brownian increments
#    W = np.cumsum(b)                                        # brownian path
#    return W, b
#
#def GBM(So, mu, sigma, W, N):    
#    t = np.linspace(0,N+1)
#    S = []
#    S.append(So)
#    for i in range(1,int(N+1)):
#        drift = (mu - 0.5 * sigma**2) * t[i]
#        diffusion = sigma * W[i-1]
#        S_temp = So*np.exp(drift + diffusion)
#        S.append(S_temp)
#    return S, t
#
#def daily_return(x):
#    returns = []
#    for i in range(0, len(x)-1):
#        today = x[i+1]
#        yesterday = x[i]
#        daily_return = (today - yesterday)/yesterday
#        returns.append(daily_return)
#    return returns


print("\n\no-o-o-o-o-o-o-o-o-o-o-o PROGRAM INITIATED o-o-o-o-o-o-o-o-o-o-o-o\n")

returns = daily_return(USDdata["USD"])

So = USDdata["USD"].values[USDdata.shape[0]-1]

N = pd.Series(pd.date_range(start, end)).map(lambda x: 1 if x.isoweekday() in range(1,6) else 0).sum()

mu = np.mean(returns) * N

if implied_volatility_check:
    sigma = implied_volatility * np.sqrt(N)
    print("\nImplied Daily Volatility: ", implied_volatility)
else:
    sigma = np.std(returns) * np.sqrt(N)
    print("\nCalculated Daily Volatility: ", np.std(returns))

#mu = np.mean(returns)
#
#if implied_volatility_check:
#    sigma = implied_volatility
#    print("\nImplied Daily Volatility: ", implied_volatility)
#else:
#    sigma = np.std(returns)
#    print("\nCalculated Daily Volatility: ", np.std(returns))   

#T = 1

seed = 5  

scenario_no = scen_size


gbm_scens = np.zeros((scenario_no, N + 1))

print("\n-> GBM is progressing !")
plt.figure(figsize = (20,10))
for i in range(scenario_no):
    W = Brownian(seed, N)[0]
    
    soln = GBM(So, mu, sigma, W, N)[0]    # Exact solution
    t = GBM(So, mu, sigma, W, N)[1]       # time increments for  plotting
    
    gbm_scens[i] = soln
    plt.title("Daily Volatility: " + str(sigma / np.sqrt(N)))
#    plt.title("Daily Volatility: " + str(sigma))
    plt.plot(np.arange(1, N + 2), soln)
    plt.ylabel('USD Rate, (₺/$)')

print("\n-> Simulation results and graph are being created !")
figure_name = "FX_Sim_Graph_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + ".png"
output_files.append(figure_name)
plt.savefig(drctry + "\\" + figure_name)

# Create a sequence of dates between start and end that includes also the weekends
# Weekend FX rates will be equal to the most recent weekday FX rate
gbm_scens_wknd = np.copy(gbm_scens)

all_fwd_dates = pd.Series(pd.date_range(start, end))
wknd_check = all_fwd_dates.map(lambda x: 1 if x.isoweekday() in range(6,8) else 0)
wknd_indices = wknd_check[wknd_check == 1].index

for i in wknd_indices:
    gbm_scens_wknd = np.insert(gbm_scens_wknd, i, gbm_scens_wknd[:,i-1], axis = 1)

excel_name = "Daily_FX_Simulations_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + ".xlsx"
output_files.append(excel_name)
workbook = xlsxwriter.Workbook(drctry + "\\" + excel_name)
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, "Scenario")
worksheet.write_column(1, 0, np.arange(1, scenario_no + 1))
worksheet.write_row(0, 1, pd.Series(pd.date_range(hist_end, end)).map(lambda x: x.strftime("%Y-%m-%d")))

col = 1
for row, data in enumerate(gbm_scens_wknd):
    worksheet.write_row(row + 1, col, data)
    
#worksheet.write(scenario_no + 1, 0, "FWD")
#worksheet.write_row(scenario_no + 1, 1, fwd_usd_arr_wknd)

workbook.close()

# %% GATHER ALL THE FOLDERS CREATED INTO ANOTHER FOLDER

cur_time = "From_" + start.strftime("%d%m%Y") + "_to_" + end.strftime("%d%m%Y") + "_RunDate_" + dt.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
os.makedirs(drctry + "\\" + cur_time)

for carry in output_files:
    os.rename(drctry + "\\" + carry, drctry + "\\" + cur_time + "\\" + carry)

print("\n\no-o-o-o-o-o-o-o-o-o-o-o CODE RUN COMPLETED o-o-o-o-o-o-o-o-o-o-o-o")

pydir = os.path.dirname(os.path.realpath(__file__))

while True:
    run_again = input("\nDo you want to run the program again ? (yes / no): ")
    if run_again == "yes":
        os.system(pydir + '\\Scripts\\python.exe ' + pydir + '\\FXSimulator.py')
        break
    elif run_again == "no":
        break
    