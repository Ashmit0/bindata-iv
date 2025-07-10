import yaml 
import sys 

with open('user_input.yaml', 'r') as f:
    inputs = yaml.safe_load(f)

if len(sys.argv) >= 3 : 
    inputs['underlying'] = sys.argv[1]
    inputs['start_date'] = sys.argv[2] 
    if len( sys.argv ) == 4 : 
        inputs['end_date'] = sys.argv[2]
        inputs['exp'] = sys.argv[3] 
    else : 
        inputs['end_date'] = sys.argv[3]
        inputs['exp'] = sys.argv[4]

from atm_data_lib.base import atm_data 

query = atm_data( inputs )
query.load_data()
query.save()
