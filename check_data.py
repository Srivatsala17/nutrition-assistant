import pandas as pd

df = pd.read_csv("data/raw_foods.csv")
print(df.columns.tolist())
print(len(df))
print(df.head())

print(df.size)
print(df.shape)