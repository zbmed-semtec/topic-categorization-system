import os
import time
import pandas as pd
from threading import Thread


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

'''
    Function to Add Semantic types column, with the translation from Mesh terms to semantic types. 

    Input:  df -> A Pandas Dataframe with 3 columns  "PMID", "Title/Abstract", "MeshTerms"
            dic_MeshToSemantic -> A dictionary with the translation of the Mesh terms to Semantic Types
    Output: A Pandas Dataframe with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def add_SemanticTypes(df):
    df_out = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms","SemanticTypes"])

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
    Function to process a Dataframes to enrich them with semantic types  

    Input:  filename -> The name of the .tsv to be processed 
            path_in -> A folder with all the fragments of datasets
            path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''

def process_article(filename,path_in,path_out):
    print(filename)
    df = pd.read_csv(path_in+"//"+filename,sep='\t')
    df = df.reset_index()
    df_out = add_SemanticTypes(df)
    df_out.to_csv(path_out +"//"+filename.split('.')[0] + "_2.tsv",sep="\t")
    print(df_out.head())

'''
    Function to sequentially process multiple Dataframes to enrich them with semantic types    

    Input:  path_in -> A folder with all the fragments of datasets
            path_out -> The folder where all the augmented fragments are going to be stored
            
    Output: A series of tsv files with 4 columns  "PMID", "Title/Abstract", "MeshTerms", "SemanticTypes"
'''


def process_articles_sequential(path_in,path_out):
    i = 0
    
    #print(dic_MeshToSemantic)

    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            process_article(filename,path_in,path_out)
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

    thread_size = 2
    my_threads = []

    dataset_List = []

    for filename in os.listdir(path_in):
        if filename.split('.')[-1] == "tsv":
            dataset_List.append(filename)
            i+=1
            if(i == 6): break
    
    for filename in dataset_List:
            
            if len(my_threads) < thread_size:
                #print("This is f: ",f)
                new_thread = Thread(target=process_article, args=(filename,path_in,path_out))
                new_thread.start()
                my_threads.append(new_thread)
            else:
                while len(my_threads) == thread_size:
                    #print(f)
                    #time.sleep(0.1)
                    my_threads = [thread for thread in my_threads if thread.is_alive()]
                new_thread = Thread(target=process_article, args=(filename,path_in,path_out))
                new_thread.start()
                my_threads.append(new_thread)         


loadMeshToSemanticDic()

# start_time = time.time()
# process_articles_sequential("data//phase1","data//phase2")
# print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
process_articles_concurrent("data//phase1","data//phase2")
print("--- %s seconds ---" % (time.time() - start_time))