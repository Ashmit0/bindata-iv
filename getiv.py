import os 
import yaml 
import random 
import pickle
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

from tqdm import tqdm 

with open('user_input.yaml', 'r') as f:
    inputs = yaml.safe_load(f)

from atm_data_lib.base import atm_data 

query = atm_data( inputs )
query.load_data()
query.save()