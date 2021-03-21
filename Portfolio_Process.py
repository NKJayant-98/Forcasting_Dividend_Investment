'''
Created on Oct 8, 2019

@author: jnutala
'''

import Portfolio_Constructor as construct
import json
import ast
import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt


class Process:
    '''
    This is where the backend process takes place for the portfolio. It calculates all the growth rates and the projected
    investment growth over the given years. This class also calls another class 'Portfolio_Constructor' which determines the Dividend & Price
    Growth Rate etc for all the Sectors and Stocks.
    This class should have: portfolio valuatio, list_sectors, list_stocks, remove_sector, get_sector_valuation(sector,duration of growth)
    '''

    def __init__(self, filepath):
        '''
        This is where the portfolio DATA FILE is read to get the existing portfolio information.
        The file info is then sent to the Constructor file where the portfolio is constructed.
        The process of valuating the portfolio is done in a function not as the constructor. This allows for 
        us to be able to get the valuation after any years we want multiple times. This can be used to create graphs etc.
        Be able to consider a stock or not into the portfolio w/o having to delete it. 
        '''
        self.total_contribution = None #allows this to be changeable 
        self.duration = None #The number of years for the investment growth
        self.history = None #The number of years to consider for the historic data
        self.Sectors = {} #make sure you have the dictionary set up: 'string_sector_name':Object sector
        
        with open(filepath) as f:
            data = json.load(f)
        
        self.total_contribution,self.duration,self.history = data['Contribution'],data['Duration'],data['History']
        
        # creating sector objects##############
        for sector in data['Sectors']:
            self.Sectors[sector[0]] = construct.Sector(sector[0],sector[1],self.total_contribution,self.duration,self.history)
            
        # creating stock objects in each respective sectors#######
        for stock_data in data['Stocks']:
            self.Sectors[stock_data[2]].add_stock(stock_data)
            
        
    
    def list_sectors(self):
        '''  This is where all the sectors within the portfolio are listed  '''
        
        return list(self.Sectors.keys())
    
    def list_all_stocks(self):
        ''' Lists all the stocks in this portfolio regardless of which sector they belong to.  '''
        lst = []
        for sector in self.Sectors.keys():
            lst += self.Sectors[sector].list_stocks()
            
        return lst
    
    def get_total_contribution(self):
        '''Returns the the total initial contribution for the portfolio
        '''
        
        total = 0
        
        for sector in self.Sectors.values():
            for stock in sector.Stocks.values():
                total += stock.get_principal_amount()
        
        return total
        
    
    def add_stock_to_sector(self,filepath):
        '''This is new stocks are added to the portfolio after it has been created.
            New stock can be added from any source, ATM it is through the stock File. From a different source, this code needs to be updated
            HAVE TO CHANGE UP THE CONTRIBUTION PERCENTAGES OF THE STOCKS BEFORE ADDING NEW STOCK.'''   
        
        with open(filepath+'\\Stock.txt','r') as f:
            stock_file = ast.literal_eval(f.read())
        
        if stock_file['Name'] in self.list_all_stocks():
            return('This stock already exists in the sector....')
        
        sector = stock_file['Sector']
        
        ######### If the sector for this stock does not exist, it will be placed in other. The stocks contribution is 100%
        ## and the sector contribution is calculated from that. 
        
        
        ########################################################################################
        #This is where you check to see if the percentages add up#####
        #later on, in user interface: have the check done on UI so only correct values get in. 
        #so the following code is temp or can be 2nd line of defence.
        try:
            contribution = stock_file['Contribution']/self.Sectors[sector].get_yearly_sector_contribution('$')
        except:
            return('The wrong sector value was entered, please re-enter the info correctly in the Stock File...')
        
        total = contribution
        
        with open(filepath+'\\Portfolio.json') as f:
            portfolio_file = json.load(f)
            
        for stock in portfolio_file['Stocks']:
            if sector in stock:
                total += float(stock[4].strip('%'))/100
        if float('%0.2f'%total) != float(1):
            return("THE STOCKS CONTRIBUTION DOES NOT ADD UP IN THE NEW STOCK'S SECTOR, PLEASE ENTER THE CORRECT INFO")
            
        stock_data = []
        stock_data.append(stock_file['Name'])
        stock_data.append(stock_file['Stock'].upper())#the ticker
        stock_data.append(sector)
        stock_data.append(stock_file['Initial'])
        stock_data.append(contribution)
    
        self.Sectors[sector].add_stock(stock_data)
        
        #update the stock contributions for other stocks in this sector
        for stock in self.Sectors[sector].Stocks.values():
            for stock2 in portfolio_file['Stocks']:
                if stock.get_stock_name() in stock2:
                    stock.stock_contribution = float(stock2[4].strip('%'))/100
        
        return('Success')
        
    def remove_stock_from_sector(self,filepath,stock):
        '''Removes the stock from a given sector'''
        status = 'none'
        for sector in self.Sectors.values():
            if stock in sector.list_stocks():
                status = sector.remove_stock(stock)
        
        if type(status) == str:
            return 'Stock DNE'
        
        stock_data = []
        stock_data.append(status.get_stock_name())
        stock_data.append(status.get_ticker())
        stock_data.append(sector.get_sector_name())
        stock_data.append(status.get_principal_amount())
        stock_data.append(status.get_yearly_stock_contribution('%'))
        
        with open(filepath+'\\Portfolio.json') as f:
            portfolio_file = json.load(f)
        
        #Update the stock contributions for other stocks in the sector
        for stock in self.Sectors[sector.get_sector_name()].Stocks.values():
            for stock2 in portfolio_file['Stocks']:
                if stock.get_stock_name() in stock2:
                    stock.stock_contribution = float(stock2[4].strip('%'))/100
        
        if stock not in self.list_all_stocks():
            return 'success'
        else:
            return 'Problem'
    
    def remove_sector(self,sector):
        '''Removes the given Sector from the portfolio'''
        
        return None
            
    def change_sector_contribution(self,sector,new_contribution):
        '''This method changes the contribution of the given sector'''
        
        return None
    

    def get_portfolio_valuation(self):
        ''' Returns the total valuation of the portfolio after a given duration. This function calls a lot of functions from
            sector class and stock class. 
        '''
        portfolio_valuation = [0]*(self.duration+1)
        portfolio_yearly_income = [0]*(self.duration+1)
        portfolio_contribution = [0]*(self.duration+1)
        
        for sector in self.Sectors.values():
            sector_valuation = sector.get_sector_valuation()
            for x in range(self.duration+1):
                portfolio_valuation[x] += sector_valuation[0][x]
                portfolio_yearly_income[x] += sector_valuation[1][x]
                portfolio_contribution[x] += sector_valuation[2][x]
        
        return (portfolio_valuation,portfolio_yearly_income,portfolio_contribution)
                
    def write_to_file(self,filepath):
        '''Writes the current Portfolio to File. If this is too slow, maybe the 'write changes to file' method is better.'''
        
        portfolio = {'Contribution':self.total_contribution,'Duration':self.duration,'History':self.history,'Sectors':[],'Stocks':[]}
        
        for sector in self.Sectors.values():
            portfolio['Sectors'].append([sector.get_sector_name(),sector.get_yearly_sector_contribution('%')])
            for stock in sector.Stocks.values():
                portfolio['Stocks'].append([stock.get_stock_name(),stock.get_ticker(),sector.get_sector_name(),stock.get_principal_amount(),stock.get_yearly_stock_contribution('%')])
            
        with open(filepath+'\\Portfolio.json','w',encoding='utf-8') as f:
            json.dump(portfolio,f,ensure_ascii=False,indent=4)
            
            
    
    def get_historic_valuation(self,filepath):
        '''This returns the historic valuation of this stock. It uses the duration to calculate the valuation from that point in history. 
            This valuation the user to see how much their investment would grow if they had invested 'duration' years ago with a certain 
            yearly contribution.
            This stock needs to have its info given and the data needs to pulled freshly...
            
        '''
        #####UNCOMMENT THE PRINT STATEMENTS TO DEBUG PROBLEMS IN THIS FUNCTION*******
        
        with open(filepath+'\\Stock.txt','r') as f:
            stock_file = ast.literal_eval(f.read())
        
        #READING THE STOCK DATA FROM THE LOCAL FILES
        div_data = pd.read_csv("Data Files\\%s.csv"%str(stock_file['Stock']))
        price_data = pd.read_csv("Data Files\\%s (1).csv"%str(stock_file['Stock']))
        
        dividend = []
        div_date = []
        prices = []
        prices_date = []
        principal = stock_file['Initial']
        contribution = stock_file['Contribution']
        
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
#         print("\nBought shares: %d Share Price: %s Total Valuation: %f Total Contribution: %d Contribution: %d Principal: %d"%(bought_shares,str(price),total_valuation,total_contribution,contribution,principal))
        while(True): #the years
            yearly_income = 0
#             print('\nThe year: ',yr)
            
            while(year == div_date[y].strftime('%Y')): #the dividend periods
#                 print('Dividend Details')
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
#                 print('Dividend Earned: %s    Share Price: %s   Bought Shares: %s    Total Valuation: %s'%(str(div_earned),str(price),str(bought_shares),str(total_valuation)))
                ###################################################              
                
                x += 1
                try:
                    year = div_date[x].strftime('%Y')
                except:
                    yr = 'exit'
                    break
                
            if type(yr) == str:
                break
            #####################THE CALCULATOINS##############
            y = x
            div_earned = contribution + remaining_cash #this is not dividend earned, it is total remaining to buy shares
            bought_shares = int(div_earned/price)
            remaining_cash = float('%0.2f' % (div_earned-(price*bought_shares)))
            total_shares += bought_shares
            total_contribution += contribution
            total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
            
#             print('The stock price: %s The dividend: %s' %(str(price),str(div)))
#             print('Total Valuation (Year End): %s\tShares Owned(Year End): %s' %(str(total_valuation),str(total_shares)))
            ################################################### 
            if type(yr) == int:
                yr += 1
        
            
        
#         print('\n##### For THIS STOCK:  ###########')
#      
#         print('Total Valuation is: $',total_valuation)
#         print('Total Shares Owned is: ',total_shares)
#         print('Total Contribution is: $', total_contribution)
#         print('The Yearly Income after ',duration,' years is: $', yearly_income)  
#          
#         print('Final Dividend: ',float('%0.4f'%div))
#         print('Final Price: $', float('%0.2f'%price))

        return([total_valuation, total_shares, total_contribution, duration, yearly_income,div,price])
        
        
        
    
# cwd = os.getcwd()
# print('This is a test: ')
# print(Process(cwd+'\\Portfolio.json').write_to_file(cwd))

    def get_pie_chart(self):
        '''Returns 2 charts, 1 shows the break down of all the sectors and their contribution and the other shows
            the valuations of all the sectors.
        '''
        labels = []
        contribution_sizes = []
        valuation_sizes = []
        yearlyincome_sizes = []
        
        for sector in self.Sectors.values():
            if sector.get_sector_name() == 'Capital Market & Investement Funds':
                labels.append('Capital Markets & IFs')
            else:
                labels.append(sector.get_sector_name())
            
            sector_value = sector.get_sector_valuation()
            contribution_sizes.append(sector_value[2][-1])
            valuation_sizes.append(sector_value[0][-1])
            yearlyincome_sizes.append(sector_value[1][-1])
            
        fig, (ax1,ax2,ax3) = plt.subplots(3,1)
        
        ax1.pie(contribution_sizes,autopct='%1.0f%%')
        ax1.set_title('Contributions')

        ax2.pie(valuation_sizes, autopct='%1.0f%%')
        ax2.set_title('Total Valuations')
        
        ax3.pie(yearlyincome_sizes,autopct='%1.0f%%')
        ax3.set_title('Yearly Incomes')
        
        plt.legend(labels,loc = 'best')
        return (plt)
        
        
        
        
        
        
        
        
        
        
        
        
     
    