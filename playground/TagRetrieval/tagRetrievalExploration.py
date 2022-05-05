#Source: https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

#Exploratory analysis of the PMC data set
def printTree(base,space):
	for child in base:
		str_out = ""
		for i in range(space):
			str_out+="--"
		print(str_out, child.tag, child.attrib)
		printTree(child,space+1)

tree = ET.parse('D:\PDG\Datasets\PMC000XXXXX_xml_unicode_small\PMC100320.xml')
 
# getting the parent tag of
# the xml document
root = tree.getroot()
 
# printing the root (parent) tag
# of the xml document, along with
# its memory location
print(root)
 
# printing the attributes of the
# first tag from the parent
print(root.tag)
 
# printing the text contained within
# first subtag of the 5th tag from
# the parent
print(root[0].attrib)

#printTree(root,0)
#Found the configuration where i could find the pmcid  
printTree(root[3][2],0)

#for i in range(5):
#	print(root[3][i].tag, root[3][i].attrib)
