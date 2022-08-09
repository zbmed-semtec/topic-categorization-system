#ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/

import shutil
import time
import urllib.request as request
from contextlib import closing
from threading import Thread

url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC/'
files_list = ["PMC000XXXXX_xml_unicode.tar.gz", "PMC030XXXXX_xml_unicode.tar.gz", "PMC035XXXXX_xml_unicode.tar.gz", "PMC040XXXXX_xml_unicode.tar.gz", "PMC045XXXXX_xml_unicode.tar.gz", "PMC050XXXXX_xml_unicode.tar.gz", "PMC055XXXXX_xml_unicode.tar.gz",
                "PMC060XXXXX_xml_unicode.tar.gz", "PMC065XXXXX_xml_unicode.tar.gz", "PMC070XXXXX_xml_unicode.tar.gz", "PMC075XXXXX_xml_unicode.tar.gz", "PMC080XXXXX_xml_unicode.tar.gz", "PMC085XXXXX_xml_unicode.tar.gz", "PMC090XXXXX_xml_unicode.tar.gz"]
file_directory = 'C:\\Users\\sleep\\Desktop\\PDG\\Datasets\\'

class Downloader(Thread):
    def __init__(self, file_url, save_path):
        super(Downloader,self).__init__()
        self.file_url = file_url
        self.save_path = save_path

    def run(self):
        with closing(request.urlopen(self.file_url)) as r:
            with open(self.save_path, 'wb') as f:
                shutil.copyfileobj(r, f)

if __name__ == '__main__':
    my_threads = []
    for file in files_list:
        print(file)
        if len(my_threads) < 5:
            new_thread = Downloader(url+file, file_directory+file)
            new_thread.start()
            my_threads.append(new_thread)
        else:
            while len(my_threads) == 5:
                time.sleep(10)
                my_threads = [thread for thread in my_threads if thread.is_alive()]
            new_thread = Downloader(url+file, file_directory+file)
            new_thread.start()
            my_threads.append(new_thread)

    
