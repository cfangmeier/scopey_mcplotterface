import lecroyreader as lcr
import matplotlib.pyplot as plt
import numpy as np


def main():
    def read_n_plot(id_, channel):
        file = f'trace_data/C{channel}step{id_:05d}.trc'
        metadata, trigtimes, data = lcr.read(file)
        times = np.linspace(0, data.shape[1], data.shape[1])*metadata['horiz_interval']
        times *= 1E6  # to um
        plt.plot(times, data[0, :], label=f'C{channel}')
        return metadata

    for i in range(2, 11):
        plt.clf()
        read_n_plot(i, 1)
        read_n_plot(i, 3)
        metadata = read_n_plot(i, 4)
        plt.legend()
        plt.xlabel(r'$\mu$s')
        plt.ylabel('V')
        plt.grid()
        plt.savefig(f'traces/sample_{i}.png')


if __name__ == '__main__':
    main()
