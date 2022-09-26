import pandas as pd
import seaborn as sns

'''
    Function to simplify the MESH dataset and write it in a new csv file using 2022AA version. 

    Input:  path -> The path location of the complete MESH dataset in csv format.
    Output: A csv file written in data\Mesh_datasets\MESH_Clean.csv
'''

def cleaning_data(path):
    raw_df = pd.read_csv(path)


    #raw_df = raw_df.loc[raw_df["Obsolete"] == "FALSE"]
    print(raw_df.info())
    raw_df = raw_df.dropna(subset=["Semantic Types","Class ID"])
    #raw_df = raw_df.loc[raw_df["MeSH Frequency"]>0]
    print(raw_df.info())

    
    for row in raw_df.index:
        full_link = raw_df['Class ID'][row].split("/")
        raw_df['Class ID'][row] = full_link[len(full_link)-1]
        #print(raw_df['Class ID'][row])
        
 
    
    out_df = raw_df[["Class ID","Preferred Label","Semantic Types","MeSH Frequency"]]

    print(out_df.info())

    out_df.to_csv('data\Mesh_datasets\MESH_Clean.csv')


if __name__ == '__main__':
    cleaning_data("data\Mesh_datasets\MESH.csv")
    