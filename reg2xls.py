#!/usr/bin/python\
REG = "REGISTRY.TXT"
from re import findall, search, sub
from os import walk, path
from copy import deepcopy
from math import ceil
from xlwt import Workbook, XFStyle
from datetime import datetime,date
#format for months
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
#colums for in output file
COL = ['N_REG','DIR','ID','FILE','DATE','TIME','CYC','POS','REP','CTIME','DTIME','DTIME2','CUCNTS','SQP','SQP5','STIME','ID1','CPM1','COUNTS1','CPM15','CPM2','COUNTS2','CPM25','CPM3','COUNTS3','CPM35','CPM4','COUNTS4','CPM45','CPM5','COUNTS5','CPM55','CPM6','COUNTS6','CPM65','CPM7','COUNTS7','CPM75','CPM8','COUNTS8','CPM85','CPMEX','COUNTSEX','PSA','PAC','CB','CHL1','CHR1','MCA1','CHL2','CHR2','MCA2','CHL3','CHR3','MCA3','CHL4','CHR4','MCA4','CHL5','CHR5','MCA5','CHL6','CHR6','MCA6','CHL7','CHR7','MCA7','CHL8','CHR8','MCA8','SP11','SP12','SP21','SP22','SPS','RESOL','INSTR']
#For debug purpose
#out_pattern2 = lambda var,intg:print("{} = {}".format(var,intg))
#Element-wise map func
elem_map = lambda funcs,data: [funcs[i](data[i]) for i in range(len(data))]
#func, that don't change element
null = lambda x:x
#spliting time variable
time_split = lambda time_var : sum(elem_map([int,lambda x:float(x)/60],time_var.split(':'))) 
time_with_sec_split = lambda time_var : sum(elem_map([int,lambda x:float(x)/60,lambda x:float(x)/3600],time_var.split(':'))) 
#type for element-wise convert
samp_types = [[int,int,int,time_with_sec_split,float,float,int,float,float,time_split],[null,float,int,float,float,int,float],[float,int,float,float,int,float]]
#get date and time for given file
getDateTime = lambda filename: datetime.fromtimestamp(path.getmtime(filename))

def get_files(dir):
	"""
	Get filenames from given directory
	"""
	for dirpath,dirnames,filenames in walk(dir): 
		return filenames 
def save_xls(path,data):
	"""
	Save formated data to xls file
	"""
	w = Workbook()
	ws = w.add_sheet('Sheet 1')
	for i in range(len(data)):
		for j in range(len(data[i])):
			if j==4 and i>0:
				continue
			ws.write(i, j, data[i][j])
	#rewrite date with apropriate format
	date_format = XFStyle()
	date_format.num_format_str = 'mm/dd/yyyy'
	for i in range(1,len(data)):
		ws.write(i, 4, data[i][4], date_format)
	w.save(path)

def get_count_from_S(path):
	"""
	Gets 'CPMEX' and 'COUNTESEX' params from sample file
	"""
	f = open(path,'r')
	samp_num,chans = f.readline()[:-1].split()[1:3]
	dif_line = f.readline()
	if 'SP#' in dif_line:#basic format
		s_time = float(dif_line.split()[2])
		curr_data = []
		for j in range(ceil(int(chans)/10)):
			curr_data+=list(int(k) for k in f.readline().split())
		countsex = sum(curr_data)
		return round(60*countsex/s_time,2),countsex 
	dif_line = f.readline()
	if 'SP#' in dif_line:#alt format
		s_time = float(dif_line.split()[2])
		curr_data = []
		for j in range(int(chans)):
			curr_data.append(int(f.readline()))
		countsex = sum(curr_data)
		return round(60*countsex/s_time,2),countsex 
	return "Can't find SP# in {}".format(path)

def folder_2_data(path):
	"""
	Parsing paramets from REG (REGISTRY.TXT) in folders recursively 
	"""
	try:
		f = open(path+'/'+REG,'r')
	except FileNotFoundError:
		print("Invalid folder:{} not found".format(REG))
		return
	data = []
	f_data = f.read().split('\n')
	pos = 0
	state = -1
	unmined = []
	samples_started = False
	while pos<len(f_data):
		if state == -1:										#Searching for date in head of file
			matched = findall(r'([A-Z]{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			if len(matched)==1:
				#out_pattern2('State',state)
				state=0
				reg_part = {}
				reg_part['DATE']=matched[0] #ignoring this
				#out_pattern2('\tDate',matched[0])
				#out_pattern2('State',state)
		elif state == 0:									#Searching for directory (DIR)
			matched = findall(r'\*\*\* DIRECTORY PATH :(.+) \*\*\*',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['DIR']=matched[0]
				#out_pattern2('\tDir',matched[0])
				#out_pattern2('State',state)
		elif state == 1:									#Searching for ID
			matched = findall(r'ID: (.+)\s*',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['ID']=matched[0]
				#out_pattern2('\tID',matched[0])
				#out_pattern2('State',state)
		elif state == 2:									#Searching for NUMBER OF CYCLES (NCYCLE)
			matched = findall(r'NUMBER OF CYCLES\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['NCYCLE']=int(matched[0])
				#out_pattern2('\tN of Cycles',matched[0])
				#out_pattern2('State',state)
		elif state == 3:									#Searching for COINCIDENCE BIAS (CB)
			matched = findall(r'COINCIDENCE BIAS \(L/H\)\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['CB']=matched[0]
				#out_pattern2('\tCB',matched[0])
				#out_pattern2('State',state)
		elif state == 4:									#Searching for PULSE COMPARATOR LEVEL(PAC), PSA LEVEL(PSA) and MCA values(WIN)
			if 'PAC' not in reg_part:
				reg_part['PAC']=0
			if 'PSA' not in reg_part:
				reg_part['PSA']=0
			matched1 = findall(r'PULSE COMPARATOR LEVEL\s+(\S+)',f_data[pos])#pac
			matched2 = findall(r'PSA LEVEL\s+(\S+)',f_data[pos])
			matched3 = findall(r'WINDOW    CHANNELS    MCA  HALF',f_data[pos])
			if len(matched1)==1:
				reg_part['PAC']=int(matched1[0])
				#out_pattern2('\tPAC',matched1[0])
				#out_pattern2('State',state)
			if len(matched2)==1:
				reg_part['PSA']=int(matched2[0])
				#out_pattern2('\tPSA',matched2[0])
				#out_pattern2('State',state)
			if len(matched3)==1:
				state+=1
				#out_pattern2('\tWin header',matched3[0])
				match_list = []
				#debug_out = #out_pattern2('\tWin data','')					
				for i in range(8):
					pos+=1
					match_list.append(findall(r'\S+\s+(\S+)-\s+(\S+)\s+(\S+)\s+(\S+)',f_data[pos])[0])
					#if debug_out==None:
					#	print('\t\t'+str(match_list[-1]))
				reg_part['WIN']=match_list
				#out_pattern2('State',state)
		elif state == 5:									#Searching for spectrums (SP11,SP12,SP21,SP22)
			matched = findall(r'SEND SPECTRA\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['SP11']='11' in matched[0]
				reg_part['SP12']='12' in matched[0]
				reg_part['SP21']='21' in matched[0]
				reg_part['SP22']='22' in matched[0]
				reg_part['SPS']='S' in matched[0]
				#out_pattern2('\tSpectrums',matched[0])
				#out_pattern2('State',state)
		elif state == 6:									#Searching for spectrum resolution (RESOL)
			matched = findall(r'RESOLUTION OF SPECTRA\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['RESOL']=matched[0]
				#out_pattern2('\tRESOLUTION',int(matched[0]))
				#out_pattern2('State',state)
		elif state == 7:
			matched = findall(r'INSTRUMENT NUMBER\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['INSTR']=int(matched[0])
				#out_pattern2('\tINSTR NUMBER',matched[0])
				#out_pattern2('State',state)
		elif state == 8:									#Searching for sample data
			if 'SAMPLES' not in reg_part:
				reg_part['SAMPLES']=[]
			matched1 = findall(r'(Q\d{6}N\.\d{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			matched2 = findall(r'([A-Z]{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			if len(matched1)==1:
				samples_started = True
				#out_pattern2('\tSample header',matched1[0])
				s_header = list(matched1[0])
				for i in range(5):							#Some magic to handle sample data
					pos+=1
					s_line = [i for i in findall(r'(\S+)'+r'\s+(\S+)'*[9,6,5,5,5][i],f_data[pos])][0]
					s_line = elem_map(samp_types[i if i < len(samp_types) else 2],s_line)
					#out_pattern2('\t____',s_line)
					s_header+= s_line
				if sub(r'N',r'S',s_header[0]) in get_files(path):
					cpmex,countsex = get_count_from_S(path+'/'+sub(r'N',r'S',s_header[0]))
				else:
					cpmex,countsex = 0,0
				s_header.append(cpmex)
				s_header.append(countsex)
				s_header.append(getDateTime(path+'/'+sub(r'S',r'N',s_header[0])))
				#out_pattern2('\tcountsex',countsex)
				#out_pattern2('\tcpmex',cpmex)
				reg_part['SAMPLES'].append(s_header)
				##out_pattern2('\tSample',s_header)
				#out_pattern2('State',state)
			if len(matched2)==1:
				state=0
				samples_started = False
				#if debug_out==None:
				#	print("*** NEW REG ***")
				unmined.append(reg_part)
				reg_part = {}
				reg_part['DATE']=matched2[0]
				#out_pattern2('\tDate',matched2[0])
				#out_pattern2('State',state)		
		pos+=1
	if samples_started:
		unmined.append(reg_part)
	return unmined

	
def prepare_data(data):
	result=[]
	for reg in data:
		curr_reg = ['-_-' for i in range(77)]
		#global for all samples vars
		curr_reg[1]=reg['DIR']
		curr_reg[2]=reg['ID']
		curr_reg[43]=reg['PSA']
		curr_reg[44]=reg['PAC']
		curr_reg[45]=reg['CB']
		for i in range(8):
			curr_reg[46+3*i]=int(reg['WIN'][i][0])
			curr_reg[46+3*i+1]=int(reg['WIN'][i][1])
			curr_reg[46+3*i+2]=reg['WIN'][i][2]+reg['WIN'][i][3]
		curr_reg[70]=reg['SP11']
		curr_reg[71]=reg['SP12']
		curr_reg[72]=reg['SP21']
		curr_reg[73]=reg['SP22']
		curr_reg[74]=reg['SPS']
		curr_reg[75]=int(reg['RESOL'])
		curr_reg[76]=reg['INSTR']
		for samp in reg['SAMPLES']:
		#if False:
			sample_reg = deepcopy(curr_reg)
			preTime = samp[42].timetuple()
			sample_reg[0]=int(samp[15]) if samp[15].isnumeric() else 0
			sample_reg[3]=samp[0]
			sample_reg[4]=date(preTime[0],preTime[1],preTime[2])
			sample_reg[5]=round(time_with_sec_split("{}:{}:{}".format(preTime[3],preTime[4],preTime[5])),3)
			sample_reg[6:41]=samp[5:40]
			sample_reg[9]=round(sample_reg[9],2)
			sample_reg[15]=round(sample_reg[15],2)
			sample_reg[41]=samp[40]
			sample_reg[42]=samp[41]
			result.append(sample_reg)
		#print(len(reg[]))
	return result

def main():
	from sys import argv
	if len(argv)!=3:
		print("Usage: reg2csv.py folder output_file.xls")
	else:
		final_samples = [COL]
		dir_count = 0
		for dirpath,dirnames,filenames in walk(argv[1]): 
			if REG in filenames:
				unmined_samples = folder_2_data(dirpath)
				mined_samples = prepare_data(unmined_samples)
				final_samples+=mined_samples
				dir_count+=1
		if len(final_samples)!=1:
			print("{} folders found, with {} samples".format(dir_count,len(final_samples)-1))
			save_xls(argv[2],final_samples)
		else:
			print('Can\'t found any samples')

if __name__ == "__main__":
	main()