# -*- coding: utf-8 -*-

import os
import alfred
from alfred_script_workflow import AlfredScriptWorkflow


class QuickRefAlfredScriptWorkflow(AlfredScriptWorkflow):

    def __init__(self):
        """ Setup """

        # Info
        self.workflow_name = 'Quick Ref'

        # Config loaded with defaults
        self.config = {
            'lookup_dirs': ['~/Documents/Cheat Sheets']
        }

        # Continue init
        super(QuickRefAlfredScriptWorkflow, self).__init__()

    def read_config(self, data):
        """ Read config data and parse into `config` """

        # Lookup dirs (expand and unique)
        lookup_dirs = {}
        for ld in data['lookup_dirs']:
            if ld:
                # expand ~ for home if we can
                ld = os.path.expanduser(ld.strip())
                if os.path.isdir(ld):
                    lookup_dirs[ld] = None
        if not lookup_dirs.keys():
            self.display_config_prompt('No valid lookup directories')
        self.config['lookup_dirs'] = lookup_dirs.keys()

    def get_items_for_query(self, query_str):
        """ Return items for the query string """

        # Process
        results = []
        for lookup_dir in self.config['lookup_dirs']:
            for root, subFolders, files in os.walk(lookup_dir):
                for file in files:
                    if file.startswith('.'):
                        continue  # exclude hidden files
                    full_path = os.path.join(root, file)
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
        if not results:
            self.display_config_prompt(
                'No documents found',
                'Press return to modify configuration',
                append_config_message=False)

        # Create alfred items
        items = []
        index = 0
        for result in results:
            path, filename = os.path.split(result)
            items.append(alfred.Item(
                title=os.path.splitext(filename)[0],
                subtitle='Quick look %s in %s' % (filename, path),
                attributes={
                    'uid': alfred.uid(index),
                    'arg': result,
                },
                icon='icon.png',
            ))
            index += 1
        return items


if __name__ == "__main__":
    QuickRefAlfredScriptWorkflow()
