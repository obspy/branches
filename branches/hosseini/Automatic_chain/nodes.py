"""
Downloading in Parallel way
Suggestion: Do not request more than 10 in parallel...
"""

import commands
import os

def nodes(input):
	
	add = os.getcwd()
	add += '/INPUT-Periods'
	f = open(add)
	per_tty = f.readlines()
	
	for i in range(0, len(per_tty)):
		per_tty[i] = per_tty[i].split('_')
	
	if os.path.exists(input['Address'] + '/Data/' + 'tty-info') != True:
	
		if os.path.exists(input['Address'] + '/Data') != True:
			os.makedirs(input['Address'] + '/Data')
	
		tty = open(input['Address'] + '/Data/' + 'tty-info', 'w')
		
		tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[0][0] + \
				'_' + per_tty[0][1] + '_' + per_tty[0][2] + '_' + per_tty[0][3][:-1] + '  ,  ' +  '\n')
		
		tty.close()
		
	else:
		n = int(raw_input('Please enter a node number:' + '\n' + '(If you enter "-1", it means that the node number already exists in the file.)' + '\n'))
		print '-------------------------------------------------------------'
		
		if n == -1:
			print 'You entered "-1" -- the node number exists in the tty-info!'
			print '-------------------------------------------------------------'
		else: 
			tty = open(input['Address'] + '/Data/' + 'tty-info', 'a')
			tty.writelines(commands.getoutput('hostname') + '  ,  ' + commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
					'_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + per_tty[n][3][:-1] + '  ,  ' +  '\n')

			tty.close()		
	
	
	Address_data = input['Address'] + '/Data'
	
	tty = open(input['Address'] + '/Data/' + 'tty-info', 'r')
	tty_str = tty.readlines()
	
	for i in range(0, len(tty_str)):
		tty_str[i] = tty_str[i].split('  ,  ')
	
	for i in range(0, len(tty_str)):
		if commands.getoutput('hostname') == tty_str[i][0]:
			if commands.getoutput('tty') == tty_str[i][1]:
				
				input['min_date'] = tty_str[i][2].split('_')[0]
				input['max_date'] = tty_str[i][2].split('_')[1]
					
	return input
