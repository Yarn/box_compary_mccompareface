
from pathlib import PurePath, PureWindowsPath
import json

with open('../local_list.json') as f:
    local = json.load(f)

with open('../remote_list.json') as f:
    remote = json.load(f)

# remote = list(remote)
# print(remote)

# a = remote[0]
# b = PurePath(a)

# print(b)

local = {
    str(PurePath(PureWindowsPath(x['path']))): x
    for x in local
}

if isinstance(remote, list):
    remote = {
        str(PurePath(PureWindowsPath(x['path']))): x
        for x in remote
    }

local_paths = set(local)
remote_paths = set(remote)

only_local = local_paths - remote_paths
only_remote = remote_paths - local_paths

print(only_local)
print(only_remote)

print(len(local_paths))
print(len(only_local))

hash_mismatch = []

for path, remote_info in remote.items():
    print(path)
    
    if path not in local:
        assert path in only_remote
        continue
    
    local_info = local[path]
    
    print(remote_info)
    print(local_info)
    print(remote_info['sha1'] == local_info['sha1'])
    
    if remote_info['sha1'] != local_info['sha1']:
        hash_mismatch.append(path)
    
    # input()

print(hash_mismatch)

print()
print(f"local only : {len(only_local)}")
print(f"remote only: {len(only_remote)}")
print(f"mismatch   : {len(hash_mismatch)}")

with open('../only_local.txt', 'w') as f:
    for p in sorted(only_local):
        f.write(p)
        f.write('\n')

with open('../only_remote.txt', 'w') as f:
    for p in sorted(only_remote):
        f.write(p)
        f.write('\n')

with open('../hash_mismatch.txt', 'w') as f:
    for p in sorted(hash_mismatch):
        f.write(p)
        f.write('\n')
        f.write(f"  l:{local[p]['sha1']}\n")
        f.write(f"  r:{remote[p]['sha1']}\n")
