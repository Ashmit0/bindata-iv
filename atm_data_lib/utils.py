import os 
import random 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

import datetime 
import calendar 
import holidays 

from tqdm import tqdm 

plt.rcParams['font.size'] = 14 
plt.rcParams['figure.figsize'] = (15,5)
plt.rcParams['lines.linewidth'] = .5

format1 = '%Y%m%d'
format2 = '%d-%m-%Y %H:%M:%S'


def drop_weekends(date_range: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Remove weekends (Saturday and Sunday) from a pandas date range."""
    return date_range[~date_range.weekday.isin([5, 6])]

# format from one fromat to another 
def format_dates(date_list):
    parsed_dates = pd.to_datetime(date_list, format='%Y%m%d')
    return parsed_dates.strftime('%d-%m-%Y').tolist()


def get_log_file_path( date_name : str , parent_dir : str =  '/data/NSE/bindata_indices/' ) : 
    dir = os.path.join( parent_dir , date_name , 'bin_data_archival_' + date_name + '.log')
    return dir 


month_to_nse_code = {
    1: 'F',   # January
    2: 'G',   # February
    3: 'H',   # March
    4: 'J',   # April
    5: 'K',   # May
    6: 'M',   # June
    7: 'N',   # July
    8: 'Q',   # August
    9: 'U',   # September
    10: 'V',  # October
    11: 'X',  # November
    12: 'Z'   # December
}


nse_code_to_month = {
    'F': 1,
    'G': 2,
    'H': 3,
    'J': 4,
    'K': 5,
    'M': 6,
    'N': 7,
    'Q': 8,
    'U': 9,
    'V': 10,
    'X': 11,
    'Z': 12
}



def last_thursday(year, month):
    # Find the last day of the month
    last_day = calendar.monthrange(year, month)[1]
    # Create a date object for the last day of the month
    last_date = datetime.date(year, month, last_day)
    # Calculate the offset to the last Thursday (weekday 3)
    offset = (last_date.weekday() - 3) % 7
    # Subtract the offset to get the last Thursday
    last_thursday_date = last_date - datetime.timedelta(days=offset)
    return last_thursday_date



def get_date_exp_code( date ) : 
    date = str( date )
    date  = pd.to_datetime(date )
    return month_to_nse_code[date.month] + str(date.year%100)


def get_code_date( code : str ): 
    month = nse_code_to_month( code[0] )
    year = 2000 + int( code[1:] )
    
    return last_thursday( year , month )


def get_file_name(date , inputs ) : 
    return f"cache/{date}_{inputs['underlying']}_{inputs['exp']}.pickel" 


india_holidays  = holidays.India()

def get_exp_date(date , inputs , files ):
    code = inputs['exp']
    exp_date = None 

    month = nse_code_to_month[code[0]]
    year = 2000 + int(code[1:])

    temp = pd.to_datetime(date).strftime(format = '%Y_%m')
    if  temp in files : 
        contract_path = [ os.path.join(inputs['contractp'], f) for f in os.listdir(inputs['contractp']) if f.startswith(temp) and os.path.isfile(os.path.join(inputs['contractp'], f))][0]
        contract = pd.read_csv( contract_path , compression='gzip' , usecols=[2,3,4,7])
        try : 
            contract = contract[(contract['type']=='FUT')&(contract['symbol'] == inputs['underlying'].split('_')[-1])]
            contract['exp_code'] = contract['expiry_date'].apply( get_date_exp_code )
            exp_date  = str(contract[ contract['exp_code'] == inputs['exp']]['expiry_date'].iloc[0])
            exp_date = pd.to_datetime( exp_date ).date()
            return exp_date
        except : 
            tqdm.write(f"Expiry Date for {inputs['underlying']} is not present in {contract_path}. Using Last Thursday of the Month Insted .... ")
    else : 
        tqdm.write(f'Contract Master for {year} {month} do not exist. Using Last Thursday of the month insted ....')

    exp_date = last_thursday( year , month )
    while exp_date in india_holidays : 
        exp_date  = exp_date - datetime.timedelta(days=1)
    return exp_date 