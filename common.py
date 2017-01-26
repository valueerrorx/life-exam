import hashlib
import os
import ipaddress




def checkFirewall():
    result = os.system("sudo iptables -L |grep DROP|wc -l")
    if result != 0:
        print "stopping ip tables"
        os.system("./scripts/exam-firewall.sh stop &") 



def checkIP(iptest):
    try:
        ip = ipaddress.ip_address(iptest)
        return True
    except ValueError:
        return False
    except:
        return False


def validate_file_md5_hash(file, original_hash):
    """ Returns true if file MD5 hash matches with the provided one, false otherwise. """

    if get_file_md5_hash(file) == original_hash:
        return True
        
    return False



def get_file_md5_hash(file):
    """ Returns file MD5 hash"""
    
    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)
        
    return md5_hash.hexdigest()



def read_bytes_from_file(file, chunk_size = 8100):
    """ Read bytes from a file in chunks. """
    
    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if chunk:
                    yield chunk
            else:
                break



def clean_and_split_input(input):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """
    
    input = input.strip()
    input = input.split(' ')
        
    return input



def get_file_list(folder):
        """ Returns a list of the files in the specified directory as a dictionary:
            dict['file name'] = (file path, file size, file md5 hash)
        """
        # what if filename or foldername exists twice in tree ??  FIXME
        file_list = {}
        for root, subdirs, files in os.walk(folder):
            for filename in files:  # add all files to the list
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                md5_hash = get_file_md5_hash(file_path)
                file_list[filename] = (file_path, file_size, md5_hash)  #probably better to use path as index and filename as first value
            for subdir in subdirs:  # add folders to the list
                dir_path = os.path.join(root,subdir)
                file_list[subdir] = (dir_path, 0, 0)
        return file_list
    
    
    
def deleteFolderContent(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and the_file != ".stickyfolder":
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


