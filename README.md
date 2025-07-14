# Bindata_Processing

### Virtual Env 
Once cloned first create virtual env. To do this in the local directory 
```bash 
conda create <env_name> python=3.10
conda activate <env_name> 
```

Now install the required libraries 
```bash
conda install numpy pandas matplotlib  statsmodels tqdm 
pip install py_vollib_vectorized
pip install -e . 
```

### Cache Folder 

Create a Folder to store pickel files containing the preporossed intermidiate dataframes for each date. This helps in preventing recomputations.
```bash
mkdir cache 
```

### Usage 

First Make Sure to appropriately fill the `user_input.yaml` file. 

	- `dt` : Time window after which to calculate the IV. 

	- `parent_dir` : Path to folder with contains the bindata for each date in folders named in "YYYYMMDD" format. 

	- `r` : The intrest rate in percentage. 

	- `outfile` : Path to store the output .csv file that contains final result. 

	- `contractp` : Path to the contract master files. 

	- `underlying` (Optional) : Underlying to calculate the IVs for.

	- `exp` (Optional) : expiary code for the contract of intrest, example 'K25' for the month of may.

	- `start_date` (Optional) : ~ 

	- `end_date`  (Optional)  : range of dates in "YYYYMMDD" format to calcute the IVs. (Make sure to pass strings here like '20250519'. Its okay to include weekends) 

	- `num_gaps` (Optional) : number of strikes above and bellow the ATM strike to consider for analyis. 


To make a query for an underlying with a specified expiary for a given date range, the `underlying`, `start_date`, `end_date` and `exp` must be provided either in the yaml file or in the teminal command itself. 

### Queries 

If complete inputs are provided in the yaml file simply run : 
```bash 
python getiv.py 
``` 

To give inputs from the terminal use : 
```bash 
python getiv.py underlying start_date end_date exp num_gaps
```
example : 
```bash 
python getiv.py NSEFNO_BANKNIFTY 20250517 20250523 K25 10
``` 

Note: In case both terminal inputs and yaml inputs are provided, the yaml inputs are ignored. 

Note: To get the data for a single_date simply skip the end_date input in the terminal: 

```bash 
python getiv.py NSEFNO_NIFTY 20250101 F25 7
``` 

### Result Files 

the result files are named as `{underlying}_{start_date}_{end_date}_{exp}_{num_gaps}_atm_iv.csv` in the path provided in the `user_inputs.yaml` file. 
 
