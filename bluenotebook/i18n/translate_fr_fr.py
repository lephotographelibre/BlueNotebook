import xml.etree.ElementTree as ET

def translate_fr_fr_file(input_filepath, output_filepath):
    # Register the namespace to avoid issues with writing the XML declaration
    ET.register_namespace('', "TS")
    tree = ET.parse(input_filepath)
    root = tree.getroot()

    for message in root.findall('.//message'):
        translation_node = message.find('translation')
        source_node = message.find('source')

        if source_node is not None and source_node.text:
            # If translation exists and is unfinished or empty, copy source
            if translation_node is not None and (translation_node.get('type') == 'unfinished' or not translation_node.text):
                translation_node.text = source_node.text
                if translation_node.get('type') == 'unfinished':
                    del translation_node.attrib['type']
            # If translation node does not exist, create it and copy source
            elif translation_node is None:
                new_translation = ET.SubElement(message, 'translation')
                new_translation.text = source_node.text

    # The ElementTree.write method does not include the DOCTYPE declaration.
    # We need to write it manually.
    with open(output_filepath, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(b'<!DOCTYPE TS>\n')
        tree.write(f, encoding='utf-8')

if __name__ == "__main__":
    translate_fr_fr_file('bluenotebook_fr.ts', 'bluenotebook_fr_translated.ts')
    print("Translation (FR-FR) complete. Output file: bluenotebook_fr_translated.ts")
