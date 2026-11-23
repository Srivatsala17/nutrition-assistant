import glob
import os
import shutil

import kagglehub

path = kagglehub.dataset_download("batthulavinay/indian-food-nutrition")
print("Downloaded to:", path)

csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
print("CSV files found:", csv_files)

os.makedirs("data", exist_ok=True)
shutil.copy(csv_files[0], "data/raw_foods.csv")
print("Copied to data/raw_foods.csv")