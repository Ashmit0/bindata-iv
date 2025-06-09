from tqdm import tqdm
import time

for i in tqdm(range(5)):
    tqdm.write(f"done with {i}/5")
    time.sleep(0.5)
