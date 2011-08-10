#???????????????????????????????????????????????

from obspy.xseed import Parser



def parse_reponse_ARC():
	pars = Parser()
						
	pars.read(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
		Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
					
	pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
		Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')


	pars = Parser()
						
	pars.read(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
		Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
					
	pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHN[i][j][0] +	'.' + Nets_Arc_req_BHN[i][j][1] + '.' + \
		Nets_Arc_req_BHN[i][j][2] + '.' + 'BHN')
		
	pars = Parser()
						
	pars.read(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
		Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
				
	pars.writeRESP(Address_events + '/' + events[i]['event_id'] + \
		'/ARC/RESP/' + 'RESP' + '.' + Nets_Arc_req_BHZ[i][j][0] +	'.' + Nets_Arc_req_BHZ[i][j][1] + '.' + \
		Nets_Arc_req_BHZ[i][j][2] + '.' + 'BHZ')
