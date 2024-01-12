
import datacat

from CDMSDataCatalog import CDMSDataCatalog

class DCCrawler:

    def __init__(self, dc : CDMSDataCatalog):
        self.dc = dc

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

import argparse
import tomli

def main(args : argparse.Namespace) -> None: 
    '''
    '''

    config = None
    dc_config  = None
    path = '/CDMS'
    if args.config:
        with open(args.config, 'rb') as f:
            config = tomli.load(f)

        if 'config' in config['catalog']: 
            dc_config = config['catalog']['config']
            print(dc_config)

        if 'path' in config['crawler']:
            path = config['crawler']['path']

    dc = CDMSDataCatalog(config_file=dc_config)

    crawler = DCCrawler(dc)

    crawler.crawl(path)


if __name__ == '__main__': 

    # Parse the command line arguments
    parser = argparse.ArgumentParser(
            description='Data catalog crawler used by the SCDMS experiment.')
    parser.add_argument('-c', action='store', dest='config',
                        help='Path to TOML based configuration file.')
    args = parser.parse_args()

    main(args)
