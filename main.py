from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import uproot
import matplotboard as mpb
import mplhep as hep


def get_phs(dataset, sub_dataset):
    with uproot.open(join('trace_data', dataset, sub_dataset, 'data.root')) as f:
        phs = f['data'].array('pulse_height')
        phs += f['data'].array('acq_vert_offset')
        times = f['data'].array('trigger_time')
        duration = times.max() - times.min()
        return phs, duration


@mpb.decl_fig
def pulse_height_comparison(datasets, title):
    txt = ''
    hs = []
    durations = []
    _, axs = plt.subplots(2, 1, sharex='col',
                          gridspec_kw={'height_ratios': [1, 0.3]})
    plt.sca(axs[0])
    for dataset, subdataset, label in datasets:
        phs, duration = get_phs(dataset, subdataset)
        h, bins = np.histogram(phs, bins=np.linspace(0.0, 3.0, 30))
        hep.histplot(h/duration, bins, yerr=np.sqrt(h)/duration, edges=True, label=label)
        txt += f'  - {dataset}.{subdataset}: {len(phs)} Triggers over {duration/3600:.2f} Hours\n'
        hs.append(h)
        durations.append(duration)
    plt.title(title)
    plt.ylim(0, 0.20)
    plt.ylabel('Hz')
    plt.legend()

    # Add ratio
    plt.sca(axs[1])
    xs = (bins[:-1]+bins[1:])/2
    xerr = (bins[1:]-bins[:-1])/2
    ratio = (hs[1]/durations[1]) / (hs[0] / durations[0])
    ratio = np.nan_to_num(ratio, nan=0, posinf=0, neginf=0)
    yerr = abs(ratio) * np.sqrt(1/hs[1] + 1/hs[0])
    yerr = np.nan_to_num(yerr, nan=0, posinf=0, neginf=0)
    plt.errorbar(xs, ratio, xerr=xerr, yerr=yerr)
    plt.ylim(0.5, 2.0)
    plt.ylabel('(S+B)/B')
    plt.xlabel('Pulse Height (V)')

    return txt


if __name__ == '__main__':
    plt.style.use(hep.style.CMS)
    plots = {
        'comparison-ph1-2020_03_10': pulse_height_comparison([('2020_03_10', 'nosrc_1', 'Background'),
                                                              ('2020_03_10', 'withsrc_1', 'With Source'),
                                                              ], 'Comparison'),
        'comparison-ph2-2020_03_10': pulse_height_comparison([('2020_03_10', 'nosrc_2', 'Background'),
                                                              ('2020_03_10', 'withsrc_2', 'With Source'),
                                                              ], 'Comparison'),
        'comparison-ph1-2020_03_13': pulse_height_comparison([('2020_03_13', 'nosrc', 'Background'),
                                                              ('2020_03_13', 'withsrc', 'With Source'),
                                                              ], 'Comparison'),
    }
    mpb.render(plots)
    mpb.generate_report(plots, 'Scintillator Traces')
