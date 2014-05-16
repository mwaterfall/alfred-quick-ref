# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys
import os
import json
import argparse

import alfred
from alfred_script_workflow import AlfredScriptWorkflow

ICON_ERROR = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
              '/Resources/AlertStopIcon.icns')

ICON_WARNING = ('/System/Library/CoreServices/CoreTypes.bundle/Contents'
                '/Resources/AlertCautionIcon.icns')


class InvalidConfiguration(Exception):
    """Raised if there is a problem parsing the configuration file"""


class QuickRefAlfredScriptWorkflow(AlfredScriptWorkflow):

    max_results = 50

    def __init__(self):
        """ Setup """
        self._lookup_dirs = None  # placeholder
        self.workflow_name = 'Quick Ref'
        super(QuickRefAlfredScriptWorkflow, self).__init__()

    def run(self):
        """Parse arguments and perform appropriate action"""
        parser = self._make_parser()
        try:
            args = parser.parse_args(alfred.args())
            if args.list_folders:
                self.do_list_folders()
            elif args.add_folder:
                self.do_add_folder(args.add_folder)
            elif args.delete_folder:
                self.do_delete_folder(args.delete_folder)
            else:
                self.do_search(args.query)
        except InvalidConfiguration:
            self.display_message('Invalid configuration.',
                                 'Please delete the configuration file.',
                                 icon=ICON_ERROR)
            return 1

    def do_list_folders(self):
        """Send list of configured folders to Alfred"""
        folders = self.lookup_dirs
        if not folders:
            self.display_message('No folders configured',
                                 "Use the 'Add QR Folder'"
                                 'File Action to add one',
                                 icon=ICON_WARNING)
            return 0
        items = []
        for path in folders:
            subtitle = path.replace(os.getenv('HOME'), '~')
            items.append(alfred.Item(
                         title=os.path.basename(path),
                         subtitle=subtitle,
                         attributes={
                             'arg': path,
                             'valid': 'yes'
                         },
                         icon=(path, {'type': 'fileicon'})))
        alfred.write(alfred.xml(items, maxresults=100))

    def do_add_folder(self, path):
        """Add folder to list of configured folders"""
        folders = self.lookup_dirs
        short_name = path.replace(os.getenv('HOME'), '~')
        if path in folders:
            print('Duplicate folder : {}'.format(short_name))
            return 0
        # Add folder
        folders.append(path)
        folders.sort()
        self._save_lookup_dirs(folders)
        print('Added : {}'.format(short_name))
        return 0

    def do_delete_folder(self, path):
        """Remove folder from list of configured folders"""
        folders = self.lookup_dirs
        short_name = path.replace(os.getenv('HOME'), '~')
        if path not in folders:
            print('Unknown folder : {}'.format(short_name))
            return 0
        folders.remove(path)
        self._save_lookup_dirs(folders)
        print('Removed : {}'.format(short_name))
        return 0

    def do_search(self, query):
        results = self.get_items_for_query(query)
        if not results:
            return self.display_message(
                'No matching documents found',
                icon=ICON_WARNING)

        # Create alfred items
        items = []
        for index, result in enumerate(results):
            path, filename = os.path.split(result)
            short_name = path.replace(os.getenv('HOME'), '~')
            items.append(alfred.Item(
                title=os.path.splitext(filename)[0],
                subtitle='Quick look {} in {}'.format(filename, short_name),
                attributes={
                    'uid': alfred.uid(index),
                    'arg': result,
                },
                icon=(result, {'type': 'fileicon'})
            ))
        alfred.write(alfred.xml(items, maxresults=self.max_results))
        return 0

    def get_items_for_query(self, query_str):
        """ Return items for the query string """

        results = []

        for lookup_dir in self.lookup_dirs:
            for root, dirnames, filenames in os.walk(lookup_dir):
                for filename in filenames:
                    if filename.startswith('.'):
                        continue  # exclude hidden files
                    full_path = os.path.join(root, filename)
                    hit = True
                    if query_str:
                        # Search path (excluding lookup_dir) and filename
                        search_path = full_path[len(lookup_dir):]
                        # Break search into keywords and
                        # ensure each is a match
                        for qp in query_str.split():
                            if qp.lower() not in search_path.lower():
                                # Search part not a match so exclude
                                hit = False
                                break
                    if hit:
                        results.append(full_path)

        return results

    def _make_parser(self):
        """Create and return an argument parser to handle script arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', dest='list_folders', action='store_true',
                            help='List configured folders')
        parser.add_argument('--add', dest='add_folder',
                            help='Add specified folder')
        parser.add_argument('--del', dest='delete_folder',
                            help='Delete specified folder')
        parser.add_argument('query', nargs='?', default='',
                            help='Search query')
        return parser

    @property
    def lookup_dirs(self):
        """Return list of directories stored in configuration"""
        if self._lookup_dirs is not None:  # return from cache if possible
            return self._lookup_dirs
        if not os.path.exists(self.config_path):
            return []
        with open(self.config_path, 'rb') as file:
            try:
                data = json.load(file)
            except (ValueError, TypeError):
                raise InvalidConfiguration()
        lookup_dirs = set()
        for dirpath in [os.path.expanduser(p.strip()) for p in
                        data.get('lookup_dirs', [])]:
            if os.path.isdir(dirpath):
                    lookup_dirs.add(dirpath)
        self._lookup_dirs = sorted(lookup_dirs)
        return self._lookup_dirs

    def _save_lookup_dirs(self, folders):
        """Write `folders` to configuration"""
        conf = {'lookup_dirs': folders}
        with open(self.config_path, 'wb') as file:
            json.dump(conf, file)


if __name__ == "__main__":
    wf = QuickRefAlfredScriptWorkflow()
    # Use return value of `run()` as exit status of script
    sys.exit(wf.run())
