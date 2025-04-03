
from pprint import pprint
import sys
from pathlib import Path, PurePosixPath
import hashlib
import json

import requests
from util import get

def load_remote_list(folder_id, path_segs=tuple()):
    print(path_segs)
    
    marker = -1
    
    items = {}
    folders = []
    
    while marker is not None:
        url = f'https://api.box.com/2.0/folders/{folder_id}/items?usemarker=true&limit=1000&fields=type,id,name,sha1'
        
        if marker is not None and marker != -1:
            url += f"&marker={marker}"
        
        # print(marker)
        
        res = get(url)
        data = res.json()
        
        
        # pprint(data)
        # input()
        marker = data.get('next_marker')
        # del data['item_collection']
        # del data['entries']
        # print(data)
        # input()
        
        # for entry in data['item_collection']['entries']:
        for entry in data['entries']:
            # print(entry)
            
            # if entry['type'] == 'folder':
            #     remote_folders[entry['name']] = entry['id']
            
            # print(entry)
            if entry['type'] == 'file':
                pass
                # print(f"{entry['name']:<20} {entry['sha1']}")
                # remote_items[entry['name']] = entry['sha1']
                path = (*path_segs, entry['name'])
                items[path] = {'sha1': entry['sha1']}
            elif entry['type'] == 'folder':
                pass
                folders.append((entry['id'], entry['name']))
                # folder_items = load_remote_list(entry['id'], path_segs=(*path_segs, entry['name']))
                # items.update(folder_items)
    
    for folder_id, folder_name in folders:
        folder_items = load_remote_list(folder_id, path_segs=(*path_segs, folder_name))
        items.update(folder_items)
    
    return items

def check_folder(_local_path, folder, *, indent_level=0):
    output = Path(sys.argv[2])
    assert not output.exists()
    
    items = load_remote_list(folder)
    # pprint(items)
    
    
    with open(output, 'w') as f:
        out_items = {
            str(PurePosixPath(*k)): v
            for k, v in items.items()
        }
        json.dump(out_items, f, indent=2)

folder = sys.argv[1]
check_folder(None, folder)
