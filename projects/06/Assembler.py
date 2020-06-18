import sys
import os

class Assembler:
	def __init__(self,file_path):
		"""initialize the Assembler
		read in the file and ignore the blank lines and comment lines
		@param file_path(str) : the .asm file to be translated into binary code
		"""	
		self.codes=[]
		self.binary_codes=[]
		self.allo_address=16 # the next address to be allocated to the variable symbol
		self.sym_table={
		"SP":0,"LCL":1,"ARG":2,"THIS":3,"THAT":4,
		"R0":0,"R1":1,"R2":2,"R3":3,"R4":4,"R5":5,
		"R6":6,"R7":7,"R8":8,"R9":9,"R10":10,"R11":11,
		"R12":12,"R13":13,"R14":14,"R15":15,
		"SCREEN":16384,"KBD":24576} # pre-defined label
		self.comp_table={
		"0":"0101010","1":"0111111","-1":"0111010",
		"D":"0001100","A":"0110000","!D":"0001101", 
		"!A":"0110001","-D":"0001111","-A":"0110011",
		"D+1":"0011111","A+1":"0110111","D-1":"0001110",
		"A-1":"0110010","D+A":"0000010","D-A":"0010011",
		"A-D":"0000111","D&A":"0000000","D|A":"0010101",
		"M":"1110000","!M":"1110001","-M":"1110011",
		"M+1":"1110111","M-1":"1110010","D+M":"1000010",
		"D-M":"1010011","M-D":"1000111","D&M":"1000000",
		"D|M":"1010101"
		}
		self.dest_table={
		"null":"000","M":"001","D":"010","MD":"011",
		"A":"100","AM":"101","AD":"110","AMD":"111"
		}
		self.jmp_table={
		"null":"000","JGT":"001","JEQ":"010","JGE":"011",
		"JLT":"100","JNE":"101","JLE":"110","JMP":"111"
		}
		self.file_name=os.path.basename(file_path)
		suffix=self.file_name[-3:]
		assert suffix == "asm","please choose an input file named like Xxx.asm"
		with open(file_path,'r') as file:
			for line in file:
				_line=line.strip()
				if len(_line)==0 or _line[0]=='/' :
					continue
				if _line.find('/') != -1:
					_line=_line[:_line.find('/')]
				self.codes.append(_line.strip())
	
	def process_label(self):
		"""
		first pass through the code to find label symbol like (Xxx)
		"""
		no_label_codes=[]
		curr_line=-1
		for line in self.codes:
			if line[0] == '(':
				self.sym_table[line[1:-1]]=curr_line+1
			else:
				no_label_codes.append(line)
				curr_line+=1
		self.codes=no_label_codes

	def parse(self):
		"""
		second pass through the codes to generate binary codes
		"""
		for line in self.codes:
			if line[0]=="@": # A-command
				self.binary_codes.append(self.A_command(line[1:]))
			else : # C-command
				self.binary_codes.append(self.C_command(line))

	def deci2bin(self,decimal):
		"""
		change the decimal into a binary with 16 width

		@param decimal(str):the decimal str to be changed into a binary str
		"""
		binary=bin(int(decimal))[2:] # bin(x) is like "0b010110"
		binary="0"*(16-len(binary))+binary 
		return binary

	def A_command(self,command):
		"""
		generate binary codes for A command which like @Xxx
		note that Xxx can be a symbol or a decimal

		@param command (str) : the A-command to be interpreted
		"""
		if command.isdecimal() :
			return self.deci2bin(command)
		elif self.sym_table.get(command) == None: # new variable
			binary=self.deci2bin(self.allo_address)
			self.sym_table[command]=self.allo_address
			self.allo_address+=1
			return binary
		else:
			address=self.sym_table.get(command)
			return self.deci2bin(address)

	def C_command(self,command):
		"""
		generate binary codes for C command which like dest=comp;jmp
		@param command (str) : the C-command to be interpreted	
		"""
		equal_loc=command.find("=")
		semicolon_loc=command.find(";")
		dest=""
		comp=""
		jmp=""
		if equal_loc == -1:
			dest="null"
		if semicolon_loc == -1:
			jmp="null"
			semicolon_loc=len(command)
		if len(dest) == 0:
			dest=command[:equal_loc]
		if len(jmp) == 0:
			jmp=command[semicolon_loc+1:]
		comp=command[equal_loc+1:semicolon_loc]
		binary="111"+self.comp_table[comp]+self.dest_table[dest]+self.jmp_table[jmp]
		return binary

	def save_binary(self):
		binary_filename=self.file_name[:-4]+".hack"
		with open(binary_filename,'w') as file:
			for line in self.binary_codes:
				file.write(line+'\n')


def main():
	file_path=sys.argv[1]
	ass=Assembler(file_path)
	ass.process_label()
	ass.parse()
	ass.save_binary()

if __name__ == '__main__':
	main()