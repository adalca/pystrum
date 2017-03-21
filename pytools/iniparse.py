'''
very simple ini parser that expands on configparser
tries to cast values from string whereever possible
parsed data ini can be accessed with

data = ini_to_struct(file)
value = data.section.key

does not support hierarchical sections
'''

import configparser

class Struct():
    '''
    a simple struct class to allow for the following syntax:
    data = Struct()
    data.foo = 'bar'
    '''
    pass

def str_to_type(val, ctype):
    '''
    cast a string to a type (e.g. int('8')), with try/except
    '''
    ret = None
    success = True
    try:
        ret = ctype(val)
    except ValueError:
        success = False
    return (ret, success)



def str_to_bool(val):
    if val == 'True':
        return (True, True)
    elif val == 'False':
        return (False, True)
    else:
        return (None, False)



def str_to_list(val):
    val = val.replace('[', '')
    val = val.replace('(', '')
    val = val.replace(']', '')
    val = val.replace(')', '')

    if ',' in val:
        lst = val.split(',')
    else:
        lst = val.split()

    return lst


def str_convert_single(val):
    # try int
    ret, done = str_to_type(val, int)

    # try float
    if not done:
        ret, done = str_to_type(val, float)

    # try bool
    if not done:
        ret, done = str_to_bool(val)

    return (ret, done)


def ini_to_struct(file):
    ''' simple ini parser '''
    conf = configparser.ConfigParser()
    confout = conf.read(file)
    assert len(confout) > 0, 'Cannot read file %s ' % file

    strct = Struct()
    for sec in conf.sections():
        secstrct = Struct()

        for key in conf[sec]:
            val = conf[sec][key]

            # try single possibilities:
            ret, done = str_convert_single(val)

            if not done:
                lst = str_to_list(val)

                if len(lst) == 1:
                    ret = lst[0]  # still not done

                else:
                    done = all([str_convert_single(v)[1] for v in lst])
                    if done:
                        ret = [str_convert_single(v)[0] for v in lst]

            # try list
            if not done:
                ret = val  # accept string

            setattr(secstrct, key, ret)

        setattr(strct, sec, secstrct)
    return strct

