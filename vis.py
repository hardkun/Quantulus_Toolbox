#!/usr/bin/python
#Made by Buzynniy Oleksandr 
#email:9alexua9( at )gmail.com
#2016
color = ['b','g','r','y']
default_spectrums = ['11','12','21','22']
from os import walk
from re import findall
REG = "REGISTRY.TXT"
def get_folders(root):
	found = []
	for path,folders,files in walk(root): 
		if (REG in files)and(any(i.split(".")[1].isnumeric() for i in files)):#found registry and spectre
			found.append(path)
	return found
def get_files(dir):
	for dirpath,dirnames,filenames in walk(dir): 
		return filenames 
get_file_type = lambda filenames: ["REGISTRY" if REG in i else "HISTOGRAM" if (i.split(".")[1].isnumeric())or(i.split('.')[1]=='sum') else "OTHER" for i in filenames]
def inp_num(array,for_files=False,for_folders=False):
	print("Please select number to open:")
	while True:
		selected = input()
		spectrums = None
		if for_files==True:
			if len(selected.split())>1:
				selected,spectrums = selected.split()[:2]
				raw_spectrums_num = []
			else: raw_spectrums_num = list(range(4))
		elif for_folders==True:
			if len(selected.split())>1:

				selected,arg = selected.split()[:2]
			else: arg=None
		if selected=="-": return "-","-","-"
		elif not(selected.isnumeric()): print("Invalid name, please reenter number")
		elif not(int(selected) in range(len(array))): print("Folder num is out of range, please reenter number")
		elif spectrums!=None:
			raw_spectrums_num = select_spectrum(spectrums)
			if raw_spectrums_num!=None:	break
		elif for_folders==True:
			if (arg == '*')or(arg == None): break
		else: break
	if for_files==True: return array[int(selected)],int(selected),raw_spectrums_num
	return array[int(selected)],int(selected),(arg=='*')
parse_reg = lambda path:(findall(r'ID: (.+)\n',open(path+'/'+REG,'r').read())[0],findall(r'SEND SPECTRA (.+)\n',open(path+'/'+REG,'r').read())[0])
def select_folder(folders):
	if len(folders)>1:
		#out folders
		print("{} folders found:".format(len(folders)))
		IDs,l_spec = list(zip(*[parse_reg(i) for i in folders]))
		max_len = (str(max(map(len,IDs))),str(max(map(len,l_spec))))
		print(("{:>4} {:<"+max_len[0]+"} {:<"+max_len[1]+"} {}").format("NUM","ID","SPECT","FOLDER"))
		for n,i in enumerate(folders):
			#print(n,IDs[n],l_spec[n],i)
			print(("{:>4} {:<"+max_len[0]+"} {:<"+max_len[1]+"} {}").format(n,IDs[n],l_spec[n],i))
		#read user's choice
		selected,num,is_star = inp_num(folders,for_folders=True)
	elif len(folders)==1:
		selected = folders[0]
		is_star=False
	else:
		print("No folders found")
		exit()
	return selected,is_star
def select_file(files):
	print("{} files found:".format(len(files)))
	for n,i in enumerate(files):
		print("{:>4} {}".format(n,i))
	s_file,num,raw_spectrums = inp_num(files,for_files=True)
	if s_file == "-":
		return "-","-","-"
	return s_file,get_file_type([s_file])[0],raw_spectrums
def select_spectrum(selected):
	result=[]
	for i in range(len(selected)//2):
		if selected[2*i:2*(i+1)] in default_spectrums:
			result.append(default_spectrums.index(selected[2*i:2*(i+1)]))
		else:
			print("Incorrect spectrum format!")
			return None
	return sorted(result)
def smooth_data(data):
	new_data = [[sum(data[j][i-1:i+2])/3 for i in range(1,len(data[j])-1)] for j in range(len(data))]
	for i in range(len(data)):
		new_data[i].insert(0,sum(data[i][:2])/2)
		new_data[i].append(sum(data[i][-2:])/2)
	return new_data
def visualise(path,spectrums):
	from matplotlib import pyplot as plt
	from math import ceil
	f = open(path,'r')
	data = []
	samp_num,chans = f.readline()[:-1].split()[1:3]#read sample ID and number of samples in file
	first_spect = f.readline()
	if first_spect.split()[0]=="SP#":#default format
		for i in range(int(samp_num)):
			curr_data = []
			for j in range(ceil(int(chans)/10)):
				curr_data+=list(int(k) for k in f.readline().split())
			maxx = max(curr_data)
			curr_data=[j/maxx for j in curr_data]
			data.append(curr_data)
			f.readline()
	else:#other format
		f.readline()
		for i in range(int(samp_num)):
			curr_data = []
			for j in range(int(chans)):
				curr_data.append(int(f.readline()))
			maxx = max(curr_data)
			curr_data=[j/maxx for j in curr_data]
			data.append(curr_data)
			f.readline()
	data = smooth_data(data)
	plt.title(path.split('/')[-1]+('' if spectrums==list(range(4)) else '('+','.join(map((lambda x:default_spectrums[x]),spectrums))+')'))
	plt.xlim([0,len(data[0])])
	if len(data)>1:
		for n,i in enumerate(data):
			if n in spectrums: plt.plot(i,color[n])
		plt.show()
	else:
		plt.plot(data[0],color[0])
		plt.show()
def show_file(path):
	print("")
	print("File:")
	print("")
	counter = 10
	f = open(path,'r')
	for line in f:
		print(line,end='')
		counter-=1
		if counter<1:
			input()
			counter=10
def print_manual():
	print("Test Manual")
	print()
	print()
	print()
	print()
def main():
	from sys import argv
	if len(argv)!=2:
		print("Usage: vis.py folder/")
	else:
		if argv[1]=='-h':
			print_manual()
			exit()
		while True:
			folders = get_folders(argv[1])
			s_folder,is_star = select_folder(folders)
			if s_folder=="-":
				break
			if is_star:
				for i in get_files(s_folder):
					if get_file_type([i]) == ["HISTOGRAM"]:
						visualise(s_folder+"/"+i,list(range(4)))
			else:
				while True:
					files = get_files(s_folder)
					s_file,file_type,raw_spectrums = select_file(files)
					if s_file=="-":	break
					elif file_type == "HISTOGRAM":	visualise(s_folder+"/"+s_file,raw_spectrums)
					elif file_type == "REGISTRY":	show_file(s_folder+"/"+s_file)
					else: print("Unable to open {}".format(s_file))

if __name__ == "__main__":
	main()