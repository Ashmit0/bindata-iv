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

Folder to store cache files for faster loading 
```bash
mkdir cache 
```