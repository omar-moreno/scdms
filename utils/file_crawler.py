
import os
import pwd

def main(path : str): 
   
    user_dict = {}

    for root, dir_names, file_names in os.walk(path):
        for dir_name in dir_names: 
            dir_path = root+'/'+dir_name
            stats = os.stat(dir_path)
            uid = stats.st_uid
            user = pwd.getpwuid(uid)[0]
            if user not in user_dict: 
                user_dict[user] = []

            user_dict[user].append(dir_path)
        break

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
    args = parser.parse_args()

    main(args.path)

