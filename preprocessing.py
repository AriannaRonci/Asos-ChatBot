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

def remove_common(a, b):
    for i in a[:]:
        if i in b:
            a.remove(i)
            b.remove(i)
    return a

for i in indexes:
    added_fields = ['Product Details', 'Brand', 'Size & Fit', 'Look After Me', 'About Me']
    dict_keys = []
    for j in range(0, len(df['description'][i])):
        dict_keys.append(str(df['description'][i][j].keys()).replace("dict_keys(['", "").replace("'])", ""))
    if dict_keys == added_fields:
        True
    else:
        missing = remove_common(added_fields, dict_keys)
        if missing.__contains__('Brand'):
            df['description'][i].insert(1, dict({'Brand': 'Information not available'}))
        if missing.__contains__('Size & Fit'):
            df['description'][i].insert(2, dict({'Size & Fit': 'Information not available'}))
        if missing.__contains__('Look After Me'):
            df['description'][i].insert(3, dict({'Look After Me': 'Information not available'}))
        if missing.__contains__('About Me'):
            df['description'][i].insert(4, dict({'About Me': 'Information not available'}))

    for entry in df['description'][i]:
        if i == 0:
            column_name.append(list(entry.keys())[0])

        if list(entry.keys())[0] == 'Product Details':
            product_details.append(list(entry.values())[0])

        if list(entry.keys())[0] == 'Brand':
            brand.append(list(entry.values())[0])

        if list(entry.keys())[0] == 'Size & Fit':
            size_fit.append(list(entry.values())[0])

        if list(entry.keys())[0] == 'Look After Me':
            look_after_me.append(list(entry.values())[0])

        if list(entry.keys())[0] == 'About Me':
            about_me.append(list(entry.values())[0])


df['product details'] = product_details
df['brand'] = brand
df['size and fit'] = size_fit
df['look after me'] = look_after_me
df['about me'] = about_me

df = df.drop(columns=['description'])

df.to_csv('dataset/product_asos_clean', header=True)
