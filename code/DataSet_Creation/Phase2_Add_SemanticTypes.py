import os
import time
import pandas as pd


'''
    Function to Add Semantic types column, with the translation from Mesh terms to semantic types. 

    Input:  df -> A Pandas Dataframe with 3 columns  "PMID", "Title/Abstract", "MeshTerms"
            dic_MeshToSemantic -> A dictionary with the translation of the Mesh terms to Semantic Types
    Output: A Pandas Dataframe with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def add_SemanticTypes(df,dic_MeshToSemantic):
    df_out = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms","SemanticTypes"])
    i = 0
    for ind in df.index:
        mesh_list = df['MeshTerms'][ind].split(';')
        semantic_list = set()
        for mesh in mesh_list:
            for semantic in dic_MeshToSemantic[mesh]:
                semantic_list.add(semantic)
        semanticTypes = ";".join(semantic_list)
        #print(semanticTypes)
        df_out.loc[len(df_out)] = [df['PMID'][ind], df['Title/Abstract'][ind],df['MeshTerms'][ind],semanticTypes]
    

    return df_out

'''
    Function to process multiple Dataframes to enrich them with semantic types  

    Input:  path_in -> A folder with all the fragments of datasets
            path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def process_articles(path_in,path_out):
    i = 0
    df_MeshToSemantic = pd.read_csv("data//Mesh_datasets//Mesh_to_Semantic.csv")
    print(df_MeshToSemantic.head())
    dic_MeshToSemantic = {}
    for data in df_MeshToSemantic.to_dict('records'):
        dic_MeshToSemantic[data['Mesh id']] = str(data['Semantic Types']).split(',')
    
    #print(dic_MeshToSemantic)

    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            print(filename)
            df = pd.read_csv(path_in+"//"+filename,sep='\t')
            df = df.reset_index()
            df_out = add_SemanticTypes(df,dic_MeshToSemantic)
            df_out.to_csv(path_out +"//"+filename.split('.')[0] + "_2.tsv",sep="\t")
            print(df_out.head())
        if(i == 0): break
            

start_time = time.time()
process_articles("data//phase1","data//phase2")
print("--- %s seconds ---" % (time.time() - start_time))