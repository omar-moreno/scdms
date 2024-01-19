
import os
import pwd

def main(path : str, depth : int = 1): 
   
    user_dict = {}
    path_length = len(path) + len(os.path.sep)
    for dpath, dnames, fnames in os.walk(path):
        level = dpath[path_length:].count(os.path.sep)
        if depth and level >= depth:
            dnames.clear()
        else: 
            for dname in dnames: 
                stats = os.stat(os.path.join(dpath, dname))
                uid = stats.st_uid
                user = pwd.getpwuid(uid)[0]
                if user not in user_dict: 
                    user_dict[user] = []

                user_dict[user].append(os.path.join(dpath, dname))

    with open('user_files.log', 'w') as f: 
        for key, value in user_dict.items():
            f.write('[ %s ]\n' % (key))
            for file_path in value: 
                f.write(file_path+'\n')

import argparse

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', action='store', dest='path',
                        help='Path to directory to crawl.')
    parser.add_argument('-d', action='store', dest='depth', 
                        help='The directory depth to crawl.')
    args = parser.parse_args()

    main(args.path, int(args.depth))

