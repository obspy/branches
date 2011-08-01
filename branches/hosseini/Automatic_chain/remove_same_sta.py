import pickle

def remove_same_sta():
	iris = open('/media/KINGSTON/TEST_NODES/TEST2_NODES/Data/2011-01-08_2011-01-10_6.5_6.8/20110109_0000017/IRIS/STATION/Input_Syn_BHE', 'r')
	IRIS_BHE = iris.readlines()
	for i in range(0, len(IRIS_BHE)):
		IRIS_BHE[i] = IRIS_BHE[i].split(',')
	
	arc = open('/media/KINGSTON/TEST_NODES/TEST2_NODES/Data/2011-01-08_2011-01-10_6.5_6.8/20110109_0000017/ARC/STATION/Input_Syn_BHE', 'r')
	ARC_BHE = arc.readlines()
	for i in range(0, len(ARC_BHE)):
		ARC_BHE[i] = ARC_BHE[i].split(',')
		
	
	one solution:
	
	for i in range(0, len(IRIS_BHE)):
		for k in range(0, len(ARC_BHE)):
			if ARC_BHE[k][0] == IRIS_BHE[i][0]:
				if ARC_BHE[k][1] == IRIS_BHE[i][1]:
					if ARC_BHE[k][2] == IRIS_BHE[i][2]:
						if ARC_BHE[k][3] == IRIS_BHE[i][3]:
							print ARC_BHE[k][0] + '.' + ARC_BHE[k][1] + '.' + ARC_BHE[k][2] + '.' + ARC_BHE[k][3]
