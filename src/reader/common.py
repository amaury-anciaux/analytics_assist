def elementtree_to_dict(element):
    node = dict()

    text = getattr(element, 'text', None)
    if text is not None:
        node['text'] = text

    node.update(element.attrib) # element's attributes
    node.pop('key')

    child_nodes = {}
    for child in element: # element's children
        child_nodes.setdefault(child.attrib['key'], []).append( elementtree_to_dict(child) )

    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        if len(value) == 1:
             child_nodes[key] = value[0]

    node.update(child_nodes.items())

    return node