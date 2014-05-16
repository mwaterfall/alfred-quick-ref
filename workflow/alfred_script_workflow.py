import os
# import json
import alfred
# from subprocess import call


config_filename = 'config.json'


class AlfredScriptWorkflow(object):

    max_results = 9

    def __init__(self):
        """ Setup """

        # Read bundle info and config path
        self.placeholder = ''
        for x in alfred.preferences['objects']:
            if x['type'] == 'alfred.workflow.input.scriptfilter':
                self.placeholder = x['config']['title']
        self.config_path = os.path.join(alfred.work(False), config_filename)

    def read_config(self, data):
        """ Read config data and parse into `config` """
        raise NotImplementedError()

    def process(self, query_str):
        """ Entry point """
        results = self.get_items_for_query(query_str)
        if results:
            xml = alfred.xml(results,
                             self.max_results)  # compiles the XML answer
            alfred.write(xml)  # writes the XML back to Alfred

    def get_items_for_query(self, query_str):
        """ Return items for the query string """
        raise NotImplementedError()

    def display_message(self, message, subtitle=None, arg=None,
                        icon='icon.png'):
        """ Inform them that something's wrong """
        if message is None:
            # Display same message as the placeholder
            message = self.placeholder
        xml = alfred.xml([
            alfred.Item(
                title=message,
                subtitle=subtitle,
                attributes={
                    'uid': alfred.uid(0),
                    'arg': arg
                },
                icon=icon
            )
        ])   # compiles the XML answer
        alfred.write(xml)  # writes the XML back to Alfred
