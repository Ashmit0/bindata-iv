import yaml 

with open('user_input.yaml', 'r') as f:
    inputs = yaml.safe_load(f)

from atm_data_lib.base import atm_data 

query = atm_data( inputs )
query.load_data()
query.save()