
from CDMSDataCatalog import CDMSDataCatalog

import datacat


def get_dataset(dc : CDMSDataCatalog, path : str):
    # Get the childen in the path to check if a folder needs to be explored
    children = dc.client.children(path)
    
    # This retrieves all datasets in the path excluding folders. If the path
    # doesn't contain a dataset, an empty list is returned.
    datasets = dc.client.search(path, site='All')

    # Loop through all the children and recursively retrieve the datasets.
    for child in children:
        if isinstance(child, datacat.model.Folder):
            datasets.extend(get_dataset(dc, child.path))
            continue

    print('Total datasets in', path, ':', len(datasets))
    return datasets

def get_resource_info(datasets):
    site_count = {}
    resource_prefix = {}

    for dataset in datasets:
        for loc in dataset.locations:

            if loc.site not in site_count:
                site_count[loc.site] = 0
            site_count[loc.site] += 1

            index = loc.resource.find('/CDMS')
            prefix = loc.resource[0:index]
            if prefix not in resource_prefix:
                resource_prefix[prefix] = 0
            resource_prefix[prefix] += 1

    print(site_count)
    print(resource_prefix)

def update_resource(dc : CDMSDataCatalog, datasets, site : str, prefix : str):

    for dataset in datasets: 
        new_resource = prefix+dataset.path
        patch_dataset(dc, dataset, site, new_resource)


def patch_dataset(dc : CDMSDataCatalog, dataset, site: str, resource : str):
    payload = {"resource": resource}
    try:
        dc.client.patch_dataset(dataset.path, payload, site='SLAC')
    except: return

import os

def find_unregistered(dc : CDMSDataCatalog, datasets, path : str, log_path : str):

    # List of files that are registered
    registered_files = [dataset.path for dataset in datasets]
       
    # Generate a list of unregistered files 
    #files = [os.path.join(path, f) for (dirpath, dirnames, filenames) in os.walk(path) for f in filenames]
    files = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in os.walk(path) for f in filenames]
    unregistered_files = [f for f in files if f[f.find('/CDMS'):] not in registered_files]

    log = open(log_path, 'w')
    log.write('Total unregisted files: ' + str(len(unregistered_files)) + '\n')
    for f in unregistered_files: log.write(f+'\n')
    log.close()

def set_master(dc : CDMSDataCatalog, datasets, path : str, resource_prefix: str, site : str):

    # Get the list of files on disk. The second processing is used to match 
    # the path of disk to the resource/
    files = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in os.walk(path) for f in filenames]
    files = [f[f.find(resource_prefix):] for f in files]

    # Loop through all files and extract the locations. If one of the locations
    # is associated with the given site and the file exists on disk, set it to
    # the master location.
    for dataset in datasets: 
        for loc in dataset.locations: 
            if loc.site == site: 
                if loc.resource in files:
                    payload = {'master' : True}
                    dc.client.patch_dataset(dataset.path, payload, site=site)
                else: 
                    print('File',loc.resource,'does not exist at', site)


    
