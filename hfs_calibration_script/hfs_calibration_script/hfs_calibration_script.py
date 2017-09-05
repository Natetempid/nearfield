
import numpy as np
import matplotlib.pyplot as plt
from scipy.odr import *
import random
import pandas as pd
#get data from file

#File Directories
start_dir = 'C:\Users\Nate\Dropbox (Minnich Lab)\PT Symmetry Project\Graphene - hBN\experimental_data\experiment_20170901_135142\intervalmeans_20170905_104846'
fluke_primary_dir = start_dir + '\\fluke8808a\primarydisplay.dat'
fluke_secondary_dir = start_dir + '\\fluke8808a\secondarydisplay.dat'
hfs_dir = start_dir + '\\daq9211\channel0.dat'

#Import data
fluke_primary_df = pd.read_csv(fluke_primary_dir, header = None)
fluke_primary_df.columns = ['time', 'mean', 'std']
fluke_secondary_df = pd.read_csv(fluke_secondary_dir, header = None)
fluke_secondary_df.columns = ['time', 'mean', 'std']
hfs_df = pd.read_csv(hfs_dir, header = None)
hfs_df.columns = ['time', 'mean', 'std']

#calculate input power and error
fluke_power = -1*fluke_primary_df['mean']*fluke_secondary_df['mean']
fluke_power_std = np.sqrt( fluke_primary_df['std']**2 + fluke_secondary_df['std']**2 )
area = 0.0285*0.0351

print(fluke_power.as_matrix())

# Initiate some data, giving some randomness using random.random().
#x = np.array([0, 1, 2, 3, 4, 5])
#y = np.array([i + random.random() for i in x])
#x_err = np.array([random.random() for i in x])
#y_err = np.array([random.random() for i in x])

x = fluke_power.as_matrix()/area
y = hfs_df['mean'].as_matrix()
x_err = fluke_power_std.as_matrix()
y_err = hfs_df['std'].as_matrix()

# Define a function (quadratic in our case) to fit the data with.
def lin_func(p, x):
     m, c = p
     return m*x + c

# Create a model for fitting.
quad_model = Model(lin_func)

# Create a RealData object using our initiated data from above.
data = RealData(x, y, sx=x_err, sy=y_err)

# Set up ODR with the model and data.
odr = ODR(data, quad_model, beta0=[0., 1.])

# Run the regression.
out = odr.run()

# Use the in-built pprint method to give us results.
out.pprint()

x_fit = np.linspace(0, np.max(x), 1000)
y_fit = lin_func(out.beta, x_fit)

plt.errorbar(x, y, xerr=x_err, yerr=y_err, linestyle='None', marker='x')
plt.plot(x_fit, y_fit)

plt.show()
