
import datacat

from CDMSDataCatalog import CDMSDataCatalog

class DCCrawler:

    def __init__(self, dc : CDMSDataCatalog, config):
        self.dc = dc

        if 'fs_prefix' not in config['crawler']: 
            raise ValueError('Failed to provide dataset prefix on filesystem.')
        self.fs_prefix = config['crawler']['fs_prefix']

        self.dc_path = '/CDMS'
        if 'dc_path' in config['crawler']:
            self.dc_path = config['crawler']['dc_path']

        self.resource_prefix = ''
        if 'resource_prefix' in config['crawler']:
            self.resource_prefix = config['crawler']['resource_prefix'])
    
        self.site = 'SLAC'
        if 'site' in config['crawler']:
            self.site = config['crawler']['site']

    def get_dataset(self, path : str = '/CDMS'): 
        # Get the childen in the path to check if a folder needs to be explored
        children = self.dc.client.children(path)
    
        # This retrieves all datasets in the path excluding folders. If the path
        # doesn't contain a dataset, an empty list is returned.
        datasets = self.dc.client.search(path, site='All')

        # Loop through all the children and recursively retrieve the datasets.
        for child in children:
            if isinstance(child, datacat.model.Folder):
                datasets.extend(self.get_dataset(child.path))
                continue

        print('Total datasets in', path, ':', len(datasets))
        return datasets

    def crawl(self, path : str = '/CDMS'):
        datasets = self.get_dataset(path)

        fs_path = self.fs_prefix+self.dc_path
        files = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in os.walk(fs_path) for f in filenames]
        files = [f[f.find(self.resource_prefix):] for f in files]

        for dataset in datasets: 
            for loc in dataset.locations: 
                if loc.site == self.site: 
                    print('Patching dataset.')
                    #payload = {'scanStatus': 'OK'}
                    #self.dc.client.patch_dataset(dataset.path, payload, site=self.site)
                    # TODO: Add timestamp

import argparse
import tomli

def main(args : argparse.Namespace) -> None: 
    '''
    '''

    dc_config  = None
    path = '/CDMS'
    
    if not args.config: 
        parser.error('A config file needs to be specified.')
    
    config = None
    with open(args.config, 'rb') as f:
        config = tomli.load(f)

    if 'config' in config['catalog']: 
        dc_config = config['catalog']['config']
    dc = CDMSDataCatalog(config_file=dc_config)
    
    crawler = DCCrawler(dc, config)

    crawler.crawl()

if __name__ == '__main__': 

    # Parse the command line arguments
    parser = argparse.ArgumentParser(
            description='Data catalog crawler used by the SCDMS experiment.')
    parser.add_argument('-c', action='store', dest='config',
                        help='Path to TOML based configuration file.')
    args = parser.parse_args()

    main(args)
