import os, ftplib

url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/wilbur/BioC-PMC'
url = urlparse.urlparse(url)

local_root = os.path.expanduser("D:\\PDG\\Datasets2") # change this to wherever you want to download to

def download(ftp, ftp_path, filename, check_cwd=True):
    """
    Using the given ftp connection, download from ftp_path to 
    filename. 

    If check_cwd is False, assume the ftp connection is already 
    in the correct current working directory (cwd)
    """
    basename = posixpath.basename(ftp_path)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if check_cwd:
        ftp_dirname = posixpath.dirname(ftp_path)
        if ftp_dirname != ftp.pwd():
            ftp.cwd(ftp_dirname)

    with open(filename, 'w') as fobj:
        ftp.retrbinary('RETR %s' % basename, fobj.write)

def ftp_dir(ftp):
    """
    Given a valid ftp connection, get a list of 2-tuples of the
    files in the ftp current working directory, where the first
    element is whether the file is a directory and the second 
    element is the filename.
    """
    # use a callback to grab the ftp.dir() output in a list
    dir_listing = []
    ftp.dir(lambda x: dir_listing.append(x))
    return [(line[0].upper() == 'D', line.rsplit()[-1]) for line in dir_listing]

# connect to ftp
ftp = ftplib.FTP(url.netloc)
ftp.login()

# recursively walk through the directory and download each file, depth first
stack = [url.path]
while stack:
    path = stack.pop()
    ftp.cwd(path)

    # add all directories to the queue
    children = ftp_dir(ftp)
    dirs = [posixpath.join(path, child[1]) for child in children if child[0]]
    files = [posixpath.join(path, child[1]) for child in children if not child[0]] 
    stack.extend(dirs[::-1]) # add dirs reversed so they are popped out in order

    # download all files in the directory
    for filepath in files:
        download(ftp, filepath, os.path.join(local_root, filepath.split(url.path,1)[-1]), 
                                             check_cwd=False)

# logout
ftp.quit()