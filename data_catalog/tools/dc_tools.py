
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


