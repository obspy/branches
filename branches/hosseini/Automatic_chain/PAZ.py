def PAZ():
	
	a = open('RESP.AK.BAL.--.BHE')
	resp = a.readlines()
	
	poles = []
	for i in range(0, len(resp)):
		if resp[i][0] == 'B053F15-18':
			poles.append(resp[i])
			
	POLES = []
	for i in range(0, len(poles)):
		POLES.append((poles[i][2], poles[i][3]))
