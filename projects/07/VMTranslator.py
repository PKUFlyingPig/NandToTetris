import os
import sys

class VMTranslator:
	""" 
	translate a .vm file into a .asm file which contains assembly code for hack machine
	"""
	def __init__(self, file_path):
		"""
		open the file & filter the blanks and comments
		@attr self.vm_filename (str): input file
		@attr self.asm_filename (str): output file
		@attr self.rela_path (str): relative path for the output_file
		@attr self.codes (list of str): a list contains clean vm code with no blank or comments
		@attr self.asm_codes(list of str): a list contains assembly codes generated from self.codes
		"""
		super(VMTranslator,self).__init__()
		self.vm_filename=os.path.basename(file_path)
		self.rela_path=file_path[:-len(self.vm_filename)]
		suffix=self.vm_filename[self.vm_filename.find(".")+1:]
		assert suffix == "vm","please choose an input file named xxx.vm"
		self.asm_filename=self.vm_filename[:-3]+".asm"
		self.codes=[]
		self.asm_codes=[]
		self.arith_dict={
		"not":"!","neg":"-","add":"+","sub":"-","and":"&","or":"|",
		"eq":"JNE","lt":"JGE","gt":"JLE",
		}
		self.mapping={
		"local":"LCL","argument":"ARG","this":"THIS","that":"THAT",
		"temp":"5","pointer":"3",
		}
		self.symbol_index=0
		with open(file_path,'r') as file:
			for line in file:
				_line=line.strip()
				if len(_line)==0 or _line[0]=='/' :
					continue
				if _line.find('/') != -1:
					_line=_line[:_line.find('/')]
				self.codes.append(_line.strip())

	def parse(self):
		"""
		for each line in self.codes, generate its corresponding assembly codes
		"""
		for code in self.codes:
			part=code.split()
			if len(part)==1: # arithmetic commands
				self.asm_codes+=self.C_arith(part[0])
			elif part[0]=="push": # push command
				self.asm_codes+=self.C_push(part[1:])
			elif part[0]=="pop": # pop command
				self.asm_codes+=self.C_pop(part[1:])

	def C_arith(self,command):
		"""
		generate assembly codes for arithmetic commands
		@para command (str): the arithmetic command to be translated
		"""
		if command in ["not","neg"]: # one argument command
			spec="M="+self.arith_dict[command]+"M"
			asm_code=["@SP","A=M-1",spec]
		elif command in ["add","sub","and","or"]:
			spec="M=M"+self.arith_dict[command]+"D"
			asm_code=["@SP","AM=M-1","D=M","A=A-1",spec]
		elif command in ["eq","gt","lt"]:
			symbol=command+"_"+str(self.symbol_index)
			symbol1="@"+symbol
			symbol2="("+symbol+")"
			spec="D;"+self.arith_dict[command]
			asm_code=["@SP","AM=M-1","D=M","A=A-1","D=M-D","M=0",symbol1,spec,"@SP","A=M-1","M=-1",symbol2]
			self.symbol_index+=1

		return asm_code
	def C_push(self,command):
		"""
		generate assembly codes for push commands
		@para command (list of str): the push command to be translated
		"""
		# put the value which will be pushed into the stack in D
		asm_code=[]
		if command[0]=="constant":
			asm_code=["@"+command[1],"D=A"]
		elif command[0] in ["local","argument","this","that"]:
			asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"A=M+D","D=M"]
		elif command[0] in ["temp","pointer"]:
			asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"A=A+D","D=M"]
		elif command[0] == "static":
			symbol="@"+self.vm_filename[:-3]+"."+command[1]
			asm_code=[symbol,"D=M"]

		# put the value in D into *SP, then SP++
		return asm_code+["@SP","A=M","M=D","@SP","M=M+1"]

	def C_pop(self,command):
		"""
		generate assembly codes for pop commands
		@para command (list of str): the pop command to be translated
		"""
		#compute the address 
		if command[0] in ["local","argument","this","that"]:
			asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"D=M+D","@R15","M=D"]
		elif command[0] in ["temp","pointer"]:
			asm_code=["@"+command[1],"D=A","@"+self.mapping[command[0]],"D=A+D","@R15","M=D"]
		elif command[0] == "static":
			symbol="@"+self.vm_filename[:-3]+"."+command[1]
			asm_code=[symbol,"D=M","@R15","M=D"]

		# put the value *SP into M[address],then SP--
		return asm_code+["@SP","AM=M-1","D=M","@R15","A=M","M=D"]

	def save_file(self):
		"""
		save self.asm_codes into Xxx.asm file
		"""
		output_path=os.path.join(self.rela_path,self.asm_filename)
		with open(output_path,'w') as file:
			for line in self.asm_codes:
				file.write(line+'\n')

def main():
	file_path=sys.argv[1]
	vmtranslator=VMTranslator(file_path)
	vmtranslator.parse()
	vmtranslator.save_file()
	for line in vmtranslator.asm_codes:
		print(line)
if __name__ == '__main__':
	main()