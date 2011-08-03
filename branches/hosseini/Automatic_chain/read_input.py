"""
Read inputs from INPUT file
"""

import os

def read_input():	
	add = os.getcwd()
	add += '/INPUT'
	f = open(add)
	S = f.readlines()
	input = {}
	input['Address'] = S[0].split()[2]
	input['min_date'] = S[1].split()[2]
	input['max_date'] = S[2].split()[2]
	input['min_mag'] = float(S[3].split()[2])
	input['max_mag'] = float(S[4].split()[2])
	input['min_lat'] = float(S[5].split()[2])
	input['max_lat'] = float(S[6].split()[2])
	input['min_lon'] = float(S[7].split()[2])
	input['max_lon'] = float(S[8].split()[2])
	input['min_depth'] = float(S[9].split()[2])
	input['max_depth'] = float(S[10].split()[2])
	input['max_result'] = int(S[11].split()[2])
	input['t_before'] = float(S[12].split()[2])
	input['t_after'] = float(S[13].split()[2])
	input['plt_event'] = S[15].split()[2]
	input['net'] = S[17].split()[2]
	input['sta'] = S[18].split()[2]
	input['loc'] = S[19].split()[2]
	input['cha'] = S[20].split()[2]
	input['BHE'] = S[21].split()[2]
	input['BHN'] = S[22].split()[2]
	input['BHZ'] = S[23].split()[2]
	input['lat_cba'] = S[29].split()[2]
	input['lon_cba'] = S[30].split()[2]
	input['mr_cba'] = S[31].split()[2]
	input['Mr_cba'] = S[32].split()[2]
	
	if S[33].split()[2] == 'None':
		input['mlat_rbb'] = None
	else:
		input['mlat_rbb'] = S[33].split()[2]
	
	if S[34].split()[2] == 'None':
		input['Mlat_rbb'] = None
	else:
		input['Mlat_rbb'] = S[34].split()[2]
	
	if S[35].split()[2] == 'None':
		input['mlon_rbb'] = None
	else:
		input['mlon_rbb'] = S[35].split()[2]
	
	if S[36].split()[2] == 'None':
		input['Mlon_rbb'] = None
	else:
		input['Mlon_rbb'] = S[36].split()[2]

	input['llcrnrlon'] = float(S[40].split()[2])
	input['llcrnrlat'] = float(S[41].split()[2])
	input['urcrnrlon'] = float(S[42].split()[2])
	input['urcrnrlat'] = float(S[43].split()[2])
	
	input['mass'] = S[45].split()[2]
	input['IRIS'] = S[46].split()[2]
	input['ArcLink'] = S[47].split()[2]
	input['QC_IRIS'] = S[48].split()[2]
	input['QC_ARC'] = S[49].split()[2]
	input['get_events'] = S[50].split()[2]
	input['nodes'] = S[51].split()[2]
	input['update_iris'] = S[52].split()[2]
	input['update_arc'] = S[53].split()[2]

	return input
