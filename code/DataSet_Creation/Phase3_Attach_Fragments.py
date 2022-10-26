import os
import time
import pandas as pd

'''
    Function to process multiple Datasets to create a file containing all of them.

    Input:  path_in -> A folder with all the datasets
            path_out -> The folder where file containing all of them is going to be stored

    Output: A tsv file with 3 columns  "PMID", "Title/Abstract", "MeshTerms"
'''

def process_datasets(path_in,path_out):
    dfs = []
    df_out = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms","SemanticTypes"])
    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            print(filename)
            print(path_in+"//"+filename)
            df = pd.read_csv(path_in+"//"+filename,sep='\t')
            df.reset_index(drop=True, inplace=True)
            dfs.append(df) 

    df_out = pd.concat(dfs, axis=0)
    df_out = df_out.iloc[: , 1:]
    df_out.to_csv(path_out +"//final_dataset.tsv", index=False, sep="\t")

start_time = time.time()
process_datasets("data//phase2","data//phase3")
print("--- %s seconds ---" % (time.time() - start_time))