
from pprint import pprint
import sys
from pathlib import Path
import hashlib

import requests
from util import get

def get_local_sha1(path):
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            
            sha1.update(data)
    
    return sha1.hexdigest()

# try:
#     folder = sys.argv[1]
# except IndexError:
#     folder = '0'

folder = sys.argv[1]
local_path = Path(sys.argv[2])
assert local_path.exists()
root_path = local_path

# url = f'https://api.box.com/2.0/folders/{folder}/'

# res = get(url)

# print(res.status_code)
# print(res.content)

# data = res.json()
# pprint(data)
# print()

def check_folder(local_path, folder, *, indent_level=0):
    url = f'https://api.box.com/2.0/folders/{folder}/'
    
    res = get(url)
    
    data = res.json()
    
    
    remote_items = {}
    remote_folders = {}
    
    for entry in data['item_collection']['entries']:
        if entry['type'] == 'folder':
            remote_folders[entry['name']] = entry['id']
        
        if entry['type'] != 'file':
            continue
        
        # print(f"{entry['name']:<20} {entry['sha1']}")
        remote_items[entry['name']] = entry['sha1']
    
    local_items = {}
    local_folders = {}
    
    for path in local_path.iterdir():
        # print(path)
        
        if path.is_dir():
            local_folders[path.name] = {
                'path': path
            }
            continue
        
        local_items[path.name] = {
            'hash': get_local_sha1(path),
            'path': path,
        }

    # print(local_items)
    # print(remote_items)

    # print()
    def iprint(*args, **kwargs):
        print(" " * indent_level, *args, sep='', **kwargs)
    
    for item_name, item_info in local_items.items():
        # iprint(item_info['path'].relative_to(root_path))
        
        if item_name not in remote_items:
            iprint(f'!{item_name} (not present on box)')
            continue
        
        if item_info['hash'] != remote_items[item_name]:
            iprint(f'!{item_name} (hash mismatch)')
            continue
        
        iprint(item_name)
    
    for folder_name, folder_info in local_folders.items():
        
        if folder_name not in remote_folders:
            iprint(f'!+{folder_name} (not present in box)')
            continue
        
        iprint('+', folder_name)
        check_folder(folder_info['path'], remote_folders[folder_name], indent_level=indent_level+1)

check_folder(local_path, folder)
