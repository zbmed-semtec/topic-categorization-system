import os
import sys
import time
sys.path.append('../code/TagRetrieval')
import tagRetrieval as tr


directory_base = "D:\\PDG\\Datasets2\\Downloaded\\"
directory_destiny = "D:\\PDG\\Datasets2\\MeshTerms\\"

start = time.time()

# iterate over files in
# that directory
for c in os.listdir(directory_base):
        dir = os.path.join(directory_base, c)
        for filename in os.listdir(dir):
            f = os.path.join(dir, filename)
            MeshList = tr.getMeshTerms(tr.getIds(tr.openXML(f)))
            if(len(MeshList)>0):
                out_dir = directory_destiny+c+"\\"
                #print(out_dir)
                if(not os.path.isdir(out_dir)):
                    os.mkdir(out_dir)
                tr.writeMeshTerms(f,out_dir,MeshList)      

end = time.time()
print(end - start)

