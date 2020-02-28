import lecroyreader as lcr
import matplotlib.pyplot as plt
import numpy as np
import matplotboard as mpb
from functools import lru_cache


@lru_cache()
def get_trace(folder, number, channel):
    from os.path import join
    filename = join(folder, f'{channel}step{number:05d}.trc')
    metadata, _, data = lcr.read(filename)
    times = np.linspace(0, data.shape[0], data.shape[0]) * metadata['horiz_interval']
    return times, data


@mpb.decl_fig
def intensity_plot(title, channel):
    for i in range(1019):
        trace = get_trace('trace_data/2020_02_27/', i, channel)
        plt.plot(*trace, 'b', alpha=0.4, linewidth=.1)
    plt.xlabel(r'Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.ylim((-0.25, 2.25))
    plt.title(title)
    plt.grid()


if __name__ == '__main__':
    plots = {
        'intensity-AND': intensity_plot('AND', 'C1'),
        'intensity-A1': intensity_plot('A1', 'C3'),
        'intensity-A2': intensity_plot('A2', 'C4'),
    }
    mpb.render(plots)
    mpb.generate_report(plots, 'Scintillator Traces')
