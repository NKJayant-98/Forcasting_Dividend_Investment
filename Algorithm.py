'''
Created on Sep 19, 2019

@author: jnutala
'''
import pandas as pd
import datetime
import ast
from Algorithm_Functions import Functions as fn
import os



# import the config file 

with open('Stock.txt','r') as f:
    config = ast.literal_eval(f.read())

source = config['Data Source'].lower()
stock = config['Stock'].upper()  
sector = config['Sector'].lower()
history = config['Historic Data']  
duration = config['Duration']
initial = config['Initial']
contribution = config['Contribution']
functions = fn()
#getting the data files ######################

if source == 'web':
    today_price = functions.web_data(stock)
    price = today_price
    path = "Data Files"
    files = os.listdir(path)
    
    for f in files:
        if f == stock+'.csv':
            f1 = pd.read_csv(path+'\\'+f)
            if 'Dividends' in f1.columns:
                div_data = f1
                price_data = pd.read_csv(path+'\\'+stock+' (1).csv')
            else:
                price_data = f1
                div_data = pd.read_csv(path+'\\'+stock+' (1).csv')
            break

elif source == 'database':
    div_data,price_data = functions.database_data(stock)
    
#***************** if neither web nor database**************
else:
    print('Please enter the correct option for Data Source.')
    print('The program will now exit...')
    exit()
#************************************************

#calling functions to get dividend growth rate and price growth rate 
div_rate,div,fq = functions.dividend_growth_rate(div_data,history)
div = float('%0.4f'%div)

price_rate = functions.price_growth_rate(price_data,history)
if fq == 4:
    price_rate = float('%.5f'%(price_rate*3))
    

#####For loops for the estimation of investment after certain duration 
div_earned = None #will be used to account for contributed amount
bought_shares = int(initial/price) #in the for loop this is earned shares as well
remaining_cash = float('%0.2f' % (initial-(price*bought_shares)))
total_shares = bought_shares
total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
total_contribution = initial
year = int(datetime.datetime.now().strftime('%Y'))

#these lists represent the amount for each year. Starts at year 0 - the current year..
valuation_lst = [total_valuation]
contribution_lst = [total_contribution] 
yearly_income_lst = [0]
shares_lst = [total_shares]


for year in range(duration):
    yearly_income = 0
    for i in range(fq):
        # update stock price and dividend payout using the growth ratios
        price = (price + price_rate)
        div = (div+div_rate)
        div_earned = float('%0.2f' % (div*total_shares))
        bought_shares = int(div_earned/price)
        remaining_cash += float('%0.2f' % (div_earned-(price*bought_shares)))
        total_shares += bought_shares
        total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
        yearly_income = float('%0.2f'%(yearly_income+div_earned))
    
    div_earned = contribution + remaining_cash #this is not dividend earned, it is total remaining to buy shares
    bought_shares = int(div_earned/price)
    remaining_cash = float('%0.2f' % (div_earned-(price*bought_shares)))
    total_shares += bought_shares
    total_contribution += contribution
    total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
    #adding to the lists
    valuation_lst.append(total_valuation)
    contribution_lst.append(total_contribution)
    yearly_income_lst.append(yearly_income)
    shares_lst.append(total_shares)
    
print('\n##### For %s:  ###########'% stock)
print('The stock purchase price: $%s'%str(today_price))
print('The stock dividend frequency is: %s'%str(fq))
print('The Calculated Dividend growth rate is: ', float('%0.4f'%div_rate))
print('The Calculated Price growth rate in CAD is: $',float('%0.4f'%price_rate))

print('Total Valuation is: $',total_valuation)
print('Total Shares Owned is: ',total_shares)
print('Total Contribution is: $', total_contribution)
print('The Yearly Income after ',duration,' years is: $', yearly_income)  

print('Final Dividend: ',float('%0.4f'%div))
print('Final Price: $', float('%0.2f'%price))
# print('\nNow printing the data for all years')

# print('Year\t\tTotal Valuation($)\t\tYearly Income($)\t\tTotal Contributed Amount($)\t\tTotal Shares Owned')
# for year in range(duration):
#     print(year+1,'\t\t%s\t\t%s\t\t%s\t\t%s' %(str(valuation_lst[1+year]), str(yearly_income_lst[1+year]), str(contribution_lst[1+year]), str(shares_lst[1+year])))
  
while(True):  
    choice = input('Would you like to get historic valuation for the past 10 years? (Y/N): ')
    if choice.lower() == 'y':
        break
    elif choice.lower != 'y':
        x = input('You have selected N or an invalid input, are you sure you want to exit?(Y/N): ')
        if x.lower() == 'y':
            exit()
    
        
# while (True):
#     history = input('Please enter the history years: ')
#     startYear = datetime.datetime.today() - datetime.timedelta(days=history*365.25)
#     
#     if functions.dividend[0].strftime('%Y') <= startYear.strftime('%Y'):
#         break
#     else:
#         print('This company did not start giving dividends during that time, please enter a smaller number for history...')
    
functions.get_historic_valuation(div_data,price_data,3000, 750)
    
    
    
    
    



