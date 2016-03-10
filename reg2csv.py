#!/usr/bin/python\
REG = "REGISTRY.TXT"
from re import findall, search, sub
from os import walk
from copy import deepcopy
from math import ceil
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
COL = ['N_REG','DIR','ID','FILE','DATE','TIME','CYC','POS','REP','CTIME','DTIME','DTIME2','CUCNTS','SQP','SQP5','STIME','ID1','CPM1','COUNTS1','CPM15','CPM2','COUNTS2','CPM25','CPM3','COUNTS3','CPM35','CPM4','COUNTS4','CPM45','CPM5','COUNTS5','CPM55','CPM6','COUNTS6','CPM65','CPM7','COUNTS7','CPM75','CPM8','COUNTS8','CPM85','CPMEX','COUNTSEX','PSA','PAC','CB','CHL1','CHR1','MCA1','CHL2','CHR2','MCA2','CHL3','CHR3','MCA3','CHL4','CHR4','MCA4','CHL5','CHR5','MCA5','CHL6','CHR6','MCA6','CHL7','CHR7','MCA7','CHL8','CHR8','MCA8','SP11','SP12','SP21','SP22','SPS','RESOL','INSTR']

def get_files(dir):
	for dirpath,dirnames,filenames in walk(dir): 
		return filenames 
def save_csv (path,data):
	f=open(path,'w')
	f.write('\n'.join(','.join(i) for i in data))
	f.close()
out_pattern = lambda var,intg:print("Set {} to {}".format(var,intg))
out_pattern2 = lambda var,intg:-1#print("{} = {}".format(var,intg))
def get_count_from_S(path):
	f = open(sub(r'N',r'S',path),'r')
	samp_num,chans = f.readline()[:-1].split()[1:3]
	dif_line = f.readline()
	if 'SP#' in dif_line:#basic format
		s_time = float(dif_line.split()[2])
		curr_data = []
		for j in range(ceil(int(chans)/10)):
			curr_data+=list(int(k) for k in f.readline().split())
		countsex = sum(curr_data)
		return countsex,60*countsex/s_time
	dif_line = f.readline()
	if 'SP#' in dif_line:#alt format
		s_time = float(dif_line.split()[2])
		curr_data = []
		for j in range(int(chans)):
			curr_data.append(int(f.readline()))
		countsex = sum(curr_data)
		return countsex,60*countsex/s_time
	return "Can't find SP# in {}".format(path)
def folder_2_data(path):
	try:
		f = open(path+'/'+REG,'r')
	except FileNotFoundError:
		print("Invalid folder:{} not found".format(REG))
		return
	data = []
	f_data = f.read().split('\n')
	#data.append(['ID','SPECTRUMS','Samples'])
	pos = 0
	state = -1
	unmined = []
	samples_started = False
	while pos<len(f_data):
		if state == -1:
			matched = findall(r'([A-Z]{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part = {}
				reg_part['DATE']=matched[0]
				out_pattern2('Date',matched[0])
				out_pattern2('State',state)
		elif state == 0:
			matched = findall(r'\*\*\* DIRECTORY PATH :(.+) \*\*\*',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['DIR']=matched[0]
				out_pattern2('\tDir',matched[0])
				out_pattern2('State',state)
		elif state == 1:
			matched = findall(r'ID: (\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['ID']=matched[0]
				out_pattern2('\tID',matched[0])
				out_pattern2('State',state)
		elif state == 2:
			matched = findall(r'NUMBER OF CYCLES\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['NCYCLE']=matched[0]
				out_pattern2('\tN of Cycles',matched[0])
				out_pattern2('State',state)
		elif state == 3:
			matched = findall(r'COINCIDENCE BIAS \(L/H\)\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['CB']=matched[0]
				out_pattern2('\tCB',matched[0])
				out_pattern2('State',state)
		elif state == 4:
			if 'PAC' not in reg_part:
				reg_part['PAC']=0
			if 'PSA' not in reg_part:
				reg_part['PSA']=0

			matched1 = findall(r'PULSE COMPARATOR LEVEL\s+(\S+)',f_data[pos])#pac
			matched2 = findall(r'PSA LEVEL\s+(\S+)',f_data[pos])
			matched3 = findall(r'WINDOW    CHANNELS    MCA  HALF',f_data[pos])
			if len(matched1)==1:
				reg_part['PAC']=matched1[0]
				out_pattern2('\tPAC',matched1[0])
				out_pattern2('State',state)
			if len(matched2)==1:
				reg_part['PSA']=matched2[0]
				out_pattern2('\tPSA',matched2[0])
				out_pattern2('State',state)
			if len(matched3)==1:
				state+=1
				out_pattern2('\tWin header',matched3[0])
				match_list = []
				debug_out = out_pattern2('\tWin data','')					
				for i in range(8):
					pos+=1
					match_list.append(findall(r'\S+\s+(\S+)-\s+(\S+)\s+(\S+)\s+(\S+)',f_data[pos])[0])
					if debug_out==None:
						print('\t\t'+str(match_list[-1]))
				reg_part['WIN']=match_list
				out_pattern2('State',state)
		elif state == 5:
			matched = findall(r'SEND SPECTRA\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['SP11']='11' in matched[0]
				reg_part['SP12']='12' in matched[0]
				reg_part['SP21']='21' in matched[0]
				reg_part['SP22']='22' in matched[0]
				reg_part['SPS']='S' in matched[0]
				out_pattern2('\tSpectrums',matched[0])
				out_pattern2('State',state)
		elif state == 6:
			matched = findall(r'RESOLUTION OF SPECTRA\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['RESOL']=matched[0]
				out_pattern2('\tRESOLUTION',matched[0])
				out_pattern2('State',state)
		elif state == 7:
			matched = findall(r'INSTRUMENT NUMBER\s+(\S+)',f_data[pos])
			if len(matched)==1:
				state+=1
				reg_part['INSTR']=matched[0]
				out_pattern2('\tINSTR NUMBER',matched[0])
				out_pattern2('State',state)
		elif state == 8:
			if 'SAMPLES' not in reg_part:
				reg_part['SAMPLES']=[]
			matched1 = findall(r'(Q\d{6}N\.\d{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			matched2 = findall(r'([A-Z]{3})\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d{1,2}:\d{1,2})',f_data[pos])
			if len(matched1)==1:
				samples_started = True
				out_pattern2('\tSample header',matched1[0])
				s_header = list(matched1[0])
				for i in range(5):
					pos+=1
					s_header+=[i for i in findall(r'(\S+)'+r'\s+(\S+)'*[9,6,5,5,5][i],f_data[pos])][0]
				if sub(r'N',r'S',s_header[0]) in get_files(path):
					countsex,cpmex = get_count_from_S(path+'/'+sub(r'N',r'S',s_header[0]))
				else:
					countsex,cpmex = 0,0
				s_header.append(countsex)
				s_header.append(cpmex)
				reg_part['SAMPLES'].append(s_header)
				out_pattern2('State',state)
			if len(matched2)==1:
				state=0
				samples_started = False
				if debug_out==None:
					print("*** NEW REG ***")
				unmined.append(reg_part)
				reg_part = {}
				reg_part['DATE']=matched2[0]
				out_pattern2('\tDate',matched2[0])
				out_pattern2('State',state)		
		pos+=1
	if samples_started:
		unmined.append(reg_part)
	return unmined
def prepare_data(data):
	result=[]
	result.append(COL)
	for reg in data:
		curr_reg = ['0' for i in range(77)]
		#global for all samples vars
		curr_reg[1]=reg['DIR']
		curr_reg[2]=reg['ID']
		curr_reg[43]=str(reg['PSA'])
		curr_reg[44]=reg['PAC']
		curr_reg[45]=reg['CB']
		for i in range(8):
			curr_reg[46+3*i]=reg['WIN'][i][0]
			curr_reg[46+3*i+1]=reg['WIN'][i][1]
			curr_reg[46+3*i+2]=reg['WIN'][i][2]+reg['WIN'][i][3]
		curr_reg[70]=str(reg['SP11'])
		curr_reg[71]=str(reg['SP12'])
		curr_reg[72]=str(reg['SP21'])
		curr_reg[73]=str(reg['SP22'])
		curr_reg[74]=str(reg['SPS'])
		curr_reg[75]=str(reg['RESOL'])
		curr_reg[76]=str(reg['INSTR'])
		for samp in reg['SAMPLES']:
			sample_reg = deepcopy(curr_reg)
			pre_date = list(samp[1:4])
			pre_date[1] = str(MONTHS.index(pre_date[1])+1)
			sample_reg[4]="/".join(pre_date)
			sample_reg[3]=samp[0]
			sample_reg[0]=samp[15] if samp[15].isnumeric() else 0
			sample_reg[5]=samp[4]
			sample_reg[6:40]=samp[5:39]
			sample_reg[40]=str(samp[39])
			sample_reg[41]=str(samp[40])
			result.append(sample_reg)
		#print(len(reg[]))
	return result

def main():
	from sys import argv
	print(argv)
	if len(argv)!=3:
		print("Usage: reg2csv.py folder/ output_file.csv")
	else:
		if REG in get_files(argv[1]):
			unmined = folder_2_data(argv[1])
			mined = prepare_data(unmined)
			save_csv(argv[2],mined)
		else:
			print('Can\'t find '+REG+' file')
main()

#0 N_REG
#1 DIR
#2 ID
#3 FILE
#4 DATE
#5 TIME
#6 CYC
#7 POS
#8 REP
#9 CTIME
#10 DTIME
#11 DTIME2
#12 CUCNTS
#13 SQP
#14 SQP5
#15 STIME
#16 ID1
#17 CPM1
#18 COUNTS1
#19 CPM15
#20 CPM2
#21 COUNTS2
#22 CPM25
#23 CPM3
#24 COUNTS3
#25 CPM35
#26 CPM4
#27 COUNTS4
#28 CPM45
#29 CPM5
#30 COUNTS5
#31 CPM55
#32 CPM6
#33 COUNTS6
#34 CPM65
#35 CPM7
#36 COUNTS7
#37 CPM75
#38 CPM8
#39 COUNTS8
#40 CPM85
#41 CPMEX
#42 COUNTSEX
#43 PSA
#44 PAC
#45 CB
#46 CHL1
#47 CHR1
#48 MCA1
#49 CHL2
#50 CHR2
#51 MCA2
#52 CHL3
#53 CHR3
#54 MCA3
#55 CHL4
#56 CHR4
#57 MCA4
#58 CHL5
#59 CHR5
#60 MCA5
#61 CHL6
#62 CHR6
#63 MCA6
#64 CHL7
#65 CHR7
#66 MCA7
#67 CHL8
#68 CHR8
#69 MCA8
#70 SP11
#71 SP12
#72 SP21
#73 SP22
#74 SPS
#75 RESOL
#76 INSTR
