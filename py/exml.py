"""this module parses .xml files"""

import re


def get_fields(data, id):
    results = []
    if type(data) == type([]):
        if len(data) > 0:
            for m in data:
                if type(m) == type([]):
                    if len(m) == 2:
                        if m[0] == id:
                            results.append(m[1])
    return results


def get_field(data, id):
    if type(data) == type([]):
        if len(data) == 1:
            if type(data[0]) == type([]):
                return get_field(data[0], id)
        elif len(data) == 2:
            if data[0] == id:
                return data[1]
        for m in data:
            if type(m) == type([]):
                if len(m) == 2:
                    if m[0] == id:
                        return m[1]
    raise KeyError("ERROR: exml: field '{}' not found".format(id))


def parse_tags(tags, debug_level=1):
    if len(tags) == 1:
        return tags[0]
    result = []
    t_start_i = 0  # index of opening tag
    raw_start_i = 0  # index of last closing tag + 1
    # raw_start_i is used to append raw text between tags
    while t_start_i < len(tags):
        t_start = tags[t_start_i]
        if t_start[0] == "<" and t_start[1] != "/":
            t_type = t_start.split(" ")[0][1:]
            if t_type.endswith(">"):  # true if no props
                t_type = t_type[:-1]
            t_end_i = t_start_i + 1
            while t_end_i < len(tags):
                t_end = tags[t_end_i]
                if t_end == "</{}>".format(t_type):
                    result.extend(tags[raw_start_i:t_start_i])
                    raw_start_i = t_end_i + 1
                    result.append(
                        [
                            t_type,
                            parse_tags(tags[t_start_i + 1 : t_end_i], debug_level),
                        ]
                    )
                    break
                t_end_i += 1
            t_start_i = t_end_i
        t_start_i += 1
    result.extend(tags[raw_start_i:])
    return result


def parse_str(str, debug_level=1):
    # match start, end tags and content
    tags = re.split("(<.+?>)", str)
    # strip whitespace
    tags = map(lambda m: m.strip("\t\n "), tags)
    # remove empty entries
    tags = list(filter(None, tags))
    return parse_tags(tags, debug_level)


def parse_file(path, debug_level=1):
    with open(path, "rt", encoding="utf-8") as f:
        return parse_str(f.read(), debug_level)
