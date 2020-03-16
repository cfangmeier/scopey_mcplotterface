import lecroyreader as lcr
import matplotlib.pyplot as plt
import numpy as np
import matplotboard as mpb
from functools import lru_cache
import mplhep as hep


@lru_cache()
def get_trigger(folder, number, channel):
    from os.path import join
    filename = join(folder, f'{channel}step{number:05d}.trc')
    return lcr.read(filename)


def triggers_in_folder(folder, channel, limit=None):
    i = 1
    while i := i + 1:
        if limit and i > limit:
            break
        try:
            yield get_trigger(folder, i, channel)
        except FileNotFoundError:
            break


def get_trace(folder, number, channel):
    metadata, _, samples = get_trigger(folder, number, channel)
    times = np.linspace(0, samples.shape[0], samples.shape[0]) * metadata['horiz_interval']
    return times, samples


def traces_in_folder(folder, channel, limit=None):
    i = 0
    while i := i + 1:
        if limit and i > limit:
            break
        try:
            yield get_trace(folder, i, channel)
        except FileNotFoundError:
            break


def duration_of_experiment(folder, channel):
    import datetime
    all_times = [metadata['trigger_time'] for metadata, _, _ in triggers_in_folder(folder, channel)]

    def to_dt(a):
        secs, usecs = np.divmod(a[5], 1.0)
        return datetime.datetime(a[0], a[1], a[2], a[3], a[4], int(secs), int(usecs*1E6))
    duration = to_dt(all_times[-1]) - to_dt(all_times[0])
    return duration.seconds


def find_pulse_height(times, samples):
    idx = np.argmax(samples)
    return times[idx], samples[idx]


@mpb.decl_fig
def pulse_height_histogram(folder, title, channel):
    phs = []
    for data in traces_in_folder(folder, channel):
        _, sample_max = find_pulse_height(*data)
        phs.append(sample_max)
    h, bins = np.histogram(phs, bins=np.linspace(1.0, 3.0, 15))
    duration = duration_of_experiment(folder, channel)
    hep.histplot(h/duration, bins, yerr=np.sqrt(h)/duration, edges=True)
    plt.title(title)


@mpb.decl_fig
def pulse_height_comparison(dataset, title, channel):
    def get_phs(sub_dataset):
        folder = f'trace_data/{dataset}/{sub_dataset}'
        phs = [find_pulse_height(*data)[1] for data in traces_in_folder(folder, channel)]
        duration = duration_of_experiment(folder, channel)
        return phs, duration

    nosrc_phs, nosrc_duration = get_phs('nosrc')
    h, bins = np.histogram(nosrc_phs, bins=np.linspace(1.0, 3.0, 15))
    hep.histplot(h/nosrc_duration, bins, yerr=np.sqrt(h)/nosrc_duration, edges=True, label='Background')

    withsrc_phs, withsrc_duration = get_phs('withsrc')
    h, bins = np.histogram(withsrc_phs, bins=np.linspace(1.0, 3.0, 15))
    hep.histplot(h/withsrc_duration, bins, yerr=np.sqrt(h)/withsrc_duration, edges=True, label='Background+Signal')

    plt.title(title)
    plt.legend()

    return f'''
# Data Collected on {dataset}
  - *No Source*: {len(nosrc_phs)} Triggers over {nosrc_duration/3600:.2f} Hours
  - *With 1 uCi Cs-137 Source*: {len(withsrc_phs)} Triggers over {withsrc_duration/3600:.2f} Hours
'''

@mpb.decl_fig
def intensity_plot(folder, title, channel):
    for data in traces_in_folder(folder, channel):
        plt.plot(*data, 'b', alpha=0.4, linewidth=.1)
    plt.xlabel(r'Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.ylim((-0.25, 2.25))
    plt.title(title)
    plt.grid()


if __name__ == '__main__':
    dataset = '2020_03_13'
    nosrc = f'trace_data/{dataset}/nosrc/'
    withsrc = f'trace_data/{dataset}/withsrc/'
    plots = {
        # 'nosource': intensity_plot(nosrc, 'No Source', 'C4'),
        # 'withsource': intensity_plot(withsrc, 'With Source', 'C4'),
        # 'nosource-ph': pulse_height_histogram(nosrc, 'No Source', 'C4'),
        # 'withsource-ph': pulse_height_histogram(withsrc, 'With Source', 'C4'),
        'comparison-ph': pulse_height_comparison(dataset, 'Comparison', 'C4'),
    }
    mpb.render(plots)
    mpb.generate_report(plots, 'Scintillator Traces')
