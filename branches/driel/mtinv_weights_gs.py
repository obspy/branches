#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal import util
from obspy.core import read, Trace, Stream
from obspy.signal import highpass, lowpass, cosTaper
import pickle
import os.path
from scipy.integrate import cumtrapz
from obspy.signal.invsim import waterlevel

def mtinv(input_set, st_tr, st_g, fmin, fmax, nsv=1, single_force=False,
          stat_subset=[], weighting_type=2, weights=[], cache_path='',
          force_recalc=False, cache=True):
    '''
    Not intended for direct use, use mtinv_gs instead!
    '''
    utrw, weights_l2, S0w, df, dt, nstat, ndat, ng, nfft, nfinv = input_set

    # setup greens matrix in fourier space
    if os.path.isfile(cache_path + 'gw.pickle') and not force_recalc:
        # read G-matrix from file if exists
        gw = pickle.load(open(cache_path + 'gw.pickle'))
        if gw.shape[-1] < nfinv:
            force_recalc = True
        else:
            gw = gw[:,:,:nfinv]

    if not os.path.isfile(cache_path + 'gw.pickle') or force_recalc:
        g = np.zeros((nstat * 3, 6 + single_force * 3, ng))
        #gw = np.zeros((nstat * 3, 6 + single_force * 3, nfft/2+1)) * 0j
        gw = np.zeros((nstat * 3, 6 + single_force * 3, nfinv)) * 0j

        for k in np.arange(nstat):
            for i in np.arange(3):
                for j in np.arange(6 + single_force * 3):
                    g[k*3 + i,j,:] = st_g.select(station='%04d' % (k + 1),
                                     channel='%02d%1d' % (i,j))[0].data
                    # fill greens matrix in freq space, deconvolve S0
                    gw[k*3 + i,j,:] = np.fft.rfft(g[k*3 + i,j,:], n=nfft) \
                                                    [:nfinv] * dt / S0w
                    

        # write G-matrix to file
        if cache:
            pickle.dump(gw, open(cache_path + 'gw.pickle', 'w'), protocol=2)

    # setup channel subset from station subset
    if stat_subset == []:
        stat_subset = np.arange(nstat)
    else:
        stat_subset = np.array(stat_subset) - 1

    chan_subset = np.zeros(stat_subset.size*3, dtype=int)
    for i in np.arange(stat_subset.size):
        chan_subset[i*3:(i+1)*3] = stat_subset[i]*3 + np.array([0,1,2])

    # setup weighting matrix (depending on weighting scheme and apriori
    # weighting)
    
    # a priori weighting   
    if weights == []:
        weights = np.ones(nstat)
    elif len(weights) == stat_subset.size:
        weights = np.array(weights)
        buf = np.ones(nstat)
        buf[stat_subset] = weights
        weights = buf
    elif len(weights) == nstat:
        weights = np.array(weights)
    else:
        raise ValueError('argument weights has wrong length')
    
    chan_weights = np.zeros(nstat*3)
    for i in np.arange(nstat):
        chan_weights[i*3:(i+1)*3] = weights[i] + np.zeros(3)

    # l2-norm weighting
    if weighting_type == 0:
        weights_l2 *= chan_weights
        weights_l2 = np.ones(nstat*3) * (weights_l2[chan_subset].sum())**.5
    elif weighting_type == 1:
        weights_l2 = weights_l2**.5
    elif weighting_type == 2:
        for k in np.arange(nstat):
            weights_l2[k*3:k*3 + 3] = (weights_l2[k*3:k*3 + 3].sum())**.5
    else:
        raise ValueError('argument weighting_type needs to be in [0,1,2]')
   
    weights_l2 = 1./weights_l2
    weightsm = np.matrix(np.diag(weights_l2[chan_subset] *
                         chan_weights[chan_subset]**.5))
    
    M = np.zeros((6 + single_force * 3, nfft/2+1)) * 0j
    
    # inversion
    for w in np.arange(nfinv):
        G = weightsm * np.matrix(gw[[chan_subset],:,w])
        GI = np.linalg.pinv(G, rcond=0.00001)
        m = GI * weightsm * np.matrix(utrw[[chan_subset],w]).T
        M[:,w] = np.array(m.flatten())

    # back to time domain

    M_t = np.zeros((6 + single_force * 3, nfft))

    for j in np.arange(6 + single_force * 3):
        M_t[j,:] = np.fft.irfft(M[j,:])[:nfft] * df
    
    M_t = lowpass(M_t, fmax, df, corners=4)

    # use principal component analysis for constrained inversion
    U, s, V = np.linalg.svd(M_t, full_matrices=False)
    m = []
    x = []
    for k in np.arange(6 + single_force * 3):
        m.append(np.matrix(U[:,k]).T)
        x.append(np.matrix(V[k] * s[k]))
    argm = np.abs(m[0]).argmax()
    sig = np.sign(m[0][argm,0])
    M_t = np.array(np.zeros((M_t.shape)))
    for k in np.arange(6 + single_force * 3):
        m[k] *= sig
        x[k] *= sig
    for k in np.arange(nsv):
        M_t += np.array(m[k] * x[k])

    # compute synthetic seismograms (for stations included in the inversion
    # only - maybe it makes sense to do it for all so that indizes in the
    # streams are the same in input and ouput)

    channels = ['u', 'v', 'w']

    stf = M_t
    traces = []
    stff = np.fft.rfft(stf, n=nfft) * dt

    for k in stat_subset:
        for i in np.arange(3):
            
            data = np.zeros(ndat)
            for j in np.arange(6 + single_force * 3):
                dummy = np.concatenate((gw[k*3 + i,j,:], np.zeros(nfft/2 + 1 -
                                        nfinv))) * stff[j]
                dummy = np.fft.irfft(dummy)[:ndat] / dt
                data += dummy

            stats = {'network': 'SY', 
                     'station': '%04d' % (k+1), 
                     'location': '',
                     'channel': channels[i],
                     'npts': len(data), 
                     'sampling_rate': st_tr[0].stats.sampling_rate,
                     'starttime': st_tr[0].stats.starttime,
                     'mseed' : {'dataquality': 'D'}}
            traces.append(Trace(data=data, header=stats))

    st_syn = Stream(traces)
    
    # compute misfit
    misfit = 0.

    for k in stat_subset:
        for i, chan in enumerate(['u', 'v', 'w']):
            u = st_tr.select(station='%04d' % (k+1), channel=chan)[0].data.copy()
            Gm = st_syn.select(station='%04d' % (k+1), channel=chan)[0].data.copy()
            misfit += weights_l2[k*3 + i]**2 * chan_weights[k*3 + i] * \
                      cumtrapz((u - Gm)**2, dx=dt)[-1]

    if weighting_type == 1:
        misfit /= chan_weights[chan_subset].sum()
    elif weighting_type == 2:
        misfit /= weights[stat_subset].sum()

    return M_t, np.array(m), np.array(x), s, st_syn, misfit





def mtinv_gs(st_tr, gl, fmin, fmax, fmax_hardcut_factor=4, S0=None, nsv=1,
          single_force=False, stat_subset=[], weighting_type=2, weights=[],
          cache_path='', force_recalc=False, cache=False, w_level=50):
    '''
    Frequency domain moment tensor inversion.

    Features:
     - grid search for best source location
     - direct inversion for different error measures (see weighting type)
     - constrain to limited number of source mechanisms/time dependencies using
       principal component analysis
     - deconvolution of source time function used for Green's function
       simulations
     - caching the Green's matrix in Frequency space for speed up of repeated
       evaluation

    Theory see Diplomathesis 'The Effect of Tilt on Moment Tensor Inversion in
    the Nearfield of Active Volcanoes' section 2.2

    :type st_tr: :class:`~obspy.core.stream.Stream`
    :param st_tr: Stream containing the seismograms, station names are numbers
        starting with 0001, channels are ['u', 'v', 'w']
    :type gl: list of :class:`~obspy.core.stream.Stream` objects or list
    :param gl: list of Streams containing the green's functions, station names
        are numbers starting with 0001, channels are of format '%02d%1d' where
        the first number is the component of the receiver ([0,1,2]) and the
        second the source ([0,1,...,5] or [0,1,...,8] including single forces).
        Should have the same sample rate as st_tr. If no grid search is needed,
        just put a single stream in the list.
        In case of a high number of stations (>250), gl can be a list of 
        strings containing the path to and names of the greens functions files
    :type fmin: float
    :param fmin: high pass frequency
    :type fmax: float
    :param fmax: low pass frequency
    :type fmax_hardcut_factor: int
    :param fmax_hardcut_factor: multiple of fmax where the inversion is stopped
    :type S0: :class:`numpy.ndarray`
    :param S0: source time function used for computation of the Green's
        function to deconvolve. Is assumed to have same sample rate as st_tr.
        If S0 is None, no deconvolution is performed.
    :type nsv: int
    :param nsv: number of mechanisms corresponding to the largest singular
        values in the constrained inversion
    :type single_force: Bool
    :param single_force: include single force in the inversion (then green's
        functions for single forces are needed in channels ([6,7,8]))
    :type stat_subset: List
    :param stat_subset: List of stations to use in the inversion
    :type weighting: int
    :param weighting_type: should be one of [0,1,2], 0: no weighting, 1: use l2
        norm weighting for each trace, 2: use l2 norm weighting for each
        station (weight is sum of the weights of the traces)
    :type weights: listtype
    :param weights: a priori relative weighting of stations, should have length
        nstat or same length as stat_subset
    :type cache_path: string
    :param cache_path: path to a folder to cache Green's matrix
    :type force_recalc: Bool
    :param force_recalc: force reevalution of fourier transform of
        Green's functions (if cached in 'cache_path' to speed up inversion).
    :type cache: Bool
    :param cache: cache in a file or not
    :type w_level: int
    :param w_level: value of waterlevel in dB under max amplitude in spectrum
        of deconvolved Green's function

    returns a tuple containing:
        M_t     - time dependent Momenttensor solution (if nsv > 1 than summed
                  up mechanisms)
        m       - time independent Momenttensor (nsv arrays)
        x       - time dependence of principal component solutions in m
        s       - singular values of principal components
        st_syn  - synthetic seismograms generated with the inverted source
        st_tr   - input seismograms filtered the same way as the synthetics
                  (for comparison to synthetic seismograms)
        misfit  - misfit of synthetics, definition depends on weighting
                  (is only mathematically strict minimized for nsv=6  (9 in
                  case of single force), otherwise approximately)
        argmin  - index of Green's function in list that minimizes the misfit
    '''
    st_tr = st_tr.copy()
    st_tr.filter('lowpass', freq=fmax, corners=4)
    st_tr.filter('highpass', freq=fmin, corners=4)

    # test if gl is a list or a stream
    if type(gl[0]) == str:
        st_g = read('%s'%(gl[0]))
    else:
        st_g = gl[0]

    ng = st_g[0].data.size

    df = st_tr[0].stats.sampling_rate
    dt = 1./df

    nstat = st_tr.select(channel='u').count()
    ndat = st_tr[0].data.size
    nfft = util.nextpow2(max(ndat, ng) * 2)

    # use freuquncies below corner frequency * fmax_hardcut_factor (tremendous
    # speed up in inversion)
    nfinv = int(fmax_hardcut_factor * fmax / (df / 2.) * nfft)
    nfinv = min(nfft/2+1, nfinv)

    # going to frequency domain

    # correction for stf used in green's forward simulation
    if S0 is None:
        S0w = 1.
    else:
        S0w = np.fft.rfft(S0, n=nfft)[:nfinv] * dt

        # introduce waterlevel to prevent instabilities in deconvolution of
        # greens functions, see obspy.signal.invsim specInv

        # Calculated waterlevel in the scale of spec
        swamp = waterlevel(S0w, w_level)
        # Find length in real fft frequency domain, spec is complex
        sqrt_len = np.abs(S0w)
        # Set/scale length to swamp, but leave phase untouched
        # 0 sqrt_len will transform in np.nans when dividing by it
        idx = np.where((sqrt_len < swamp) & (sqrt_len > 0.0))
        S0w[idx] *= swamp / sqrt_len[idx]


    # setup seismogram matrix in fourier space
    utr = np.zeros((nstat * 3, ndat))
    utrw = np.zeros((nstat * 3, nfft/2+1)) * 0j
    weights_l2 = np.zeros(nstat * 3)

    for k in np.arange(nstat):
        for i, chan in enumerate(['u', 'v', 'w']):
            utr[k*3 + i,:] = st_tr.select(station='%04d' % (k+1), channel=chan)[0].data
            utrw[k*3 + i,:] = np.fft.rfft(utr[k*3 + i,:], n=nfft) * dt
            # calculate l2 norm for weighting
            weights_l2[k*3 + i] = cumtrapz(utr[k*3 + i,:]**2, dx=dt)[-1]
    
    M_tl = []
    ml = []
    xl = []
    sl = []
    st_synl = []
    misfitl = []

    st_tr.filter('lowpass', freq=fmax, corners=4)

    for i, stg in enumerate(gl):
        if type(stg) == str:
            st_g = read('%s'%(stg))
        else:
            st_g = stg
        print i

        if round(st_tr[0].stats.sampling_rate, 5) != round(st_g[0].stats.sampling_rate, 5):
            msg = 'sampling rates of Seismograms and Green\'s function are not the'
            msg = msg + ' same: %f != %f' % (st_tr[0].stats.sampling_rate,
                                             st_g[0].stats.sampling_rate)
            raise ValueError(msg)

        M_t, m, x, s, st_syn, misfit = mtinv((utrw, weights_l2.copy(), S0w, df,
            dt, nstat, ndat, ng, nfft, nfinv), st_tr, st_g, fmin, fmax,
            nsv=nsv, single_force=single_force, stat_subset=stat_subset,
            force_recalc=force_recalc, weighting_type=weighting_type,
            weights=weights, cache_path=cache_path + ('%06d_' % i), cache=cache)

        M_tl.append(M_t)
        ml.append(m)
        xl.append(x)
        sl.append(s)
        st_synl.append(st_syn)
        misfitl.append(misfit)

    misfit = np.array(misfitl)
    argmin = misfit.argmin()
    

    return M_tl[argmin], ml[argmin], xl[argmin], sl[argmin], st_synl[argmin], st_tr, misfit, argmin
    




def generate_constrained_sources(mt_eigenvalues, euler_angles=[(-np.pi,
        np.pi),(-0.5*np.pi, 0.5*np.pi),(-np.pi, np.pi)], angle_steps=[10,10,10],
        rotation_mode='extrinsic'):
    '''
    For a Moment Tensor given as Eigenvalues, compute all rotations for the angle limits in euler_angles.
    
    :param mt_eigenvalues: 3x1 list type containing the eigenvalues of the MT to rotate
    :param euler_angles: angle range to parameterize (depends on the symmetries
        of the MT) list of 3 tuples with two entries each
    :param angle_steps: list of 3 integers, number of interpolation points in the euler angle range
    :param rotation_mode: 'intrinsic' or 'extrinsic', see http://en.wikipedia.org/wiki/Euler_angles
    '''

    # set up angle search grid
    angle_grid = np.empty((angle_steps[0], angle_steps[1], angle_steps[2], 3))
    print angle_grid.shape
    
    # set up constraines sources by rotating the mt defined by mt_eigenvalues
    # by angles in the grid
    constrained_sources = np.zeros((angle_steps[0], angle_steps[1], angle_steps[2], 6))
    
    for k in np.arange(angle_steps[0]):
        for l in np.arange(angle_steps[1]):
            for m in np.arange(angle_steps[2]):

                phi = k  / float(angle_steps[0] - 1) \
                    * (euler_angles[0][1] -  euler_angles[0][0]) \
                    + euler_angles[0][0]
            
                theta = l  / float(angle_steps[1] - 1) \
                      * (euler_angles[1][1] -  euler_angles[1][0]) \
                      + euler_angles[1][0]

                psi = m  / float(angle_steps[2] - 1) \
                      * (euler_angles[2][1] -  euler_angles[2][0]) \
                      + euler_angles[2][0]
           
                angle_grid[k,l,m,:] = (phi, theta, psi)

        
                # Define the 3D rotation matrix with Euler angles phi, theta and psi

                R1 = np.matrix(np.zeros((3,3)))

                R1[2,2] = 1.
                R1[0,0] =  np.cos(phi)
                R1[1,1] =  np.cos(phi)
                R1[0,1] = -np.sin(phi)
                R1[1,0] =  np.sin(phi)

                R2 = np.matrix(np.zeros((3,3)))

                R2[0,0] = 1.
                R2[1,1] =  np.cos(theta)
                R2[2,2] =  np.cos(theta)
                R2[1,2] = -np.sin(theta)
                R2[2,1] =  np.sin(theta)
                
                R3 = np.matrix(np.zeros((3,3)))

                R3[2,2] = 1.
                R3[0,0] =  np.cos(psi)
                R3[1,1] =  np.cos(psi)
                R3[0,1] = -np.sin(psi)
                R3[1,0] =  np.sin(psi)

                m_const = np.matrix(np.diag(mt_eigenvalues))
                
                if rotation_mode == 'extrinsic':
                    m_const = R3 * R2 * R1 * m_const * R1.T * R2.T * R3.T
                elif rotation_mode == 'intrinsic':
                    m_const = R1 * R2 * R3 * m_const * R3.T * R2.T * R1.T

                constrained_sources[k,l,m,0] = m_const[0,0]
                constrained_sources[k,l,m,1] = m_const[1,1]
                constrained_sources[k,l,m,2] = m_const[2,2]
                constrained_sources[k,l,m,3] = m_const[0,1]
                constrained_sources[k,l,m,4] = m_const[0,2]
                constrained_sources[k,l,m,5] = m_const[1,2]
    
    return (constrained_sources, angle_grid)
