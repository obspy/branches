#!/usr/bin/env python
# -*- coding: utf-8 -*-

# run this file inside a project directory to create a data-vs-time plot
# out of pickle dumps.
# normally not necessary since the main script will to this periodically

import matplotlib.pyplot as plt
import pickle, os

plotfn = "data_vs_time.pdf"
dlplot_x_fp = 'dlplot_x.pickle'
dlplot_y_fp = 'dlplot_y.pickle'

dlplot_x_fh = open(dlplot_x_fp, 'rb')
dlplot_y_fh = open(dlplot_y_fp, 'rb')
dlplot_x = pickle.load(dlplot_x_fh)
dlplot_y = pickle.load(dlplot_y_fh)
dlplot_x_fh.close()
dlplot_y_fh.close()

# convert to hours and gigabytes
dlplot_x[:] = [x/(60.0*60*24) for x in dlplot_x]
dlplot_y[:] = [y/1024.0 for y in dlplot_y]

# save plot of database size versus elapsed download time
plt.plot(dlplot_x, dlplot_y)
plt.xlabel('Time in days')
plt.ylabel('Folder size in GB')
titlemsg = "Folder size vs elapsed time"
plt.savefig(plotfn)
