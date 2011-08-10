"""
Updating in Parallel way
"""

import commands

def nodes_update (input, pre_ls_event):
	'''
	if commands.getoutput('hostname') == 'kasra-laptop':
		input['min_date'] = '2011-01-01'
		input['max_date'] = '2011-01-10'
		input['Address'] = '/media/Elements/TEST2_NODE'
	
	if commands.getoutput('hostname') == 'funten':
		if commands.getoutput('tty') == '/dev/pts/11':
			input['min_date'] = '2011-07-01'
			input['max_date'] = '2011-08-25'
	'''
	pre = []
	if commands.getoutput('hostname') == 'hopfen':
		
		if commands.getoutput('tty') == '/dev/pts/0':
			pre.append(pre_ls_event[0])
			
		if commands.getoutput('tty') == '/dev/pts/1':
			pre.append(pre_ls_event[1])
		
		if commands.getoutput('tty') == '/dev/pts/2':
			pre.append(pre_ls_event[2])
		
		if commands.getoutput('tty') == '/dev/pts/3':
			pre.append(pre_ls_event[3])

		if commands.getoutput('tty') == '/dev/pts/4':
			pre.append(pre_ls_event[4])
		
		if commands.getoutput('tty') == '/dev/pts/5':
			pre.append(pre_ls_event[5])
		
		if commands.getoutput('tty') == '/dev/pts/6':
			pre.append(pre_ls_event[6])
		
		if commands.getoutput('tty') == '/dev/pts/7':
			pre.append(pre_ls_event[7])
			
		if commands.getoutput('tty') == '/dev/pts/8':
			pre.append(pre_ls_event[8])
		
		if commands.getoutput('tty') == '/dev/pts/9':
			pre.append(pre_ls_event[9])
		
			
	return pre
