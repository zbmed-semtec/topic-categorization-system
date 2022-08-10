#ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/

import shutil
import urllib.request as request
from contextlib import closing
list_names = ["",]
with closing(request.urlopen('ftp://ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/PMC000XXXXX_xml_unicode.tar.gz')) as r:
    with open('D:\\PDG\\Datasets2\\test1.zip', 'wb') as f:
        shutil.copyfileobj(r, f)

