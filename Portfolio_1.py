'''
Created on Oct 8, 2019

@author: jnutala
'''
import os
import Portfolio_Process 
import time
import DataFilesUpdate


print('Type Y to start the program: ')
x = input()

DataFilesUpdate.UpdateFile()

if x != 'y' and x!= 'Y':
    print('You did not enter "Y" the program will now exit.')
    exit()    
print('\n')

###########STARTS THE PORTFOLIO PROCESS FILE#############################
cwd = os.getcwd()
my_portfolio = Portfolio_Process.Process(cwd+'\\Portfolio.json')
changes = False

while(True):
    chart = my_portfolio.get_pie_chart()
    chart.draw()
    chart.pause(0.001)
    
    print('This Portfolio: ')
    print('The Initial Amount is: $%d' %(my_portfolio.get_total_contribution()))
    print('Yearly Contribution is: $%d' %(my_portfolio.total_contribution))    
    print('The number of years of investment growth: ',my_portfolio.duration)
    print('The number of years of historic data used: %d' %my_portfolio.history)
    portfolio_value = my_portfolio.get_portfolio_valuation()
    print('The Total Valuation for this Portfolio is: $%s' %str(float('%0.2f'%portfolio_value[0][-1])))
    print('The Total Yearly Income for this Portfolio is: $%s'%str(float('%0.2f'%portfolio_value[1][-1])))
    print('The Total Contributed Amount for this Portfolio is: $%s\n'%str(float('%0.2f'%portfolio_value[2][-1])))
    
    for sector in my_portfolio.Sectors.values():
    #     sector = my_portfolio.Sectors[i] 
        print('The '+sector.get_sector_name()+' sector is '+str(sector.get_yearly_sector_contribution('percent'))+ ' of the portfolio.##########')
        sector_value = sector.get_sector_valuation()
        print('Total Sector Valuation of the Sector: $%s'%str(float('%0.2f'%sector_value[0][-1])))
        print('Total Sector Yearly Income: $%s' %str(float('%0.2f'%sector_value[1][-1])))
        print('Total amount contributed to this sector: $%s' %str(sector_value[2][-1]))
        print('Stocks in this sector: \n')
        for stock in sector.Stocks.values():
            div_rate = stock.get_div_growth_rate()
            print(stock.get_stock_name()+':')
            print('Ticker: '+stock.get_ticker())
            print('Initial Contribution: ' + str(stock.get_principal_amount()))
            print('Contribution in the sector: '+ str(stock.get_yearly_stock_contribution('dollar')))
            print('The last dividend rate is: '+ str(stock.get_div_growth_rate()[1]))
            if div_rate[2]==4:
                print('The dividend frequency is: Quarterly')
                x = 3
            elif div_rate[2]==12:
                print('The dividend frequency is: Monthly')
                x=1
            
            stock_valuation = stock.get_stock_valuation()
            print('The stock is valued at: $%s after the duration.'%str(stock_valuation[0][-1]))
            print('Total owned shares are: %s'%str(stock_valuation[3][-1]))
            print('The yearly income is: $%s'%str(stock_valuation[1][-1]))
            print('The total contributed is: $%s'%str(stock_valuation[2][-1]))
            print()
            
            print()
        print('\n')

    while(True):
        print("To add a new stock type: Add Stock")
        print('To remove a stock type: Remove Stock')
        print("To get the historic valuation of a Stock type: Historic Valuation")
        print('To Exit type: Exit')
        
        x = input()
        
        if x.lower() == 'exit':
            if changes == True:
                a = input('Would you like to save your changes?(Y/N)').lower()
                if a == 'y':
                    my_portfolio.write_to_file(cwd)
                    print('Save Complete.')
                    
            print('\nThe program will now exit.')
            exit()
        
        while(x.lower() == 'add stock'):
            print('Please add the new stock info in the Stock File.')
            print('Set the contributions of the rest of the stocks in the respective sector. ')
            print('If this stock belongs to a new sector then change the sector contributions accordingly.')
            print('Once you have completed, type "continue": ')
            a = input().lower()
            if a == 'continue':
                result = my_portfolio.add_stock_to_sector(cwd)
                if result == 'Success':
                    print('\nThe stock has been added!\n\n###########################################################################')
                    changes = True
                    time.sleep(1)
                    break
                else:
                    print('\n',result)
                    print()                    
            elif a == 'exit':
                print('\n')
                break
            else:
                print('You have not entered the correct input...')
    
    
        while(x.lower() == 'remove stock'):
            remove_stock = input('Please change the contributions of stocks in the respective sector and enter the stock you wish to remove: ')
            if remove_stock == 'exit':
                print('\n')
                break
                
            result = my_portfolio.remove_stock_from_sector(cwd,remove_stock)
            if result == 'success':
                print('\nThe stock has been removed!\n\n###########################################################################')
                changes = True
                time.sleep(1)
                break
            elif result == 'Stock DNE':
                print('The stock does not exit in the portfolio. Please re-enter.')
                
            else:
                print('Something went wrong...')
                time.sleep(2)
                break
            
        while(x.lower() == 'historic valuation'):
            print("\nThis historic valuation will display the valuation of your investment based on your principal amount and contribution.")
            print("The default history is 10 years back, or the IPO year of the stock if the stock is less than 10 years old.")
            print("Please add the stock info to the stock file")
            print('Once you have completed, type "continue": ')
            a = input().lower()
            if a == 'continue':
                result = my_portfolio.get_historic_valuation(cwd)
                if type(result) == list:
                    print('\n##### Historic Valuation For THIS STOCK:  ###########')
                    print('Total Valuation is: $',result[0])
                    print('Total Shares Owned is: ',result[1])
                    print('Total Contribution is: $', result[2])
                    print('The Yearly Income after ',result[3],' years is: $', result[4])  
                     
                    print('Final Dividend: ',float('%0.4f'%result[5]))
                    print('Final Price: $', float('%0.2f'%result[6]))
                    print('\n To continue press enter')
                    none = input('\n')
                    changes = True
                    time.sleep(1)
                    break
                else:
                    print('\n',result)
                    print()                    
            elif a == 'exit':
                print('\n')
                break
            else:
                print('You have not entered the correct input...')
        
        else:
            print('\nYou have not entered a valid response. Please try again.\n')
            
        break


