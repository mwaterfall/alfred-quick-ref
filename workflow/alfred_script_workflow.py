import os
import json
import alfred
import plistlib
from subprocess import call

alfred_config_path = '~/Library/Application Support/Alfred 2/Workflow Data/'
config_filename = 'config.json'


class AlfredScriptWorkflow(object):

    def __init__(self):
        """ Setup """

        # Read bundle info and config path
        self.bundle_id = plistlib.readPlist(
            os.path.abspath('./info.plist'))['bundleid']
        self.placeholder = ''
        for x in plistlib.readPlist(
                os.path.abspath('./info.plist'))['objects']:
            if x['type'] == 'alfred.workflow.input.scriptfilter':
                self.placeholder = x['config']['title']
        self.config_path = '%s/%s/' % (
            os.path.expanduser(alfred_config_path).rstrip('/'),
            self.bundle_id,
        )

        # Handle init
        if alfred.args()[0] == 'run_config':

            # Create config if doesn't exist and then open in textedit
            try:
                os.makedirs(self.config_path)
            except OSError:
                # Exists
                pass
            if not os.path.exists(self.config_path + config_filename):
                config_file = open(self.config_path + config_filename, 'w')
                # dump default config
                config_file.write(json.dumps(self.config, indent=4))
                config_file.close()
            call(['open', '-a', 'TextEdit',
                  self.config_path + config_filename])

        else:

            # Read existing config
            config_file = None
            try:
                config_file = open(self.config_path + config_filename, 'r')
                config_data = json.loads(''.join(config_file.readlines()))
            except IOError:
                self.display_config_prompt()  # Config file doesnt exist
            except ValueError:
                self.display_config_prompt('Invalid configuration',
                                     'Config contains invalid JSON')
            finally:
                if config_file:
                    config_file.close()
            try:
                self.read_config(config_data)
            except (ValueError, TypeError):
                self.display_config_prompt('Invalid configuration')

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
            xml = alfred.xml(results)  # compiles the XML answer
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
        exit()

    def display_config_prompt(self, message=None, reason=None,
                              append_config_message=True):
        """ Workflow needs to be config """
        if message and append_config_message:
            message += '. Press return to configure %s.' % self.workflow_name
        elif message is None:
            message = 'Configure %s' % self.workflow_name
        self.display_message(message, reason, arg='!config')
