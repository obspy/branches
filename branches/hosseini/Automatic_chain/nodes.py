import commands

def nodes(input):
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
	if commands.getoutput('hostname') == 'hopfen':
		if commands.getoutput('tty') == '/dev/pts/0':
			input['min_date'] = '2011-01-08'
			input['max_date'] = '2011-01-10'
		
		if commands.getoutput('tty') == '/dev/pts/1':
			input['min_date'] = '2011-01-11'
			input['max_date'] = '2011-01-13'	
		
		if commands.getoutput('tty') == '/dev/pts/2':
			input['min_date'] = '2011-02-09'
			input['max_date'] = '2011-02-11'
		
		if commands.getoutput('tty') == '/dev/pts/3':
			input['min_date'] = '2011-02-13'
			input['max_date'] = '2011-02-15'

		if commands.getoutput('tty') == '/dev/pts/4':
			input['min_date'] = '2011-02-20'
			input['max_date'] = '2011-02-22'
		
		if commands.getoutput('tty') == '/dev/pts/5':
			input['min_date'] = '2011-03-05'
			input['max_date'] = '2011-03-07'
		
		if commands.getoutput('tty') == '/dev/pts/6':
			input['min_date'] = '2011-03-08'
			input['max_date'] = '2011-03-10'
		
		if commands.getoutput('tty') == '/dev/pts/7':
			input['min_date'] = '2011-03-09'
			input['max_date'] = '2011-03-11'
		
		if commands.getoutput('tty') == '/dev/pts/8':
			input['min_date'] = '2011-03-11'
			input['max_date'] = '2011-03-13'
		
		if commands.getoutput('tty') == '/dev/pts/9':
			input['min_date'] = '2011-03-23'
			input['max_date'] = '2011-03-26'
		
		if commands.getoutput('tty') == '/dev/pts/10':
			input['min_date'] = '2011-03-26'
			input['max_date'] = '2011-03-28'
		
		if commands.getoutput('tty') == '/dev/pts/11':
			input['min_date'] = '2011-04-02'
			input['max_date'] = '2011-04-04'
		
		if commands.getoutput('tty') == '/dev/pts/12':
			input['min_date'] = '2011-04-06'
			input['max_date'] = '2011-04-08'
		
		if commands.getoutput('tty') == '/dev/pts/13':
			input['min_date'] = '2011-04-10'
			input['max_date'] = '2011-04-12'
		
		if commands.getoutput('tty') == '/dev/pts/14':
			input['min_date'] = '2011-04-17'
			input['max_date'] = '2011-04-19'
		
		if commands.getoutput('tty') == '/dev/pts/15':
			input['min_date'] = '2011-04-22'
			input['max_date'] = '2011-04-24'
		
		if commands.getoutput('tty') == '/dev/pts/16':
			input['min_date'] = '2011-05-14'
			input['max_date'] = '2011-05-16'
		
		if commands.getoutput('tty') == '/dev/pts/17':
			input['min_date'] = '2011-06-02'
			input['max_date'] = '2011-06-04'
			
		if commands.getoutput('tty') == '/dev/pts/18':
			input['min_date'] = '2011-06-15'
			input['max_date'] = '2011-06-17'
		
		if commands.getoutput('tty') == '/dev/pts/19':
			input['min_date'] = '2011-06-19'
			input['max_date'] = '2011-06-21'
		
	if commands.getoutput('hostname') == 'moench':
		if commands.getoutput('tty') == '/dev/pts/0':
			input['min_date'] = '2011-04-17'
			input['max_date'] = '2011-04-19'
		
		if commands.getoutput('tty') == '/dev/pts/8':
			input['min_date'] = '2011-04-22'
			input['max_date'] = '2011-04-24'
		
		if commands.getoutput('tty') == '/dev/pts/10':
			input['min_date'] = '2011-05-14'
			input['max_date'] = '2011-05-16'
		
		if commands.getoutput('tty') == '/dev/pts/11':
			input['min_date'] = '2011-06-02'
			input['max_date'] = '2011-06-04'
	
	if commands.getoutput('hostname') == 'kochel':
		if commands.getoutput('tty') == '/dev/pts/0':
			input['min_date'] = '2011-06-15'
			input['max_date'] = '2011-06-17'	
		
		if commands.getoutput('tty') == '/dev/pts/2':
			input['min_date'] = '2011-06-02'
			input['max_date'] = '2011-06-04'
		
		if commands.getoutput('tty') == '/dev/pts/1':
			input['min_date'] = '2011-06-19'
			input['max_date'] = '2011-06-21'
		
		if commands.getoutput('tty') == '/dev/pts/3':
			input['min_date'] = '2011-06-21'
			input['max_date'] = '2011-06-23'
			
	return input
