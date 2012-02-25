import numpy as np
from obspy.signal import util, cosTaper

# Kristekova et. al. (2006) refers to:
#
# M. Kristekova, J. Kristek, P. Moczo, and S. M. Day,
# Misfit Criteria for Quantitative Comparison of Seismograms
# Bulletin of the Seismological Society of America, Vol. 96, No. 5,
# pp. 1836-1850, October 2006, doi: 10.1785/0120060012


def cwt(st, t, w0, f, wl='morlet'):
    '''
    Continuous Wavelet Transformation in the Frequency Domain. Compare to
    Kristekova et. al. (2006) eq. (4)
    st: time dependent signal. Will be demeaned and tapered before FFT
    t: time discretization
    w0: parameter for the wavelet
    f: frequency discretization
    wl: wavelet to use, for now only 'morlet' is implemented
    '''
    cwt = np.zeros((t.shape[0], f.shape[0])) * 0j

    if wl == 'morlet':
        psi = lambda t : np.pi**(-.25) * np.exp(1j * w0 * t) * np.exp(-t**2 / 2.)
        scale = lambda f : w0 / (2 * np.pi * f)
    else:
        raise ValueError('wavelet type "' + wl + '" not defined!')

    st -= st.mean()
    st *= cosTaper(len(st), p=0.05)
    nfft = util.nextpow2(len(st)) * 2
    sf = np.fft.fft(st, n=nfft)

    for n, _f in enumerate(f):
        a = scale(_f)
        # time shift necesarry, because wavelet is defined around t = 0
        psih = psi(-1*(t - t[-1]/2.)/a).conjugate() / np.abs(a)**.5
        psihf = np.fft.fft(psih, n=nfft)
        tminin = int(t[-1]/2. / (t[1] - t[0]))
        cwt[:,n] = np.fft.ifft(psihf * sf)[tminin:tminin+t.shape[0]] * (t[1] - t[0])

    return cwt.T



def TFEM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Time Frequency Envelope Misfit, see Kristekova et. al. (2006) eq. (9)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logaritmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    return (np.abs(W2) - np.abs(W1)) / np.max(np.abs(W1))



def TFPM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Time Frequency Phase Misfit, see Kristekova et. al. (2006) eq. (10)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    TFPMl = np.angle(W2) - np.angle(W1)
    TFPMl[TFPMl > np.pi] -= 2*np.pi
    TFPMl[TFPMl < -np.pi] += 2*np.pi

    return np.abs(W1) * TFPMl / np.pi / np.max(np.abs(W1))



def TEM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Time-dependent Envelope Misfit, see Kristekova et. al. (2006) eq. (11)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    TEMl = np.sum((np.abs(W2) - np.abs(W1)), axis=0) / nf
    TEMl /=  np.max(np.sum(np.abs(W1), axis=0))  / nf
   
    return TEMl



def TPM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Time-dependent Phase Misfit, see Kristekova et. al. (2006) eq. (12)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    TPMl = np.angle(W2) - np.angle(W1)
    TPMl[TPMl > np.pi] -= 2*np.pi
    TPMl[TPMl < -np.pi] += 2*np.pi

    TPMl = np.abs(W1) * TPMl / np.pi

    TPMl = np.sum(TPMl, axis=0) / nf
    TPMl /= np.max(np.sum(np.abs(W1), axis=0)) / nf

    return TPMl



def FEM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Frequency-dependent Envelope Misfit, see Kristekova et. al. (2006) eq. (11)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    TEMl = np.sum((np.abs(W2) - np.abs(W1)), axis=1) / npts
    TEMl /=  np.max(np.sum(np.abs(W1), axis=1))  / npts
   
    return TEMl



def FPM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Frequency-dependent Phase Misfit, see Kristekova et. al. (2006) eq. (12)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    TPMl = np.angle(W2) - np.angle(W1)
    TPMl[TPMl > np.pi] -= 2*np.pi
    TPMl[TPMl < -np.pi] += 2*np.pi

    TPMl = np.abs(W1) * TPMl / np.pi

    TPMl = np.sum(TPMl, axis=1) / npts
    TPMl /= np.max(np.sum(np.abs(W1), axis=1)) / npts

    return TPMl



def EM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Single Valued Envelope Misfit, see Kristekova et. al. (2006) eq. (12)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    EMl = (np.sum((np.abs(W2) - np.abs(W1))**2))**.5
    EMl /=  (np.sum(np.abs(W1)**2))**.5
   
    return EMl



def PM(st1, st2, dt=1., fmin=1., fmax=10., nf=100, w0=6, wl='morlet'):
    '''
    Single Valued Phase Misfit, see Kristekova et. al. (2006) eq. (12)
    st1, st2: two signals to compare, will be demeaned and tapered before FFT in CWT
    dt: time step
    fmin, fmax: minimal and maximal frequency to be analyzed
    nf: number of frequencies (will be chosen with logarithmic spacing)
    w0: parameter for the wavelet
    wl: wavelet to use in continuous wavelet transform
    '''
    f = np.logspace(np.log10(fmin), np.log10(fmax), nf)
    npts = len(st1)
    tmax = (npts - 1) * dt
    t = np.linspace(0., tmax, npts)

    W1 = cwt(st1, t, w0, f)
    W2 = cwt(st2, t, w0, f)

    PMl = np.angle(W2) - np.angle(W1)
    PMl[PMl > np.pi] -= 2 * np.pi
    PMl[PMl < -np.pi] += 2 * np.pi

    PMl = np.abs(W1) * PMl / np.pi

    PMl = (np.sum(PMl**2))**.5
    PMl /= (np.sum(np.abs(W1)**2))**.5

    return PMl


