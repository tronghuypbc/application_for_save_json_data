def output_json_object(key, val, last):
    if val is None:
        val = ''
    obj = ''
    obj += '\t\t"' + str(key).lower() + '" : '
    obj += '"' + str(val) + '"'
    if last != True:
        obj += ','
    obj += '\n'
    return obj