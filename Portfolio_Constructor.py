'''
Created on Oct 9, 2019

@author: jnutala
'''
import pandas as pd
import os
import datetime
import numpy

class Sector(object):
    '''
    This is where each sector with its contribution is created. All its stocks and their contributions are constructed in the next class.
    A sector object is created. 
    When a sector object is created it contains: sector name, its contribution and all its stocks (as objects).
    '''
    
    def __init__(self, sector_name,contribution,total_contri,duration,history):
        '''
        Pulls the portfolio sector and constructs it. It calls the Stock class for each stock in the sector and creates objects and adds
        to the sector object. 
        '''
        self.name = None
        self.contribution_in_folio = None #allow this to be able to change. this is teh sector contribution in the portfolio
        self.Stocks = {} #make sure it has 'string of stock':Object stock!!
        self.total_contribution = None
        self.duration = duration
        self.history = history
        
        self.total_contribution = total_contri
        self.name, self.contribution_in_folio = sector_name, float(contribution.strip('%'))/100
        
        
    def get_sector_name(self):
        '''Returns the sector name'''
        return self.name
    
    def get_yearly_sector_contribution(self,option):
        ''' Returns the yearly contributions of the given sector, in percentage of total contributions and the dollar value 
            - Rememeber to show what the total yearly contribution is as well. 
        '''
        if option.lower() == '$' or option.lower() == 'dollar':
            return (self.contribution_in_folio * self.total_contribution)
        elif option.lower() == '/' or option.lower() == 'fraction':
            return (self.contribution_in_folio)#returns a fraction
        elif option.lower() == '%' or option.lower() == 'percent':
            return (str(self.contribution_in_folio*100)+'%')#returns a percent 
    
    
    
    ##### FOLLOWING FUNCTIONS ALL REFER TO THE SOCKS IN THE SECTOR OBJECT.#####
    
    def add_stock(self,stock_data):
        '''Adds a new stock object to this sector object. HAVE TO MAKE SURE TO ADD THE NEW STOCK TO THE SECTOR IN THE DATA FILE'''
        self.Stocks[stock_data[0]] = Stock(stock_data,self.get_yearly_sector_contribution('$'),self.duration,self.history)
        
     
    def get_stock(self,stock): #this may not be needed. 
        '''Returns the stock object specified.'''
        return self.Stocks[stock]
    
    def list_stocks(self):
        '''Retruns all the stocks in this portfolio'''
        return list(self.Stocks.keys())
    
    def remove_stock(self,stock):
        '''Removes a specific stock from the sector. HAVE TO MAKE SURE TO REMOVE THE STOCK FROM THE SECTOR IN THE DATA FILE'''
        
        return self.Stocks.pop(stock,'The stock does not exist in the Portfolio. Please re-enter..')
    
    
    def get_sector_valuation(self):
        ''' Returns the total valuation of a sector after a given duration'''
        
#         You get these values from get_stock_valuation module total_valuation_list,yearly_income_list,total_contribution_list,total_shares_list
        duration = self.duration
        
        sector_valuation_lst = [0]*(duration+1)
        sector_yearly_income_lst = [0]*(duration+1)
        sector_contribution_lst = [0]*(duration+1)
       
        
        for stock in self.Stocks.values():
            stock_valuation = stock.get_stock_valuation()
            for x in range(duration+1):
                sector_valuation_lst[x] += stock_valuation[0][x]
                sector_yearly_income_lst[x] += stock_valuation[1][x]
                sector_contribution_lst[x] += stock_valuation[2][x]
        
        return (sector_valuation_lst,sector_yearly_income_lst,sector_contribution_lst)
    
    
    
class Stock(Sector):
    '''
    This is where the stock object is created that is used in the Sector object. This object has the following attributes:
    stock name, its % in sector, ticker, principal amount, dividend growth rate, price growth rate
    '''
    name = None
    ticker = None
    principal= None
    stock_contribution = None
    consider = True #if this is set to false, then this stock is not considered in the portfolio but is not deleted (the % distributed)
    sector_contribution = None
    # allow the principal and contribution % to be able to change.....
    
    def __init__(self,stock_data,contri,duration,history):
        '''
        Gets the portfolio stock data from the Sector class and constructs the stock object.
        '''
        
        self.name = None
        self.ticker = None
        self.principal= None
        self.stock_contribution = None
        self.consider = True #if this is set to false, then this stock is not considered in the portfolio but is not deleted (the % distributed)
        self.sector_contribution = None
        self.duration = duration
        self.history = history
        # allow the principal and contribution % to be able to change.....   
        
        
        self.name,self.ticker,self.principal = stock_data[0],stock_data[1],stock_data[3]
        self.sector_contribution = contri
        if type(stock_data[4]) == float:
            self.stock_contribution = stock_data[4]
        else:
            self.stock_contribution = float(stock_data[4].strip('%'))/100
        
        
    def get_stock_name(self):
        'Returns the name of the stock'
        
        return self.name
    
    def get_yearly_stock_contribution(self,option):
        ''' Returns the yearly contribution of the sector for the stock in $ amount of sector. '''
        
        if option.lower() == '$' or option.lower() == 'dollar':
            return (self.sector_contribution*self.stock_contribution)
        elif option.lower() == '/' or option.lower() == 'fraction':
            return (self.stock_contribution)
        elif option.lower()=='%' or option.lower() =='percent':
            return (str(self.stock_contribution*100)+'%')
        
        
    def get_ticker(self):
        ''' Returns the ticker string of the stock. '''
        return self.ticker
    
    def get_principal_amount(self):
        '''Returns the initial amount used to buy the stocks.'''
        return self.principal
    
    def stock_consideration(self,option):
        '''If the consider is False, then it will turn true to consider this stock into the Portfolio. If it is true
           it will return that the stock is already being considered.'''
        if option.lower() == 'false':
            self.consider = False
            return (print('No longer including %s in this porfolio.'%self.name))
        elif option.lower() == 'true':
            self.consider = True
            return(print('Now including %s in this portfolio.'%self.name))
    
    
    def get_div_growth_rate(self):
        '''Returns the dividend growth rate of the stock'''
        data = self.read_data_files('dividend')
        
        dividend = [] # the y
        date = []
        
        data['Date'] = pd.to_datetime(data['Date'])        
        sorted_data = data.sort_values('Date')
        
        for i in sorted_data['Date']:
            date.append(i.to_pydatetime())
            
            
        for i in sorted_data['Dividends']:
            dividend.append(float(i))
        
        pivot = datetime.datetime.today() - datetime.timedelta(days=self.history*365.25)
        
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
        '''This is used to get the dividend frequency'''
        if abs(date[-2].month - date[-3].month) >= 2 or abs(date[-2].month - date[-3].month) >=8:
            return(4)
        elif abs(date[-2].month - date[-3].month) < 2 or abs(date[-2].month - date[-3].month) < 10:
            return(12)
        else:
            print('The frequency of dividend is undetermined, the program will now exit\n\n.')
            print('The date values: \n',date)            
            exit()
        
    def get_price_growth_rate(self):
        '''Returns the price growth rate of the stock'''
        data = self.read_data_files('price')
        
        price = [] # the y
        date = []
        
        sorted_data = data.sort_values('Date')
        
        for i in sorted_data['Date']:
            date.append(datetime.datetime.strptime(str(i),'%Y-%m-%d'))
        
        for i in sorted_data['Close']:
            price.append(float(i))
        
        pivot = datetime.datetime.today() - datetime.timedelta(days=self.history*365.25)
        
        for i in range(len(date)-1,-1,-1):
            if date[i] < pivot:
                price.remove(price[i])
        
        x = list(range(1,len(price)+1)) # x
        rate = numpy.polyfit(x,price,1)[0]
        
        if rate < -0.0014:
            rate = -0.0014
        return (rate,price[-1])
        
        
    def get_stock_valuation(self):
        '''Returns the total valuation of a stock after a given duration'''
        duration, history = self.duration, self.history
        div_rate,div,fq = self.get_div_growth_rate()
        div = float('%0.4f'%div)
        
        contribution = self.get_yearly_stock_contribution('dollar')
        
        price_rate,price = self.get_price_growth_rate()
        if fq == 4:
            price_rate = float('%.5f'%(price_rate*3))
        
        #####For loops for the estimation of investment after certain duration
        div_earned = None #will be used to account for contributed amount
        bought_shares = int(self.principal/price) #in the for loop this is earned shares as well
        remaining_cash = float('%0.2f' % (self.principal-(price*bought_shares)))
        total_shares = bought_shares
        total_valuation = float('%0.2f' % (total_shares*price + remaining_cash))
        total_contribution = self.principal
        
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
                div_earned = (div*total_shares)
                bought_shares = int(div_earned/price)
                remaining_cash += (div_earned-(price*bought_shares))
                total_shares += bought_shares
                total_valuation = (total_shares*price + remaining_cash)
                yearly_income = (yearly_income+div_earned)
            
            div_earned = contribution + remaining_cash #this is not dividend earned, it is total remaining to buy shares
            bought_shares = int(div_earned/price)
            remaining_cash = float('%0.2f' % (div_earned-(price*bought_shares)))
            total_shares += bought_shares
            total_contribution += contribution
            total_valuation = (total_shares*price + remaining_cash)
            #adding to the lists
            valuation_lst.append(float('%0.2f'%total_valuation))
            contribution_lst.append(float('%0.2f'%total_contribution))
            yearly_income_lst.append(float('%0.2f'%yearly_income))
            shares_lst.append(total_shares)
        
        return (valuation_lst,yearly_income_lst,contribution_lst,shares_lst)
        
        
        
    def read_data_files(self,rate):
        '''Reading historic data from local data files. This is used when database connection
           is not available.'''
        
        path = "Data Files"
        files = os.listdir(path)
        for f in files:
            if f == self.ticker+'.csv':
                f1 = pd.read_csv(path+'\\'+f)
                if 'Dividends' in f1.columns:
                    div_data = f1
                    price_data = pd.read_csv(path+'\\'+self.ticker+' (1).csv')
                else:
                    price_data = f1
                    div_data = pd.read_csv(path+'\\'+self.ticker+' (1).csv')
                break
        
        if rate.lower() ==  'dividend':
            return (div_data)
        elif rate.lower() == 'price':
            return (price_data)
        else:
            print('wrong rate string...')
    
    
    
    
    
    