import yaml 
import sys 

with open('user_input.yaml', 'r') as f:
    inputs = yaml.safe_load(f)

if len(sys.argv) >= 5 : 
    inputs['underlying'] = sys.argv[1]
    inputs['start_date'] = sys.argv[2] 
    if len( sys.argv ) == 5 : 
        inputs['end_date'] = sys.argv[2]
        inputs['exp'] = sys.argv[3]
        inputs['num_gaps'] = sys.argv[4] 
    elif len( sys.argv ) == 6 : 
        inputs['end_date'] = sys.argv[3]
        inputs['exp'] = sys.argv[4]
        inputs['num_gaps'] = sys.argv[5] 
    else : 
        raise ValueError('In correct input lenght, either 0, 4 or 5' ) 

from atm_data_lib.base import atm_data 

query = atm_data( inputs )
query.load_data()
query.save()
