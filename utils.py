import base64
import csv


def file_put_contents(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


def str_2_b64(inp):
    return base64.b64encode(inp.encode('utf8')).decode('ascii')


def write_output_csv(filename, data):
    with open('out/' + filename, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for row in data:
            writer.writerow(row)


def get_nice_bytes(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return size, Dic_powerN[n] + 'bytes'
