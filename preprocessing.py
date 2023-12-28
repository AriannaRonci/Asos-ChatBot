import pandas as pd

file_path = 'dataset/products_asos.csv'
df = pd.read_csv(file_path)

df = df.dropna()
df = df.drop_duplicates(subset='sku')

'''unique = df['sku'].nunique()
print(unique)'''
