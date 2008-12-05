from zope.dottedname.resolve import resolve
_dotted_cache = {}

def resolve_dotted_name(dotted_name):
    """Resolve a dotted name to a real object
    """
    global _dotted_cache
    if dotted_name not in _dotted_cache:
        _dotted_cache[dotted_name] = resolve(dotted_name)
    return _dotted_cache[dotted_name]
    
def merged_tagged_value_dict(schema, name):
    tv = schema.queryTaggedValue(name, {})
    for base in schema.__bases__:
        tv.update(merged_tagged_value_dict(base, name))
    return tv

def merged_tagged_value_list(schema, name):
    tv = schema.queryTaggedValue(name, [])
    for base in schema.__bases__:
        tv.extend(merged_tagged_value_list(base, name))
    return tv