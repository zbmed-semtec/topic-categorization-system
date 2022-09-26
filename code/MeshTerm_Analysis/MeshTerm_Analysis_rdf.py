from owlready2 import *
onto_path.append("/path/to/your/local/ontology/repository")

graph = Graph()

print("--- Reading Data ---")
graph.parse('.\data\Mesh_datasets\MESH_small.ttl', format='ttl')

list(default_world.sparql("""SELECT * { ?x a owl:Class . FILTER(ISIRI(?x)) }"""))

print("--- printing raw triples ---")
i = 0
for elem in graph:
    print(elem)
    print()
    i+=1
    if(i==10):
        break

