import pandas as pd
import seaborn as sns

STY_graph = {}
df_TP = pd.DataFrame()
STY_cnt = {}

'''
    Function  count of the appearances of a STY in the topic_categorization dataset.

    Input:  
    Output: A Dictionary with the  count of the appearances of a STY, when an STY appears its parents as well appear   
            {STY : CNT}
'''
def count_STY_in_Dataset():

    for i in df_TP.index: 
        #print(df_semantic["Semantic Types"][i])
        split_types = df_TP["SemanticTypes"][i].split(";")
        #print(split_types)
        for s_type_link in split_types:
            s_type = s_type_link.split("/")[-1]
            if(s_type in STY_cnt):
                STY_cnt[s_type] = STY_cnt[s_type] + 1
            else:
                STY_cnt[s_type] = 1

    for k,v in STY_cnt:
        curr = k
        while('#' not in STY_graph[curr][0]):
            curr = STY_graph[curr][0]
            STY_cnt[curr] += v

    print(sorted(STY_cnt.items(), key=lambda kv:(kv[1], kv[0])))

    

'''
    Function to load the complete topic_categorization dataset. 

    Input:  path -> The path location of the topic_categorization dataset in tsv format.
    Output: A DataFrame with all the topic_categorization dataset "PMID", "Title/Abstract", "MeshTerms","SemanticTypes"
'''
def load_Dataset(path):
    df_TP = pd.read_csv(path,sep='\t')
    print(df_TP.head())


'''
    Function create the STY tree. 

    Input:  path -> The path location of the complete STY dataset in csv format.
    Output: A dictionary representing the Semantic Type tree
            {STY ID : [Parent STY ID, STY Preferred Label]}
'''

def create_SemanticTree(path):
    raw_df = pd.read_csv(path)


    #raw_df = raw_df.loc[raw_df["Obsolete"] == "FALSE"]
    print(raw_df.head())
    
    print(raw_df.info())

    
    for row in raw_df.index:
        full_link = raw_df['Class ID'][row].split("/")
        full_link_parent = raw_df['Parents'][row].split("/")
        raw_df['Class ID'][row] = full_link[len(full_link)-1]
        STY_graph[full_link[-1]] = [full_link_parent[-1],raw_df['Preferred Label'][row]]
        #print(raw_df['Class ID'][row])
    


if __name__ == '__main__':
    create_SemanticTree("data\UMLS_datasets\STY.csv")
    #load_Dataset("data\phase3\final_dataset.tsv")
    #load_Dataset("data\phase2\Dataset_100000_2.tsv")
    #count_STY_in_Dataset()
    