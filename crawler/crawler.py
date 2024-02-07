
import datacat
import logging
import os
import time

from CDMSDataCatalog import CDMSDataCatalog
from datetime import date
from datetime import datetime

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
            self.resource_prefix = config['crawler']['resource_prefix']
    
        self.site = 'SLAC'
        if 'site' in config['crawler']:
            self.site = config['crawler']['site']

        log_fn = ('%s_crawler.log' % date.today().isoformat())
        logging.basicConfig(filename=log_fn, level=logging.INFO,
                            format="[%(levelname)s] %(asctime)s %(message)s")

    def get_dataset(self, path : str = '/CDMS'):
        try: 
            # Get the childen in the path to check if a folder needs to be explored
            children = self.dc.client.children(path)
    
            # This retrieves all datasets in the path excluding folders. If the path
            # doesn't contain a dataset, an empty list is returned.
            query = "scanStatus = 'UNSCANNED' or scanStatus = 'MISSING'" 
            datasets = self.dc.client.search(path, site=self.site, query=query)
        except requests.exceptions.HTTPError as err:
            logging.error('HTTPError %s' % err)
            return []

        # Loop through all the children and recursively retrieve the datasets.
        for child in children:
            if isinstance(child, datacat.model.Folder):
                datasets.extend(self.get_dataset(child.path))
                continue

        logging.info('Total datasets in %s : %s', path, len(datasets))
        return datasets

    def crawl(self):
        datasets = self.get_dataset(self.dc_path)

        for dataset in datasets:
            for loc in dataset.locations:
                if loc.site == self.site: 
                    payload = { 'locationScanned': datetime.utcnow().isoformat()+"Z" }
                    if os.path.exists(self.fs_prefix+loc.resource):
                        stat = os.stat(self.fs_prefix+loc.resource)
                        if loc.site == 'SLAC': payload['master'] = True
                        payload.update( {'scanStatus': 'OK', 'size': stat.st_size } )
                    elif loc.site == 'SNOLAB' and len(dataset.locations) > 1:
                        payload['scanStatus'] = 'ARCHIVED'
                        logging.info('File %s at %s has been ARCHIVED.', loc.resource, loc.site)
                    else: 
                        payload['scanStatus'] = 'MISSING'
                        logging.info('File %s at %s is MISSING.', loc.resource, loc.site)
                    
                    try: 
                        self.dc.client.patch_dataset(dataset.path, payload, site=self.site)
                    except DcException as err:
                        logging.error('DataCat Error: %s', err)


import argparse
import tomli

def main(args : argparse.Namespace) -> None: 
    '''
    '''

    if not args.config: 
        parser.error('A config file needs to be specified.')
    
    config = None
    with open(args.config, 'rb') as f:
        config = tomli.load(f)

    dc_config  = None
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
