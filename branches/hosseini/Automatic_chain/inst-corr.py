# ------------------------Import required Modules (Python and Obspy)-------------

"""
Required Python and Obspy modules will be imported in this part.
"""

from obspy.core import read, UTCDateTime
from obspy.signal import seisSim, invsim
from obspy.iris import Client
import numpy as np
import scipy
import cmath
from obspy.taup import taup
import os
import shutil

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def DMT_inst():
	
	t1_pro = datetime.now()

###################################################### inst_IRIS ######################################################

def IRIS(input):
	
	"""
	Call "inst_IRIS" function based on your channel request.
	"""

	if input['BHE'] == 'Y':
		inst_IRIS(input, channel = 'BHE', interactive = input['inter_address'])
	
	if input['BHN'] == 'Y':
		inst_IRIS(input, channel = 'BHN', interactive = input['inter_address'])
	
	if input['BHZ'] == 'Y':
		inst_IRIS(input, channel = 'BHZ', interactive = input['inter_address'])

	print "-------------------------------------------------"
	print 'IRIS Instrument Correction is DONE'
	print "-------------------------------------------------"
	
###################################################### update_req_sta_IRIS ######################################################
	
def inst_IRIS(input, channel, interactive = 'N'):
	
	"""
	
	"""
	
	t_inst_1 = datetime.now()
	
	if interactive == 'N':
		Period = input['min_date'] + '_' + input['max_date'] + '_' + str(input['min_mag']) + '_' + str(input['max_mag'])
		Address_events = input['Address'] + '/' + Period
	else:
		address_inter = get_address()
		Address_events = address_inter

	
	Event_file = open(Address_events + '/EVENT/event_list', 'r')
	events = pickle.load(Event_file)
	
	len_events = len(events)
	
	input_file = []
	
	for l in range(0, len_events):
		
		input_file[l].append(open(Address_events + '/' + events[l]['event_id'] + '/IRIS/info/iris_' + channel))
		
		try:
			os.makedirs(Address_events + '/' + events[l]['event_id'] + '/IRIS/BH')
			
		except Exception, e:
			print e
			print "This folder:"
			print Address_events + '/' + events[l]['event_id'] + '/IRIS/BH'
			print "exists in your directory...The program will continue in the same folder!"
		
		input_sta = input_file[l].readlines()
		
		for i in range(0, len(input_sta)):
			input_sta[i] = input_sta[i].split(',')
		
		BH_raw_file = []
		resp_file = []

		for i in range(0, len(input_sta)):
			if input_sta[i][2] == '  ':
				input_sta[i][2] = '--'
			BH_raw_file.append(address + 'IRIS/BH_RAW/' + input_sta[i][0] + '.' + input_sta[i][1] + '.' + input_sta[i][2] + '.' + input_sta[i][3]) 
		
		for k in range(0, len(BH_raw_file)):
			
			print '********************************************'
			print k + '/' + len(BH_raw_file)
			rt_c = RTR(stream = BH_raw_file[k], , degree = 2)
			print '********************************************'
			
			tr = BH_raw_file[k][0]
			tr.data = rt_c
			
			# Tapering
			taper = invsim.cosTaper(len(tr.data))
			tr.data *= taper
						
			if tr.stats['location'] == '':
				location = '--'
				resp_file = address + 'IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel']
			else:
				resp_file = address + 'IRIS/Resp/RESP.' + \
					tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
			
			print '--------------------------------------'
			print 'Response file:'
			print resp_file
			print '--------------------------------------'
			
			inst_corr(trace = tr, resp_file = resp_file, unit = input['corr_unit'], BP_filter = input['pre_filt']):
	
	t_inst_2 = datetime.now()
	
	print '*********************************************************************'
	print 'Time passed for Instrument Correction of ' + channel + ' :'
	print t_inst_2 - t_inst_1
	print '*********************************************************************'

###################################################### RTR ######################################################

def RTR(stream, degree = 2):
	
	raw_f = read(stream)

	t = []
	b0 = 0
	inc = []
	
	b = raw_f[0].stats['starttime']

	for i in range(0, raw_f[0].stats['npts']):
		inc.append(b0)
		b0 = b0+1.0/raw_f[0].stats['sampling_rate'] 
		b0 = round(b0, 4)
		
	A = np.vander(inc, degree)
	(coeffs, residuals, rank, sing_vals) = np.linalg.lstsq(A, raw_f[0].data)
	
	print '--------------------'
	print 'coeffs = ' + str(coeffs)
	print 'residuals = ' + str(residuals)
	print 'rank = ' + str(rank)
	print 'sing_vals = ' + str(sing_vals)
	print '--------------------'
	
	f = np.poly1d(coeffs)
	y_est = f(inc)
	rt_c = raw_f[0].data-y_est
	
	return rt_c

###################################################### inst_corr ######################################################

def inst_corr(trace, resp_file, unit = 'DIS', BP_filter = (0.008, 0.012, 3.0, 4.0)):

	date = trace.stats['starttime']
	seedresp = {'filename':resp_file,'date':date,'units':unit}
	
	try:
			
		trace.data = seisSim(data = trace.data,samp_rate = trace.stats.sampling_rate,paz_remove=None, \
			paz_simulate = None, remove_sensitivity=False, simulate_sensitivity = False, water_level = 600.0, \
			zero_mean = True, taper = False, pre_filt=BP_filter, seedresp=seedresp)
		
		if trace.stats['location'] == '':
			location = '--'
			trace.write(address + 'IRIS/BH/' + \
				trace.stats['network'] + '.' + trace.stats['station'] + '.' + trace.stats['location'] + \
				'.' + trace.stats['channel'], format = 'SAC')
				
		else:
			trace.write(address + 'IRIS/BH/' + \
				trace.stats['network'] + '.' + trace.stats['station'] + '.' + trace.stats['location'] + \
				'.' + trace.stats['channel'], format = 'SAC')
		
	except Exception, e:
		print e

#########################################################################################################################
#########################################################################################################################
#########################################################################################################################

if __name__ == "__main__":
	status = DMT_inst()
	sys.exit(status)



'''
	#plt.plot(range(0, len(trace.data)), trace.data*1e9)
	#plt.plot(range(0, len(sac[0].data)), sac[0])
	#plt.plot(range(0, len(sac[0].data)), sac[0]-trace.data*1e9)
	
	#plt.plot(t_inc, trace.data*1e6+delta, color = 'black')
	#plt.plot(t_inc, aa[0].data/1e3+delta, color = 'red')
	
	

	tr = raw_f[0]
	
	taper = invsim.cosTaper(len(tr.data))
	#tr = rt_calc[i][0]
	tr.data = rt_c
	
	tr.data *= taper
	if tr.stats['location'] == '':
		location = '--'
		resp_file = address + 'IRIS/Resp/RESP.' + \
			tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel']
	else:
		resp_file = address + 'IRIS/Resp/RESP.' + \
			tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel']
	
	print resp_file
	print '--------------------------------------'
	fl1 = 0.008
	fl2 = 0.012
	fl3 = 3.0
	fl4 = 4.0

	date = tr.stats['starttime']

	seedresp = {'filename':resp_file,'date':date,'units':'DIS'}
	
	try:
			
		tr.data = seisSim(data = tr.data,samp_rate = tr.stats.sampling_rate,paz_remove=None, \
			paz_simulate = None, remove_sensitivity=False, simulate_sensitivity = False, water_level = 600.0, \
			zero_mean = True, taper = False, pre_filt=(fl1,fl2,fl3,fl4), seedresp=seedresp)
		# taper_fraction=0.0,
		'''
		tr.data = seisSim(data = rawf_data,samp_rate = tr.stats.sampling_rate,paz_remove=None, \
			paz_simulate = None, remove_sensitivity=False, simulate_sensitivity = False, water_level = 600.0, \
			zero_mean = True, taper = True, taper_fraction=0.1, pre_filt=(fl1,fl2,fl3,fl4), seedresp=seedresp)
		'''
		#plt.plot(range(0, len(tr.data)), tr.data*1e9)
		#plt.plot(range(0, len(sac[0].data)), sac[0])
		#plt.plot(range(0, len(sac[0].data)), sac[0]-tr.data*1e9)


	#???????????????????????
		"""
		depth = abs(float(input_sta[i][11]))
		delta = taup.locations2degrees(float(input_sta[i][4]), float(input_sta[i][5]), float(input_sta[i][9]), float(input_sta[i][10]))
		print float(input_sta[i][4]), float(input_sta[i][5]), float(input_sta[i][9]), float(input_sta[i][10])
		print delta
		print tr.data[0]
		print '-----------------------'
		model='iasp91'
		Travel_t = taup.getTravelTimes(delta, depth, model='iasp91')

		time_all = tr.stats['npts']/tr.stats['sampling_rate']
		t_inc = np.linspace(0, time_all, tr.stats['npts'])
	
		"""
	
		if tr.stats['location'] == '':
			location = '--'
			tr.write(address + 'IRIS/eval_kasra/' + \
				tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel'], format = 'SAC')
			#aa = read(address + 'IRIS/sac_folder/' + \
			#	tr.stats['network'] + '.' + tr.stats['station'] + '.' + location + '.' + tr.stats['channel'])
				
		else:
			tr.write(address + 'IRIS/eval_kasra/' + \
				tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel'], format = 'SAC')
			#aa = read(address + 'IRIS/sac_folder/' + \
			#	tr.stats['network'] + '.' + tr.stats['station'] + '.' + tr.stats['location'] + '.' + tr.stats['channel'])
		
		
		#plt.plot(t_inc, tr.data*1e6+delta, color = 'black')
		#plt.plot(t_inc, aa[0].data/1e3+delta, color = 'red')
		'''
		for i in Travel_t:
			print i['phase_name']
		'''
	except Exception, e:
		print e


'''
req_ph = ['P', 'Pdiff', 'S']

T_t = {}

for i in np.linspace(0, 181, 1000):
	# change 300!!!!!!!! ekhtelafe zamane event va starttime
	T_t[str(i)] = taup.getTravelTimes(i, depth, model='iasp91')

ph = []
for i in T_t.keys():
	for j in T_t[i]:
		if j['phase_name'] in req_ph:
			ph.append([j['phase_name'], float(i), j['time']+300])
	#	plt.vlines(x=i['time']+300, ymin=-5.0+delta, ymax=5.0+delta, linewidth = 2, label = i['phase_name'])
		#plt.text(i['time']+300, 6+delta, i['phase_name'])


ph_dic = {}
for i in req_ph:
	jj = []
	for j in ph:
		if j[0] == i:
			jj.append([j[1], j[2]])
	
	ph_dic[i] = jj


for i in req_ph:
	ph_dic[i].sort()
	x = []
	y = []
	for j in range(0, len(ph_dic[i])):
		y.append(ph_dic[i][j][0])
		x.append(ph_dic[i][j][1])
	plt.plot(x, y, label = i)


plt.legend()
plt.show()

# -------------reponse file
client = Client()
data = client.evalresp(network = 'GR', station = 'GRA1', location = '--', channel = 'BHZ', time = raw_f[0].stats['starttime'], units='dis', output = 'fap')

reall = []
imagg = []
freq = []
resp = []
for i in data:
	reall.append(i[1])
	imagg.append(i[2])
	freq.append(i[0])
	resp.append(complex(i[1], i[2]))

'''









"""
address = '/home/hosseini/Desktop/usarray/2011-03-01_2011-04-01_9.0_9.6/20110311_0000010/'

input_file = open(address + 'IRIS/info/iris_BHZ')

'''
if os.path.exists(address + 'IRIS/eval_kasra') == True:
	shutil.rmtree(address + 'IRIS/eval_kasra')
'''
try:
	os.makedirs(address + 'IRIS/eval_kasra')

except Exception, e:
	print e


input_sta = input_file.readlines()
for i in range(0, len(input_sta)):
	input_sta[i] = input_sta[i].split(',')
"""
BH_raw_file = []
resp_file = []

for i in range(0, len(input_sta)):
	if input_sta[i][2] == '  ':
		input_sta[i][2] = '--'
	BH_raw_file.append(address + 'IRIS/BH_RAW/' + input_sta[i][0] + '.' + input_sta[i][1] + '.' + input_sta[i][2] + '.' + input_sta[i][3]) 

#import ipdb; ipdb.set_trace()
'''
raw_file = read('/home/hosseini/Desktop/30aug-inst/inst-data/iris/GR.GRA1..BHZ.sac')
sac = read('/home/hosseini/Desktop/30aug-inst/inst-data/iris/GR.GRA1..BHZ.eval')
resp_file = '/home/hosseini/Desktop/30aug-inst/inst-data/iris/RESP.GR.GRA1..BHZ'
'''


'''
