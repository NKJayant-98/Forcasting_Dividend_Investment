'''
Created on Sep 20, 2019

@author: jnutala
'''
import datetime
import numpy
from Web_Element import web_data
import pandas as pd


class Functions:
    '''
    These functions are used in the Algorithm file.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    #retrieves the stock's historic data from web using selenium
    def web_data(self,stock):
        print('Now obtaining the stock data from Yahoo Finance...\n')
        today_price = web_data().Download_Data(stock)
        return today_price
        
        
    #retrieves the stock's historic data from the database (yahoo)
    def database_data(self,stock):
        return (None,None)
        

    def dividend_growth_rate(self,data,history):
        
        #the x and y are used to find the growth
        dividend = [] # the y
        date = []
        
        data['Date'] = pd.to_datetime(data['Date'])        
        sorted_data = data.sort_values('Date')
        
        for i in sorted_data['Date']:
            date.append(i.to_pydatetime())
            
        for i in sorted_data['Dividends']:
            dividend.append(float(i))
        
        #As of Oct 6th 2019, the dividend values take into account the splits as well 
        #so this piece of code is not necessary.
        '''
        for i in splits: #for stock splits
            if type(i) == str:
                break
            for a in range(len(date)-1,-1,-1):
                if date[a]<i[0]:
                    dividend[a] = dividend[a]*i[1]
        '''
            
#         print('\nThe dividend Data: ', dividend,'\n')
        
        pivot = datetime.datetime.today() - datetime.timedelta(days=history*365.25)
        
        for i in range(len(date)-1,-1,-1):
            if date[i] < pivot:
                dividend.remove(dividend[i])
        
        #determine the growth rate********
        x = list(range(1,len(dividend)+1)) # x
        
        rate = numpy.polyfit(x,dividend,1)[0]
        
        #get the frequency of the date
        fq = self.get_div_frequency(date)
        
        return(rate,dividend[(len(dividend)-1)],fq)
        
    def get_div_frequency(self,date):
        if abs(date[-2].month - date[-3].month) == 3 or abs(date[-2].month - date[-3].month) == 9:
            return(4)
        elif abs(date[-2].month - date[-3].month) <= 2 or abs(date[-2].month - date[-3].month) <= 11:
            return(12)
        else:
            print('The frequency of dividend is undertermined, the program will now exit\n\n.')
            print('The date values: \n',date)            
            exit()
        
    
    def price_growth_rate(self,data,history):
        #the x and y are used to find the growth
        
        price = [] # the y
        date = []
        
        sorted_data = data.sort_values('Date')
        
        for i in sorted_data['Date']:
            date.append(datetime.datetime.strptime(str(i),'%Y-%m-%d'))
        
        for i in sorted_data['Close']:
            price.append(float(i))
        
        self.Prices = price
        self.priceDate = date
        
        pivot = datetime.datetime.today() - datetime.timedelta(days=history*365.25)
        
        for i in range(len(date)-1,-1,-1):
            if date[i] < pivot:
                price.remove(price[i])
        
        x = list(range(1,len(price)+1)) # x
        
#         rate = float('%.5f' % (numpy.polyfit(x,price,1)[0]))
        rate = numpy.polyfit(x,price,1)[0]
        
        if rate < -0.0014:
            rate = 0.01
        
        return(rate)
        
    def get_historic_valuation(self,div_data,price_data,principal,contribution):
        ''' Returns the valuation of this stock if investment into it started 10 years ago with the current yearly
        contribution. If no dividends where being given out 10 years ago, it calculates from the dividend release inception
        '''
        
        dividend = []
        div_date = []
        prices = []
        prices_date = []
        
        div_data['Date'] = pd.to_datetime(div_data['Date'])        
        sorted_data = div_data.sort_values('Date')
        
        for i in sorted_data['Date']:
            div_date.append(i.to_pydatetime())
            
        for i in sorted_data['Dividends']:
            dividend.append(float(i))
        
        sorted_data = price_data.sort_values('Date')
        
        for i in sorted_data['Date']:
            prices_date.append(datetime.datetime.strptime(str(i),'%Y-%m-%d'))
        
        for i in sorted_data['Close']:
            prices.append(float(i))
            
        
        duration = 10
        startYear = datetime.datetime.today() - datetime.timedelta(days=duration*365.25)
        
        if div_date[0].strftime('%Y') < startYear.strftime('%Y'):
            for i in range(len(div_date)-1,-1,-1):
                if div_date[i] < startYear:
                    dividend.remove(dividend[i])
                    div_date.remove(div_date[i])
        else:
            duration = int(datetime.datetime.today().strftime('%Y')) - int(div_date[0].strftime('%Y'))
        
        
        #####For loops for the estimation of investment after the given history
        div_earned = None #will be used to account for contributed amount
        for i in range(len(prices_date)): #determine the initial stock purchase price
                    if div_date[0].strftime('%Y%m') == prices_date[i].strftime('%Y%m'):
                        price = prices[i]
        bought_shares = int(principal/price) #in the for loop this is earned shares as well
        remaining_cash = float('%0.2f' % (principal-(price*bought_shares)))
        total_shares = bought_shares
        total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
        total_contribution = principal
        year = div_date[0].strftime('%Y')
        x = 0
        y = 0
        yr = 0
        print("\nBought shares: %d Share Price: %s Total Valuation: %f Total Contribution: %d Contribution: %d Principal: %d"%(bought_shares,str(price),total_valuation,total_contribution,contribution,principal))
        while(True): #the years
            
            yearly_income = 0
            print('\nThe year: ',yr)
            
            while(year == div_date[y].strftime('%Y')): #the dividend periods
                print('Dividend Details')
                for i in range(len(prices_date)):
                    if div_date[x].strftime('%Y%m') == prices_date[i].strftime('%Y%m'):
                        price = prices[i]
                        break 
                    
                #####################THE CALCULATOINS##############
                div = dividend[x]
                div_earned = float('%0.2f' % (div*total_shares))             
                bought_shares = int(div_earned/price)
                remaining_cash += float('%0.2f' % (div_earned-(price*bought_shares)))
                total_shares += bought_shares
                total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
                yearly_income = float('%0.2f'%(yearly_income+div_earned))
                print('Dividend Earned: %s    Share Price: %s   Bought Shares: %s    Total Valuation: %s'%(str(div_earned),str(price),str(bought_shares),str(total_valuation)))
                ###################################################              
                
                x += 1
                try:
                    year = div_date[x].strftime('%Y')
                except:
                    yr = 'exit'
                    break
                
            if type(yr) == str:
                break
            #####################THE YEAR END CALCULATOINS##############
            y = x
            div_earned = contribution + remaining_cash #this is not dividend earned, it is total remaining to buy shares
            bought_shares = int(div_earned/price)
            remaining_cash = float('%0.2f' % (div_earned-(price*bought_shares)))
            total_shares += bought_shares
            total_contribution += contribution
            total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
            
            print('The stock price: %s The dividend: %s' %(str(price),str(div)))
            print('Total Valuation (Year End): %s\tShares Owned(Year End): %s' %(str(total_valuation),str(total_shares)))
            ################################################### 
            if type(yr) == int:
                yr += 1
                
#             
            
        
        print('\n##### For THIS STOCK:  ###########')
    
        print('Total Valuation is: $',total_valuation)
        print('Total Shares Owned is: ',total_shares)
        print('Total Contribution is: $', total_contribution)
        print('The Yearly Income after ',duration,' years is: $', yearly_income)  
        
        print('Final Dividend: ',float('%0.4f'%div))
        print('Final Price: $', float('%0.2f'%price))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    
    
    