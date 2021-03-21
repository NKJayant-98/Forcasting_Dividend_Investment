'''
Created on Oct 24, 2019

@author: jnutala
'''

from Web_Element import web_data
import os
import datetime
import time

class UpdateFile:
    
    
    def __init__(self):
        
        ''' The data files in the Data Files folder will be updated if they are more than 6 days old. '''
        
        cwd = os.getcwd()
        files_path = cwd+"\\Data Files"
        files = os.listdir(files_path)
        
        try:
            stock_dt = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(files_path+'\\%s'%files[0])))
            stock_dt = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(files_path+'\\%s'%files[1])))
            stock_dt = datetime.datetime.strptime(stock_dt,'%m/%d/%Y')
            pivot = datetime.datetime.today() - datetime.timedelta(days=6)
        except:
            stock_dt,pivot = 1,2
        
        if stock_dt > pivot:
            print ('The Data Files are Up to Date')

        else:
            print('The Data Files need to be updated, this may take a few minutes...')
            
            for f in files:
                if '(' in f: 
                    continue
                f = f.split('TO')
                f = f[0]+'TO'
                print('The stock %s is being updated now...'%str(f))
                price = web_data().Download_Data(f)
                print('Update complete...\n')
            
            print ('\nThe Data Files have been updated...\n')

