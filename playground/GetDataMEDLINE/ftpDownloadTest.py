#ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/

import shutil
import urllib.request as request
from contextlib import closing

with closing(request.urlopen('ftp://ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/BioC.dtd')) as r:
    with open('D:\\PDG\\Datasets2\\test.txt', 'wb') as f:
        shutil.copyfileobj(r, f)

