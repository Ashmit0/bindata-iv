import os 
import random 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from tqdm import tqdm 
import pickle 

import datetime 
import calendar 
import holidays 

from datetime import time 
import py_vollib_vectorized as pvl 

plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5


from .utils import * 


def get_strike_gap( datesf2 , dates_log_path , inputs ) : 
    print('Initiating Strike Gap Processing:')
    st_gap = []
    symbol = inputs['underlying'] + '_' + inputs['exp']
    bar = tqdm(zip( datesf2 , dates_log_path ) , total = len(datesf2) , ncols = 125  )

    for date , path in bar :
        bar.set_postfix_str(f'Processing Strike Gap for {date}')  
        find_16 = False 
        temp_df = []
        
        for df in pd.read_csv(path , chunksize=10000 , usecols = [0,1,2,8] ) : 
            df.Time = pd.to_datetime( df.Time , format = "%H:%M:%S" ).dt.time 
            df = df.set_index("Time")
            df = df[df.index == time( 9 , 16 , 1 )]
            
            if not df.empty : 
                if not find_16 : 
                    find_16 = True 
                # keep only options symbols 
                df = df[(df.Symbol.str.startswith(symbol) )& (df.Symbol != symbol) ] 
                if not df.empty : 
                    df['Strike'] = df.Symbol.str.split('_' , expand = True )[3].astype(float)
                    temp_df.append( df.copy() )
            else : 
                if find_16 : 
                    if len( temp_df ) != 0  :
                        temp_df = pd.concat( temp_df , ignore_index= True )
                        unique , counts = np.unique(np.diff(temp_df.Strike.unique()) , return_counts = True )
                        st_gap.append( unique[counts == counts.max()].min() )
                    else : 
                        tqdm.write(f"Underlying Future for {inputs['underlying']} does not exist on {date}, the contract might have expired. Droping this date .........")
                    break 
                else : 
                    continue 
    return st_gap 



def init_df(date , inputs ) :
    df = pd.DataFrame() 

    df.index = pd.date_range(
        start =  date +  ' ' + "09:16:01" , 
        end = date  + ' ' + "15:30:01" , 
        freq= f"{inputs['dt']}min"
    )

    cols = ['Spot', 'ATM_Strike' , 'PE', 'CE']
    df[cols] = np.nan

    return df 


def fill_comn( df1 , df2 , col1 , col2 ) : 
    common_idx = df1.index.intersection(df2.index)
    df1.loc[common_idx , col1 ] = df2.loc[ common_idx , col2 ]


def create_df( date , path , gap , inputs  , files ) : 
    # init the df 
    df = init_df( date , inputs )
    
    # start reading the data in chunks :
    symbol = inputs['underlying'] + '_' + inputs['exp']

    # get the exp date : 
    exp_date = get_exp_date(date , inputs , files ) 

    for chunk in pd.read_csv(path, chunksize=100000, usecols = [1,2,8] ) :

        # convert the time to index : 
        chunk.Time = pd.to_datetime( date + ' ' + chunk.Time  )
        chunk = chunk.set_index('Time')
        chunk.Close = chunk.Close/100 

        # check if the time indices exist for the current chunk : 
        if chunk[ chunk.index.isin(df.index) ].empty: 
            continue 
        
        # Identify matching indices
        future_chunk = chunk[ chunk.Symbol == symbol ].copy() 
        
        # fill Spot values : 
        fill_comn( df , future_chunk , 'Spot' , 'Close')
        
        # get the ATM prices 
        future_chunk['ATM'] = (future_chunk['Close']/gap).round(0)*gap
        fill_comn( df , future_chunk , 'ATM_Strike' , 'ATM')
        
        # GET the ATM PUT and CALL close prices : 
        chunk  = chunk[
            chunk['Symbol'].str.startswith(symbol) & 
            (chunk['Symbol'] != symbol ) 
        ]
        split_cols = chunk['Symbol'].str.split('_', expand=True)
        chunk.loc[:, 'Strike'] = split_cols[3].astype(float)
        chunk.loc[:, 'Type'] = split_cols[5]
        
        df_reset = df.reset_index()
        chunk.reset_index( inplace = True )

        # Put : 
        matched = pd.merge(
            df_reset, 
            chunk, 
            left_on=['index', 'ATM_Strike'], 
            right_on=['Time', 'Strike'], 
            how='inner'
        ).set_index('index')
        fill_comn( df , matched[matched.Type == 'PE'] , 'PE' , 'Close' )
        fill_comn( df , matched[matched.Type == 'CE'] , 'CE' , 'Close' )
    
    if( df.isna().any().any() ) : 
        tqdm.write(f"Underlying Future for {inputs['underlying']} does not exist on {date}, the contract might have expired. Droping this date .........")
    else : 
        df['t'] = (( exp_date - pd.to_datetime( date ).date() ).days + 1 )/365
    return df 



def load_main_df( datesf1 , dates_log_path , st_gap , inputs , files  ): 
    print('Initiating Main DataFrame Processing:')
    df_list = []
    bar = tqdm(zip(datesf1 , dates_log_path , st_gap ) , total = len( datesf1) , ncols = 125 )

    for date, path, gap in bar : 
        file_name = get_file_name( date , inputs )

        # check if the corresponding picke file exists, if not create it : 
        try : 
            with open( file_name , 'rb' ) as f : 
                df = pickle.load( f )
                df = df.reindex(
                    pd.date_range(
                        start =  date +  ' ' + "09:16:01" , 
                        end = date  + ' ' + "15:30:01" , 
                        freq= f"{inputs['dt']}min"
                    )
                )
        except : 
            # init the data frame : 
            bar.set_postfix_str(f'Creating {file_name}. This is a one time process .....')
            df = create_df( date , path , gap , inputs , files  )
            with open( file_name , 'wb' ) as f : 
                pickle.dump( df , f )
            df = df.reindex(
                pd.date_range(
                    start =  date +  ' ' + "09:16:01" , 
                    end = date  + ' ' + "15:30:01" , 
                    freq= f"{inputs['dt']}min"
                )
            )
        
        df_list.append( df )

    if( len( df_list ) == 0 ) :
        raise ValueError('******No Valid Data Found******') 
    else : 
        main_df = pd.concat( df_list)
        return main_df 


def get_ivs( main_df , r): 
    main_df['CE_IV'] = pvl.implied_volatility.vectorized_implied_volatility_black(
        price = main_df['CE'] , 
        F = main_df['Spot'] , 
        K = main_df['ATM_Strike'] , 
        t = main_df['t'] , 
        r = r/100 , 
        flag = 'c' , 
        on_error = 'warn' , 
        return_as = 'array'
    ) * 100 


    # for put options using the black 76 model ; 
    main_df['PE_IV'] = pvl.implied_volatility.vectorized_implied_volatility_black(
        price = main_df['PE'] , 
        F = main_df['Spot'] , 
        K = main_df['ATM_Strike'] , 
        t = main_df['t'] , 
        r = r/100 , 
        flag = 'p' , 
        on_error = 'warn' , 
        return_as = 'array'
    ) * 100 

    main_df.drop( columns = ['ATM_Strike' , 'PE' , 'CE' , 't' ] , inplace = True )
    main_df.index.name = 'TimeStamp'
