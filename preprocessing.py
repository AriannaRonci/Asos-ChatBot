import pandas as pd
import re

file_path = 'data/products_asos.csv'
df = pd.read_csv(file_path)

df = df.dropna()
df = df.drop_duplicates(subset='sku')

df['images'] = df['images'].apply(lambda x: re.search(r"'(.*?)'", x).group(1) if pd.notnull(x) else x)
df = df.rename(columns={'images': 'image'})

