import re


file = 'pg_high_ref1_R1_5866_g99_s200_eps80_i472_Gt11483.h5'


def get_variance_code(varstr):
    if varstr == 'low':
        return 0
    if varstr == 'med':
        return 1
    if varstr == 'high':
        return 2


def model_ripper(filename):
    name = filename.split('.')[0]
    components = name.split('_')

    hypers = {}
    for component in components:
        properties = re.split('(\d+)', component)
        if properties[0] == 'pg':
            continue
        if properties[0] == '':
            hypers['info'] = properties[1]
        if len(properties) == 1:
            hypers['var'] = get_variance_code(properties[0])
        else:
            if properties[0] == 'ref':
                hypers[properties[0]] = bool(properties[1])
            elif properties[0] == 'R':
                hypers[properties[0]] = bool(properties[1])
            elif properties[0] == 'g':
                hypers[properties[0]] = float(properties[1])/100
            else:
                hypers[properties[0]] = int(properties[1])

    return hypers


if __name__ == '__main__':
    print(model_ripper(file))
