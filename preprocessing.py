import pandas as pd
import re
import ast

file_path = 'dataset/products_asos.csv'
df = pd.read_csv(file_path)

df = df.dropna()
df = df.drop_duplicates(subset='sku', keep=False)

df['images'] = df['images'].apply(lambda x: re.search(r"'(.*?)'", x).group(1) if pd.notnull(x) else x)
df = df.rename(columns={'images': 'image'})

df['color'] = df['color'].str.title()

df['description'] = df['description'].apply(ast.literal_eval)
indexes = list(df.index)
column_name = []
product_details = []
brand = []
size_fit = []
look_after_me = []
about_me = []

for i in indexes:
    dict_keys = []
    for j in range(0, len(df['description'][i])):
        dict_keys.append(str(df['description'][i][j].keys()).replace("dict_keys(['", "").replace("'])", ""))
    for entry in df['description'][i]:
        if i == 0:
            column_name.append(list(entry.keys())[0])

        if list(entry.keys())[0] == 'Product Details':
            if list(entry.values())[0] != '':
                product_details.append(list(entry.values())[0])
            else:
                product_details.append('Information not available')

        if list(entry.keys())[0] == 'Brand':
            brand.append(list(entry.values())[0])
        else:
            brand.append('Information not available')

        if list(entry.keys())[0] == 'Size & Fit':
            if list(entry.values())[0] != '':
                size_fit.append(list(entry.values())[0])
            else:
                size_fit.append('Information not available')

        if list(entry.keys())[0] == 'Look After Me':
            if list(entry.values())[0] != '':
                look_after_me.append(list(entry.values())[0])
            else:
                look_after_me.append('Information not available')

        if list(entry.keys())[0] == 'About Me':
            if list(entry.values())[0] != '':
                about_me.append(list(entry.values())[0])
            else:
                about_me.append('Information not available')

df['product details'] = product_details
df['brand'] = brand
df['size and fit'] = size_fit
df['look after me'] = look_after_me
df['about me'] = about_me

df = df.drop(columns=['description'])

df.to_csv('dataset/product_asos_clean', header=True)
