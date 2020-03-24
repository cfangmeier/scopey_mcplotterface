#!/usr/bin/env python
from collections import defaultdict
import datetime
import lecroyreader as lcr
import uproot
import numpy as np


def triggers_in_folder(folder, channel):
    i = 1
    while i := i + 1:
        try:
            from os.path import join
            filename = join(folder, f'{channel}step{i:05d}.trc')
            yield lcr.read(filename)
        except FileNotFoundError:
            break


def find_pulse_height(samples):
    idx = np.argmax(samples)
    return samples[idx]


def collect_data(folder, channel):
    data = defaultdict(list)
    for metadata, _, samples in triggers_in_folder(folder, channel):
        for key, val in metadata.items():
            if key == 'trigger_time':
                secs, usecs = np.divmod(val[5], 1.0)
                dt = datetime.datetime(val[0], val[1], val[2], val[3], val[4], int(secs), int(usecs * 1E6))
                val = dt.timestamp()
            if type(val) in (int, float):
                data[key].append(val)
        data['pulse_height'].append(find_pulse_height(samples))
    for key, val in data.items():
        data[key] = np.array(val)
    return data


def save_data(folder, data):
    from os.path import join
    with uproot.recreate(join(folder, 'data.root')) as f:
        f['data'] = uproot.newtree({key: val.dtype for key, val in data.items()})
        f['data'].extend(data)


def main():
    import argparse
    parser = argparse.ArgumentParser('preprocess.py')
    parser.add_argument('dirs', nargs='+')
    args = parser.parse_args()
    for folder in args.dirs:
        data = collect_data(folder, 'C4')
        save_data(folder, data)


if __name__ == "__main__":
    main()
