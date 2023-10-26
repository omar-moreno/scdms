
import os

from CDMSDataCatalog import CDMSDataCatalog

def check_existence(old_resource : str, new_resource : str): 
    # Check for the existence of the old file
    if not os.path.isfile(old_resource): 
        print('Existing resource is no longer available:', old_resource)
        return False
    elif not os.path.isfile(new_resource): 
        print('New resource does not exist:', new_resource)
        return False

    return True
    
def patch_dataset(dc : CDMSDataCatalog, dataset, site: str, resource : str):
    payload = {"resource": resource}
    dc.client.patch_dataset(dataset.path, payload, site='SLAC')

def update_resource(dc : CDMSDataCatalog, path : str, site : str, prefix : str): 
    # Get a list of all the contents in the specified path
    content = dc.ls(path = path)
    
    # If path is empty, don't bother processing anything
    if len(content) == 0: return

    # Check the contents in each path
    for p in content:
        datasets = dc.client.search(p)
        print('%s : %s datasets' % (p, len(datasets)))
        # If there aren't any datasets, navigate deeper into the path
        if len(datasets) == 0: 
            update_resource(dc, p, site, prefix)
            continue

        # Each dataset is of type datacat.model.Dataset
        for dataset in datasets:
            # For each dataset, get the locations and find the one associated
            # with the given site.
            # Each location is of type datacat.model.DatasetLocation
            location = None
            for loc in dataset.locations: 
                if loc.site == site:
                    new_resource = prefix+dataset.path
                    if check_existence(loc.resource, new_resource): 
                        patch_dataset(dc, dataset, site, new_resource) 

def main(path : str, site : str, prefix : str):
    '''
    '''
    dc = CDMSDataCatalog()
    update_resource(dc, path, site, prefix)

import argparse

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', action='store', dest='path',
                        help='Data catalog path to files of interest.')
    parser.add_argument('-s', action='store', dest='site', 
                        help='The location site to update.')
    parser.add_argument('-l', action='store', dest='prefix', 
                        help='The prefix for the updated resource location.')
    args = parser.parse_args()

    main(args.path, args.site, args.prefix)
