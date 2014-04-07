import os
import json
import alfred
from subprocess import call


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

        # Handle init
        if alfred.args()[0] == 'run_config':

            if not os.path.exists(self.config_path):
                with open(self.config_path, 'wb') as file:
                    # dump default config
                    json.dump(self.config, file, indent=4)

            call(['open', self.config_path])

        else:
            if not os.path.exists(self.config_path):
                return self.display_config_prompt()
            # Read existing config
            try:
                with open(self.config_path, 'rb') as file:
                    config_data = json.load(file)
            except ValueError:
                return self.display_config_prompt(
                    'Invalid configuration',
                    'Config contains invalid JSON')
            try:
                self.read_config(config_data)
            except (ValueError, TypeError):
                return self.display_config_prompt('Invalid configuration')

            # Get query
            query_str = alfred.args()[1].strip()

            # Run
            if query_str == "config":
                self.display_config_prompt()
            else:
                self.process(query_str)

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

    def display_message(self, message, subtitle=None, arg=None):
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
                icon='icon.png',
            )
        ])   # compiles the XML answer
        alfred.write(xml)  # writes the XML back to Alfred

    def display_config_prompt(self, message=None, reason=None,
                              append_config_message=True):
        """ Workflow needs to be config """
        if message and append_config_message:
            message += '. Press return to configure %s.' % self.workflow_name
        elif message is None:
            message = 'Configure %s' % self.workflow_name
        self.display_message(message, reason, arg='!config')
