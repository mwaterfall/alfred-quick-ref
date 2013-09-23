# -*- coding: utf-8 -*-

import os
import alfred


def process(query_str):
    """ Entry point """
    if query_str:
        results = get_results(query_str)
        if results is not None:
            response = alfred_items_for_results(results)
            xml = alfred.xml(response)  # compiles the XML answer
            alfred.write(xml)  # writes the XML back to Alfred


def get_results(query_str):
    """ Return value for the query string """
    results = []
    query_parts = query_str.split(' ')
    for root, subFolders, files in os.walk(lookup_dir):
        for file in files:
            if file.startswith('.'):
                continue  # exclude hidden files
            hit = False
            full_path = os.path.join(root, file)
            # Search path (excluding lookup_dir) and filename
            search_path = full_path[len(lookup_dir):]
            for qp in query_parts:
                if qp.lower() in search_path.lower():
                    hit = True
                    break
            if hit:
                results.append(full_path)
    return results


def alfred_items_for_results(items):
    """ Create alfred items for each result """
    index = 0
    results = []
    if not items:
        display_message(None, 'No documents found')
    for item in items:
        path, filename = os.path.split(item)
        results.append(alfred.Item(
            title=os.path.splitext(filename)[0],
            subtitle='Quick look %s in %s' % (filename, path),
            attributes={
                'uid': alfred.uid(index),
                'arg': item,
            },
            icon='icon.png',
        ))
        index += 1
    return results


def display_message(message, subtitle=None):
    """ Inform them that something's wrong """
    if message is None:
        # Display same message as the placeholder
        message = 'Quick reference documents'
    xml = alfred.xml([
        alfred.Item(
            title=message,
            subtitle=subtitle,
            attributes={
                'uid': alfred.uid(0),
            },
            icon='icon.png',
        )
    ])   # compiles the XML answer
    alfred.write(xml)  # writes the XML back to Alfred
    exit()


if __name__ == "__main__":
    lookup_dir = alfred.args()[0]
    lookup_dir = os.path.expanduser(lookup_dir)  # expand ~ if we can
    if not os.path.isdir(lookup_dir):
        display_message('Invalid lookup directory. Please edit in '
                        'workflow script filter.')
    query_str = alfred.args()[1]
    process(query_str)
