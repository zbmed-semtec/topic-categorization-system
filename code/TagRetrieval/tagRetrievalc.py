'''
    This class is used as concurrent version of tagRetrieval.py
'''
import os
import time
from threading import Thread
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'TagRetrieval'))
import tagRetrieval as tr

directory_base = "D:\\PDG\\Datasets2\\Downloaded\\"
directory_destiny = "D:\\PDG\\Datasets2\\MeshTerms\\"

'''
    Function to extract the Mesh terms associated to an article and put them in an XML file.

    Input:  file ->  The path of the input xml file.
            directory_out -> The path where the resulting xml file will be stored.

    Output: A file with the Mesh terms files added to it, they are put in the <collection> tag, with the <DescriptorName> tag 
'''
def threadMeshTerms(file,directory_out):
    MeshList = tr.getMeshTerms(tr.getIds(tr.openXML(file)))
    tr.writeMeshTerms(file,directory_out,MeshList)


if __name__ == '__main__':
    
    start = time.time()

    my_threads = []
    for c in os.listdir(directory_base):
        dir = os.path.join(directory_base, c)
        for filename in os.listdir(dir):
            f = os.path.join(dir, filename)
            out_dir = directory_destiny+c+"\\"
            if(not os.path.isdir(out_dir)):
                os.mkdir(out_dir)
            #print(out_dir)
            if len(my_threads) < 5:
                #print("This is f: ",f)
                new_thread = Thread(target=threadMeshTerms, args=(f,out_dir,))
                new_thread.start()
                my_threads.append(new_thread)
            else:
                while len(my_threads) == 5:
                    #print(f)
                    time.sleep(1)
                    my_threads = [thread for thread in my_threads if thread.is_alive()]
                new_thread = Thread(target=threadMeshTerms, args=(f,out_dir,))
                new_thread.start()
                my_threads.append(new_thread)
    
    end = time.time()
    print(end - start)
    
