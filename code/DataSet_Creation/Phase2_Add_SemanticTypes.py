import os
import time
import pandas as pd
import multiprocessing as mp
from threading import Thread
from multiprocessing import Pool

dic_MeshToSemantic = {}


'''
    Function to load the dictionary that allows the translation between Mesh terms to Semantic Types 

    Input: 
    Output:
'''

def loadMeshToSemanticDic():
    df_MeshToSemantic = pd.read_csv("data//Mesh_datasets//Mesh_to_Semantic.csv")
    print(df_MeshToSemantic.head())
    
    for data in df_MeshToSemantic.to_dict('records'):
        dic_MeshToSemantic[data['Mesh id']] = str(data['Semantic Types']).split(',')
    
    #print(dic_MeshToSemantic)

def init_pool(the_dict):
        global globalDict
        globalDict = the_dict
        print("Initialized")

'''
    Function to Add Semantic types column, with the translation from Mesh terms to semantic types. 

    Input:  df -> A Pandas Dataframe with 3 columns  "PMID", "Title/Abstract", "MeshTerms"
            dic_MeshToSemantic -> A dictionary with the translation of the Mesh terms to Semantic Types
    Output: A Pandas Dataframe with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def add_SemanticTypes(df):
    global globalDict
    df_out = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms","SemanticTypes"])

    for ind in df.index:
        mesh_list = df['MeshTerms'][ind].split(';')
        semantic_list = set()
        for mesh in mesh_list:
            #if mesh in dic_MeshToSemantic:
            for semantic in globalDict[mesh]:
                semantic_list.add(semantic)
                
        semanticTypes = ";".join(semantic_list)
        #print(semanticTypes)
        df_out.loc[len(df_out)] = [df['PMID'][ind], df['Title/Abstract'][ind],df['MeshTerms'][ind],semanticTypes]
    

    return df_out

'''
    Function to process a Dataframes to enrich them with semantic types  

    Input:  info_dic -> A dictionary that contains all the information needed to process an article
                filename -> The name of the .tsv to be processed 
                path_in -> A folder with all the fragments of datasets
                path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def     process_article(info_dic):
    print(info_dic['filename'])
    df = pd.read_csv(info_dic['path_in']+"//"+info_dic['filename'],sep='\t')
    df = df.reset_index()
    df_out = add_SemanticTypes(df)
    df_out.to_csv(info_dic['path_out'] +"//"+info_dic['filename'].split('.')[0] + "_2.tsv",sep="\t")
    print(df_out.head())

'''
    Function to sequentially process multiple Dataframes to enrich them with semantic types    

    Input:  path_in -> A folder with all the fragments of datasets
            path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''


def process_articles_sequential(path_in,path_out):
    i = 0
    print("lol")
    #print(dic_MeshToSemantic)

    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            process_article({"filename":filename,"path_in":path_in,"path_out":path_out})
            i+=1
            if(i == 6): break


'''
    Function to process multiple Dataframes to enrich them with semantic types with parallelization techniques   

    Input:  path_in -> A folder with all the fragments of datasets
            path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def process_articles_concurrent(path_in,path_out):
    i = 0
    #print(dic_MeshToSemantic)

    # thread_size = 2
    # my_threads = []

    dataset_List = []

    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            dataset_List.append({"filename":filename,"path_in":path_in,"path_out":path_out})
            i+=1
    
    pool = mp.Pool(4, initializer= init_pool, initargs = (dic_MeshToSemantic,))

    try:
        pool.map(process_article, dataset_List)
    finally:
        pool.close()
        pool.join()

    




if __name__ == "__main__":
    loadMeshToSemanticDic()

    # start_time = time.time()
    # process_articles_sequential("data//phase1","data//phase2")
    # print("--- %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    process_articles_concurrent("data//phase1","data//phase2")
    print("--- %s seconds ---" % (time.time() - start_time))