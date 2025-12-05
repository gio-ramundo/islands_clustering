import pickle
import os
import pandas as pd

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_raw.csv")
df = pd.read_csv(csv_path)

# Constraint list
cl_cons = []

# Iterate for islands
print(f'Total islands: {len(df)}')
for k,(ind,isl) in enumerate(df.iterrows(),0):
    if k%100 == 0:
        print(f'{k} islands made')
    cons = (isl.consumption)/1000000 # kWh to GWh
    # Nested iteration for comparison
    for k1,(ind1,isl1) in enumerate(df.iloc[k+1:].iterrows(),k+1):
        cons1 = (isl1.consumption)/1000000
        # Constraints creation
        if cons <= 1.8:
            if cons1 >= 2.2:
                cl_cons.append((ind,ind1))
        if cons > 1.8 and cons < 2.2:
            if cons1 >= 16.5:
                cl_cons.append((ind,ind1))
        if cons >= 2.2 and cons <= 13.5:
            if cons1 <= 1.8 or cons1 >= 16.5:
                cl_cons.append((ind,ind1))
        if cons > 13.5 and cons < 16.5:
            if cons1 <= 1.8 or cons1 >= 110:
                cl_cons.append((ind,ind1))
        if cons >= 16.5 and cons <= 90:
            if cons1  <= 13.5 or cons1  >= 110:
                cl_cons.append((ind,ind1))
        if cons>90 and cons<110:
            if cons1 <= 13.5:
                cl_cons.append((ind,ind1))
        if cons >= 110:
            if cons1 <= 90:
                cl_cons.append((ind,ind1))

# Expo
output_path = os.path.join(current_folder, 'cannot_link.pkl')
with open(output_path, 'wb') as f:
    pickle.dump(cl_cons, f)

# Constraints counter
print(f"Total cannot-link generated {len(cl_cons)}")
cont1 = (len(cl_cons)*2)/len(df)
print(f"An islands has {cont1} cannot-link on average")

# Total cannot-link generated 1088608
# An islands has 1082.1153081510934 cannot-link on average