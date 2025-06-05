import os 
import random 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

import datetime 
import calendar 
import holidays  

plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5

def plot_time_series( df , col  , strike , start_end_stamp , date , underlying , code  , save_dir = None  ): 
    start_time , end_time = start_end_stamp
    plt.figure()
    if col == 'Orb2_diff' or col == 'Spot Return %': 
        plt.plot( df.index[1:] , df[col][1:]  , 'o-' , color = 'r' , markersize=0.1)
    else : 
        plt.plot( df.index , df[col]  , 'o-' , color = 'r' , markersize=0.1)
    plt.xlim( start_time , end_time )
    plt.tight_layout()
    plt.xticks(
        ticks = pd.date_range(start=start_time, end=end_time, freq='1h') , 
        labels = pd.date_range( start = start_time  , end = end_time, freq = '1h' ).time
    )
    plt.grid()
    plt.title( f"{col} for {underlying}; exp: {code}; strike: {strike}; date : {date} {pd.to_datetime( date , dayfirst=True).day_name()}")
    if save_dir != None : 
        plt.savefig( save_dir )
    plt.show()



def plot_all_orb2( q  , col ): 
    for i , underlying in enumerate(q.main_dict) : 
        for code in q.main_dict[underlying] : 
            for date in q.main_dict[underlying][code] : 
                for strike  , df in q.main_dict[underlying][code][date]['Strike'].items() : 
                    plot_time_series(df,col,strike,q.main_dict[underlying][code][date]['Stamp'],date,underlying,code)




def print_dict_hierarchy(d, indent : int = 0 ): 
    for key , val in  d.items() : 
        print('|\t'*indent , key )
        if isinstance( val , dict ) : 
            print_dict_hierarchy( val , indent + 1 )