'''
Created on Sep 27, 2019

@author: jnutala
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
import time
import os
import datetime

class web_data:
    def Download_Data(self,stock):
        #First check if the data files already are relatively new before downloading new ones
        #Saves alot of time. 
        #If the data files are more than 6 days old, the files will be updated. 
        try:
            cwd = os.getcwd()
            stock_dt = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(cwd+'\\Data Files\\%s (1).csv'%stock)))
            stock_dt = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(cwd+'\\Data Files\\%s.csv'%stock)))
            stock_dt = datetime.datetime.strptime(stock_dt,'%m/%d/%Y')
            pivot = datetime.datetime.today() - datetime.timedelta(days=6)
        except:
            stock_dt,pivot = 1,2
        
        if stock_dt > pivot:
            return_stock_price_only = True
        else:
            return_stock_price_only = False
        
        
        WINDOW_SIZE = "1980,1080"
        options = Options()
                
        options.add_experimental_option("prefs", {
          "download.default_directory": cwd+"\\Data Files",
          "download.prompt_for_download": False,
          "download.directory_upgrade": True,
          "safebrowsing.enabled": True
        })
        
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--headless")
        options.add_argument("windows-size%s" % WINDOW_SIZE)
        driver = webdriver.Chrome(options=options)
        
        ## Uncomment when testing without headless mode
#         driver = webdriver.Chrome() 
        
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': cwd+"\\Data Files"}}
        command_result = driver.execute("send_command", params)
        
        
        driver.get("https://ca.finance.yahoo.com/")
        
        print('Website has been reached.')
        time.sleep(3)
        
        elem = driver.find_element_by_xpath('//*[@id="yfin-usr-qry"]')
        elem.send_keys(stock)
        time.sleep(0.75)
        driver.find_element_by_xpath('//*[@id="search-button"]').click()
        
        # waits for the specific element in the text
        wait = WebDriverWait(driver, 20)
        check = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="quote-header-info"]/div[2]')))
         
        # obtaining the stock price and checking if the stock searched for is the correct one
        if stock in driver.find_element_by_xpath('//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1').text:            
            try:
                today_price = float(driver.find_element_by_xpath('//*[@id="quote-header-info"]/div[3]/div/div/span[1]').text)
                print('Stock check Complete.')
                
                if return_stock_price_only == True:#do no need to update the data files
                    driver.close()
                    return(today_price)
                
            except:
                print("There was an error in fetching today's price, please re-check. \nThe program will now exit")
                exit()
            
            
        else:
            print('The correct stock did not show up on the website, please check that the stock name matches the name from Yahoo Finance.')
        time.sleep(.5)
        
        #removing existing old-data files before downloading new ones
        files = os.listdir(cwd+'\\Data Files')
        if stock+'.csv' in files:
            try:
                os.remove(cwd+'\\Data Files\\%s.csv'%stock)
                os.remove(cwd+'\\Data Files\\%s (1).csv'%stock)
            except:
                print('One of the 2 data files exist, please investigate. The program will not exit...')
                exit()
                
        #DOWNLOADING NEW HISTORIC STOCK DATA##################33
        driver.find_element_by_xpath('//*[@id="quote-nav"]/ul/li[5]').click() #historical data
#         check = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/span/input'))) #waits 
        time.sleep(1)
        
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div').click() #time period
        driver.find_element_by_xpath('//*[@id="dropdown-menu"]/div/ul[2]/li[4]').click() #max_data
#         driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]').click() #click done
        
        # Stock Splits ******* #As of Oct 6th 2019, the dividend values take into account the splits as well ##############
        '''
        stock_splits = []
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div').click() #show:
        driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div[2]//*[contains(text(), "Stock Splits")]')[0].click() #Stock Splits
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click() #apply
        check = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table'))) #waits 
        time.sleep(2)
                                                                        
        for tr in driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody'):
            tds = tr.find_elements_by_tag_name('tr')
            data = ([td.text for td in tds])
        
        for i in data:#creating a list of stock splits and the ratios
            if 'No Split' in i:
                stock_splits.append('none')
                break
            if '1/0' in i:
                if len(data) == 1:
                    stock_splits.append('none')
                continue
            
            x = []
            x.append(datetime.datetime.strptime(i[:12],'%b %d, %Y'))
            x.append(int(data[0][13:14])/int(data[0][15:16]))
            stock_splits.append(x)
        '''
        
        #Historical Prices****
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div').click() #show:
        driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div[2]//*[contains(text(), "Historical Prices")]')[0].click()
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[3]/span/div').click() #Frequency: 
        driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[3]/span/div[2]//*[contains(text(), "Monthly")]')[0].click() #Monthly
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click() #apply
        
        check = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/thead/tr/th[5]/span'))) #waits 
        print('The prices data has been selected...')
        time.sleep(.75)
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]').click()
        time.sleep(3)
        #Rename price data file here:
        src = cwd+"\\Data Files\\%s.csv"%stock
        dst = cwd+"\\Data Files\\%s (1).csv"%stock
        os.rename(src,dst)
        
        
        #Dividends data****
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div').click() #show: 
        driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[2]/span/div[2]//*[contains(text(), "Dividends Only")]')[0].click()
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[3]/span/div').click() #Frequency: 
        driver.find_elements_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[3]/span/div[2]//*[contains(text(), "Monthly")]')[0].click() #Monthly
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()
        
        check = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/thead/tr/th[2]/span'))) #waits 
        print('The dividend Data has been selected...')
        time.sleep(.75)
        driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]').click()
        time.sleep(2)
        
        
        
        driver.close()
        
        return(today_price)
        

# uncomment for testing the code
# print('The function is in progress...')
# lst = web_data().Download_Data('ENB.TO')
# 
# print('\nThe list is: ',lst)
