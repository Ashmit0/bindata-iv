import os 
import yaml 
import random 
import pickle
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from tqdm import tqdm 

from datetime import time 

random.seed( 17 )
import datetime 
import calendar 
import holidays 


plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5


from .utils import * 
from .preprocessing import *  




class atm_data: 

    def __init__(self,inputs) -> None:
        self.inputs = inputs 

        self.N = len(inputs['underlying'])

        # list of working dates 
        datesf1 = pd.date_range( start= inputs['start_date'] , end = inputs['end_date'] , freq = 'D' )
        self.datesf1 = datesf1.strftime( date_format= format1 ).to_list()
        #datesf1 = drop_weekends( datesf1 )


        # lof file paths : 
        self.dates_log_path = [ get_log_file_path( date ) for date in self.datesf1 if os.path.isfile(get_log_file_path(date)) ]
        dates_droped  = [ date  for date in self.datesf1 if ( not  os.path.isfile(get_log_file_path(date)) ) ]
        self.datesf1 = [ date for date in self.datesf1 if ( os.path.isfile(get_log_file_path(date))) ] 
        
        for date in dates_droped : 
            print(f"{date} not found in {inputs['parent_dir']}...") 
        
        # dates in standard format 
        self.datesf2 = format_dates( self.datesf1)
        
        self.files = [f[:7] for f in os.listdir(inputs['contractp']) if os.path.isfile(os.path.join(inputs['contractp'], f))]
    
    
    def load_data(self)-> None : 
        if not len(self.datesf1) : 
            return 
        # load st gap 
        self.st_gap = get_strike_gap( self.datesf2 , self.dates_log_path , self.inputs )
        # load main df : 
        self.main_df = load_main_df( self.datesf1 , self.dates_log_path , self.st_gap , self.inputs  , self.files)

        get_ivs( self.main_df , self.inputs['r'] , self.inputs )

    def save( self ) :
        if not len(self.datesf1) : 
            return 
        self.main_df.to_csv( os.path.join(self.inputs['outfile'] , '_'.join([self.inputs['underlying'],self.inputs['start_date'],self.inputs['end_date'] , self.inputs['exp'] , self.inputs['num_gaps'] , 'atm_iv.csv'])))



