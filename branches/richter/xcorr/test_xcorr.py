#!/usr/bin/python

import numpy as np
import unittest
import xcorr
import scipy.signal

class UtilTestCase(unittest.TestCase):

    def test_xcorr_obspy(self):
        N=1001
        data1 = np.sin(np.arange(N)/100.)
        data2 = np.e**(-(np.arange(N)-500)**2/100.) - np.e**(-(np.arange(N)-50)**2/100.) + 5*np.e**(-(np.arange(N)-950)**2/100.)
        data1[:] = data1[:]- np.mean(data1)
        data2[:]= data2[:]-np.mean(data2)
        cor1 =  scipy.signal.correlate(data1, data2, 'same')
        cor2 = xcorr.xcorr_obspy(data1, data2, N//2, 1)
        cor3 = xcorr.xcorr_obspy(data1, data1, N, 2)
        cor1 *= max(cor2)/max(cor1)
#        from pylab import plot, show, subplot
#        subplot(211)
#        plot(data1)
#        plot(data2)
#        subplot(212)
#        plot(cor1)
#        plot(cor2)
#        plot(cor3)
#        show()
        np.testing.assert_array_almost_equal(cor1, cor2, 1)

    def test_xcorr(self):
        N=1001
        data1 = np.sin(np.arange(N//2+1)/100.)
        data2 = np.e**(-(np.arange(N)-500)**2/100.) - np.e**(-(np.arange(N)-50)**2/100.) + 5*np.e**(-(np.arange(N)-950)**2/100.)
        cor1 =  scipy.signal.correlate(data1 - np.mean(data1), data2-np.mean(data2), 'full')
        cor2 = xcorr.xcorr(data1, data2, 750, padding=0)
        cor3 = xcorr.xcorr(data1, data2, 750, padding=1)
        cor1 *= max(cor2)/max(cor1)

        cor4 =  scipy.signal.correlate(data2-np.mean(data2), data1 - np.mean(data1), 'full')
        cor5 = xcorr.xcorr(data2, data1, 750, padding=0)
        cor6 = xcorr.xcorr(data2, data1, 750, padding=1)
        cor5b = xcorr.xcorr(data2, data1, 750, shift_zero=-100, padding=0)
        cor5c = xcorr.xcorr(data2, data1, 750, shift_zero=100, padding=0)
        cor4 *= max(cor5)/max(cor4)

        cor7 = scipy.signal.correlate(data1, data2, 'full')
        cor8 = xcorr.xcorr(data1, data2, 750, padding=0, demean=0)
        cor7 *= max(cor8)/max(cor7)

        cor9 = xcorr.xcorr(data1, data2, 750, shift_zero=100, padding=0, demean=0)
        cor10 = xcorr.xcorr(data1, data2, 750, shift_zero=100, twosided=False, padding=0, demean=0)

#        from pylab import plot, show, subplot, legend
#        subplot(411)
#        plot(data1)
#        plot(data2)
#        subplot(412)
#        plot(cor1, label='scipy.signal demeaned')
#        plot(cor2, label='xcorr.xcorr')
#        plot(cor3, label='xcorr.xcorr padded to same length')
#        legend()
#        subplot(413)
#        plot(cor4, label='scipy.signal demeaned')
#        plot(cor5, label='xcorr.xcorr')
#        plot(cor5b, label='xcorr.xcorr shifted -100')
#        plot(cor5c, label='xcorr.xcorr shifted 100')
#        plot(cor6, label='xcorr.xcorr padded to same length')
#        legend()
#        subplot(414)
#        plot(cor7, label='scipy.signal')
#        plot(cor8, label='xcorr.xcorr not demeaned')
#        plot(cor9, label='xcorr.xcorr shifted 100')
#        plot(cor10, label='xcorr.xcorr shifted 100 twosided=False')
#        legend()
#        show()
        np.testing.assert_array_almost_equal(cor1, cor2)
        np.testing.assert_array_almost_equal(cor4, cor5)
        np.testing.assert_array_almost_equal(cor7, cor8)
        np.testing.assert_array_almost_equal(cor5[200:300], cor5b[100:200])
        np.testing.assert_array_almost_equal(cor5[200:300], cor5c[300:400])

    def test_acorr(self):
        data1 = np.sin(np.arange(1001)*2*np.pi/500.)
        data2 = np.sin(np.arange(1001)*2*np.pi/500.)
        data2[:100]=0
        data2[-100:]=0
        cor1 = xcorr.xcorr(data1, data1, 1000, padding=1)
        cor2 = xcorr.acorr(data1, 1000, twosided=True, padding=1)
        cor3 = xcorr.acorr(data1, 1000, twosided=True, padding=1000)
        cor4 = xcorr.acorr(data1, 1000, shift_zero=-100, twosided=False, padding=1)
        cor5 = xcorr.acorr(data1, 1000, shift_zero=100, twosided=False, padding=1)

#        from pylab import plot, show, subplot, legend
#        subplot(211)
#        plot(data1)
#        subplot(212)
#        plot(cor1, label='xcorr.xcorr')
#        plot(cor2, label='xcorr.acorr')
#        plot(cor3, label='xcorr.acorr padding=1000')
#        plot(cor4, label='xcorr.acorr shifted -100 twosided=False')
#        plot(cor5, label='xcorr.acorr shifted 100 twosided=False')
#        legend()
#        show()
        np.testing.assert_array_almost_equal(cor1, cor2)
        np.testing.assert_array_almost_equal(cor1, cor3)

def suite():
    return unittest.makeSuite(UtilTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
