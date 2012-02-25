import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from matplotlib.ticker import NullFormatter, MultipleLocator, NullLocator
from tf_misfit import *

tmax = 6.
dt = 0.01
npts = int(tmax / dt + 1)

fmin = 1.
fmax = 10
nf = 100

clims = .1
ylims = .19
cm = 'RdBu'

w0 = 6

# Constants for S1
A1 = 4.
t1 = 2.
f1 = 2.
phi1 = 0.

# Constants for S1t and S1a
ps = 0.1
A1a = A1 * 1.1

# Constants for S2
A2 = 1.
t2 = 3.5
f2 = 3.
phi2 = 0.

t = np.linspace(0., tmax, npts)
f = np.logspace(np.log10(fmin), np.log10(fmax), nf)

H = lambda t: (np.sign(t) + 1)/ 2 

S1 = lambda t: A1 * (t - t1) * np.exp(-2*(t - t1)) * np.cos(2. * np.pi * f1 * \
               (t - t1) + phi1 * np.pi) * H(t - t1)
S2 = lambda t: A2 * np.exp(-2*(t - t2)**2) * np.cos(2. * np.pi * f2 * (t - t2) \
               + phi2 * np.pi)
S12 = lambda t: S1(t) + S2(t)

# generate analytical signal (hilbert transform) and add phase shift
s1h = hilbert(S1(t))
s1p = np.real(np.abs(s1h) * np.exp(np.angle(s1h) * 1j + ps * np.pi * 1j))

# signal with amplitude error
S1a = lambda t: A1a * (t - t1) * np.exp(-2*(t - t1)) * np.cos(2. * np.pi * f1 * \
                (t - t1) + phi1 * np.pi) * H(t - t1)

###############################################################################
# plotting constants

left = 0.1
bottom = 0.1
h_1 = 0.2
h_2 = 0.125
h_3 = 0.2

w_1 = 0.2
w_2 = 0.6
w_cb = 0.01
d_cb = 0.0

################################################################################
# Plot S1 and S1t and TFEM + TFPM misfits
fig = plt.figure()

# plot signals
ax_sig = fig.add_axes([left + w_1, bottom + h_2 + h_3, w_2, h_1])
ax_sig.plot(t, S1(t), 'k')
ax_sig.plot(t, s1p, 'r')

# plot TEM
TEM_11p = TEM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TEM = fig.add_axes([left + w_1, bottom + h_1 + h_2 + h_3, w_2, h_2])
ax_TEM.plot(t, TEM_11p)
ax_TEM.set_ylim(-ylims, ylims)

# plot TFEM
TFEM_11p = TFEM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TFEM = fig.add_axes([left + w_1, bottom + h_1 + 2*h_2 + h_3, w_2, h_3])
ax_TFEM.imshow(TFEM_11p, interpolation='nearest', cmap=cm, extent=[t[0], t[-1],
               f[0], f[-1]], aspect='auto', vmin=-clims, vmax=clims,
               origin='lower')
ax_TFEM.set_yscale('log')

# plot FEM
FEM_11p = FEM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_FEM = fig.add_axes([left, bottom + h_1 + 2*h_2 + h_3, w_1, h_3])
ax_FEM.semilogy(FEM_11p, f)
ax_FEM.set_xlim(-ylims, ylims)
ax_FEM.set_ylim(fmin, fmax)

# plot TPM
TPM_11p = TPM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TPM = fig.add_axes([left + w_1, bottom, w_2, h_2])
ax_TPM.plot(t, TPM_11p)
ax_TPM.set_ylim(-ylims, ylims)

# plot TFPM
TFPM_11p = TFPM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TFPM = fig.add_axes([left + w_1, bottom + h_2, w_2, h_3])
img = ax_TFPM.imshow(TFPM_11p, interpolation='nearest', cmap=cm, extent=[t[0],
                     t[-1], f[0], f[-1]], aspect='auto', vmin=-clims,
                     vmax=clims, origin='lower')
ax_TFPM.set_yscale('log')

# add colorbar
ax_cb = fig.add_axes([left + w_1 + w_2 + d_cb + w_cb, bottom, w_cb, h_2 + h_3])
fig.colorbar(img, cax=ax_cb)

# plot FPM
FPM_11p = FPM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_FPM = fig.add_axes([left, bottom + h_2, w_1, h_3])
ax_FPM.semilogy(FPM_11p, f)
ax_FPM.set_xlim(-ylims, ylims)
ax_FPM.set_ylim(fmin, fmax)

# add text box for EM + PM
PM_11p = PM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
EM_11p = EM(S1(t), s1p, dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_EMPM = fig.add_axes([left, bottom + h_2 + h_3 + h_1 / 2., w_1 * .7, (h_1 +
                        h_2) / 3.])
textstr = 'EM = %.2f\nPM = %.2f' % (EM_11p, PM_11p)
ax_EMPM.text(0.05, 0.1, textstr)

ax_TPM.set_xlabel('time / seconds')
ax_FEM.set_ylabel('f / Hz')
ax_FPM.set_ylabel('f / Hz')

ax_TFEM.set_title('TFEM', x=0.9, y=0.75)
ax_TFPM.set_title('TFPM', x=0.9, y=0.75)
ax_TEM.set_title('TEM', x=0.9, y=0.65)
ax_TPM.set_title('TPM', x=0.9, y=0.65)

ax_FEM.set_title('FEM', x=0.8, y=0.75)
ax_FPM.set_title('FPM', x=0.8, y=0.75)

ax_TFPM.xaxis.set_major_formatter(NullFormatter())
ax_TFEM.xaxis.set_major_formatter(NullFormatter())
ax_TEM.xaxis.set_major_formatter(NullFormatter())
ax_sig.xaxis.set_major_formatter(NullFormatter())

ax_TFPM.yaxis.set_major_formatter(NullFormatter())
ax_TFEM.yaxis.set_major_formatter(NullFormatter())

ax_TEM.yaxis.set_major_locator(MultipleLocator(0.1))
ax_TPM.yaxis.set_major_locator(MultipleLocator(0.1))
ax_sig.yaxis.set_major_locator(MultipleLocator(0.5))

ax_FEM.xaxis.set_major_locator(MultipleLocator(0.1))
ax_FPM.xaxis.set_major_locator(MultipleLocator(0.1))

ax_EMPM.xaxis.set_major_formatter(NullFormatter())
ax_EMPM.yaxis.set_major_formatter(NullFormatter())
ax_EMPM.yaxis.set_major_locator(NullLocator())
ax_EMPM.xaxis.set_major_locator(NullLocator())


################################################################################
# Plot S1 and S1a and TFEM + TFPM misfits
fig = plt.figure()

# plot signals
ax_sig = fig.add_axes([left + w_1, bottom + h_2 + h_3, w_2, h_1])
ax_sig.plot(t, S1(t), 'k')
ax_sig.plot(t, S1a(t), 'r')

# plot TEM
TEM_11p = TEM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TEM = fig.add_axes([left + w_1, bottom + h_1 + h_2 + h_3, w_2, h_2])
ax_TEM.plot(t, TEM_11p)
ax_TEM.set_ylim(-ylims, ylims)

# plot TFEM
TFEM_11p = TFEM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TFEM = fig.add_axes([left + w_1, bottom + h_1 + 2*h_2 + h_3, w_2, h_3])
ax_TFEM.imshow(TFEM_11p, interpolation='nearest', cmap=cm, extent=[t[0], t[-1],
               f[0], f[-1]], aspect='auto', vmin=-clims, vmax=clims,
               origin='lower')
ax_TFEM.set_yscale('log')

# plot FEM
FEM_11p = FEM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_FEM = fig.add_axes([left, bottom + h_1 + 2*h_2 + h_3, w_1, h_3])
ax_FEM.semilogy(FEM_11p, f)
ax_FEM.set_xlim(-ylims, ylims)
ax_FEM.set_ylim(fmin, fmax)

# plot TPM
TPM_11p = TPM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TPM = fig.add_axes([left + w_1, bottom, w_2, h_2])
ax_TPM.plot(t, TPM_11p)
ax_TPM.set_ylim(-ylims, ylims)

# plot TFPM
TFPM_11p = TFPM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_TFPM = fig.add_axes([left + w_1, bottom + h_2, w_2, h_3])
img = ax_TFPM.imshow(TFPM_11p, interpolation='nearest', cmap=cm, extent=[t[0],
                     t[-1], f[0], f[-1]], aspect='auto', vmin=-clims,
                     vmax=clims, origin='lower') 
ax_TFPM.set_yscale('log')

# add colorbar
ax_cb = fig.add_axes([left + w_1 + w_2 + d_cb + w_cb, bottom, w_cb, h_2 + h_3])
fig.colorbar(img, cax=ax_cb)

# plot FPM
FPM_11p = FPM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_FPM = fig.add_axes([left, bottom + h_2, w_1, h_3])
ax_FPM.semilogy(FPM_11p, f)
ax_FPM.set_xlim(-ylims, ylims)
ax_FPM.set_ylim(fmin, fmax)

# add text box for EM + PM
PM_11p = PM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
EM_11p = EM(S1(t), S1a(t), dt=dt, fmin=fmin, fmax=fmax, nf=nf)
ax_EMPM = fig.add_axes([left, bottom + h_2 + h_3 + h_1 / 2., w_1 * .7, (h_1 +
                        h_2) / 3.])
textstr = 'EM = %.2f\nPM = %.2f' % (EM_11p, PM_11p)
ax_EMPM.text(0.05, 0.1, textstr)

ax_TPM.set_xlabel('time / seconds')
ax_FEM.set_ylabel('f / Hz')
ax_FPM.set_ylabel('f / Hz')

ax_TFEM.set_title('TFEM', x=0.9, y=0.75)
ax_TFPM.set_title('TFPM', x=0.9, y=0.75)
ax_TEM.set_title('TEM', x=0.9, y=0.65)
ax_TPM.set_title('TPM', x=0.9, y=0.65)

ax_FEM.set_title('FEM', x=0.8, y=0.75)
ax_FPM.set_title('FPM', x=0.8, y=0.75)

ax_TFPM.xaxis.set_major_formatter(NullFormatter())
ax_TFEM.xaxis.set_major_formatter(NullFormatter())
ax_TEM.xaxis.set_major_formatter(NullFormatter())
ax_sig.xaxis.set_major_formatter(NullFormatter())

ax_TFPM.yaxis.set_major_formatter(NullFormatter())
ax_TFEM.yaxis.set_major_formatter(NullFormatter())

ax_TEM.yaxis.set_major_locator(MultipleLocator(0.1))
ax_TPM.yaxis.set_major_locator(MultipleLocator(0.1))
ax_sig.yaxis.set_major_locator(MultipleLocator(0.5))

ax_FEM.xaxis.set_major_locator(MultipleLocator(0.1))
ax_FPM.xaxis.set_major_locator(MultipleLocator(0.1))

ax_EMPM.xaxis.set_major_formatter(NullFormatter())
ax_EMPM.yaxis.set_major_formatter(NullFormatter())
ax_EMPM.yaxis.set_major_locator(NullLocator())
ax_EMPM.xaxis.set_major_locator(NullLocator())


plt.show()
