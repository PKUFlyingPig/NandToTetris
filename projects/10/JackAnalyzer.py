import sys
import os
import re

class Token:
	"""
	jack token
	"""
	def __init__(self, category, value):
		self.value = value
		self.t = category
		self.is_terminal = True
		if value == '<':
			self.form = "<" + category + "> &lt; </" + category + ">"
		elif value == '>':
			self.form = "<" + category + "> &gt; </" + category + ">"
		elif value == '&':
			self.form = "<" + category + "> &amp; </" + category + ">"
		else:
			self.form = "<" + category + "> " + value + " </" + category + ">"

class UnTerminalToken:
	"""
	jack unterminal token
	"""
	def __init__(self, value, isbegin):
		self.value = value
		self.is_terminal = False

		if isbegin:
			self.form = '<' + value + '>'
		else:
			self.form = '</' + value + '>'

class JackTokenizer:
	"""
	filter the input Xxx.jack file into tokens
	"""
	def __init__(self,file_name):
		"""
		@attr self.tokens (list of Token): contain all the tokens
		@attr self.codes (list of str): jack codes with no comments or blank
		@attr self.keywords (set): jack keywords set
		@attr self.symbols (set): jack symbols set
		"""
		self.tokens = []
		self.codes = []
		self.strings = []
		self.index = 0
		self.keywords = ['class', 'constructor', 'function', 
		'method', 'field', 'static', 'var', 'int', 'char',
		'boolean', 'void', 'true', 'false', 'null', 'this',
		'let', 'do', 'if', 'else', 'while', 'return']
		self.symbols = ['{', '}', '(', ')', '[', ']', '.',',',
		 ';', '+', '-', '*', '/', '&', '|', '<', '>','=', '~']

		assert file_name[-4:] == "jack", "the input file must be Xxx.jack"
		self.file_name = file_name[:-5]

		with open(file_name) as file:
			multi_comments = False
			for line in file:
				_line=line.strip()
				if multi_comments:
					if  _line.find('*/') == -1:
						continue
					_line = _line[_line.find('*/')+2 : ]
					multi_comments = False
					continue
				if len(_line) == 0 or _line[:2] == '//' :
					continue
				if _line.find('//') != -1:
					_line = _line[:_line.find('//')]
				if _line.find('/*') != -1:
					s = _line.find('/*')
					t = _line.find('*/')
					if t == -1:
						multi_comments = True
						_line = _line[:s]
					else:
						_line = _line[:s] + _line[t+2:]
				self.codes.append((_line.strip()))

	def tockenize(self):
		""""""
		self.strings = []
		self.index = 0
		for code in self.codes:
			if code.find('\"') != -1 :
				s = code.find('\"')
				e = s + 1 + code[s + 1:].find('\"')
				self.strings.append(code[s + 1:e])
				code = code[:s] + code[e:]
			tmp = code.split()
			for x in tmp:
				self.handle_code(x)

	def handle_code(self, code):
		if code[0] in self.symbols:
			self.tokens.append(Token("symbol", code[0]))
			if len(code) == 1:
				return
			self.handle_code(code[1:])
		elif code[0] == '\"':
			self.tokens.append(Token("stringConstant", self.strings[self.index]))
			self.index += 1
			if len(code) == 1:
				return	
			self.handle_code(code[1:])
		elif code[0].isdecimal():
			integer = code
			for i,s in enumerate(code[1:],1):
				if s.isdecimal() == False:
					integer = code[:i]
					break
			self.tokens.append(Token("integerConstant", integer))
			if len(integer) == len(code):
				return
			self.handle_code(code[len(integer):])
		else:
			iskeyword = False
			for keyword in self.keywords:
				if code.find(keyword) == 0:
					self.tokens.append(Token("keyword", keyword))
					if len(keyword) == len(code):
						return
					self.handle_code(code[len(keyword):])
					iskeyword = True
					break

			if iskeyword:
				return
			identifier = code
			for i,s in enumerate(code):
				if s in self.symbols:
					identifier = code[:i]
					break
			self.tokens.append(Token("identifier", identifier))
			if len(identifier) == len(code):
				return 
			self.handle_code(code[len(identifier):])

	def save_tokenfile(self):
		with open(self.file_name+'TT.xml','w') as file:
			file.write("<tokens>\n")
			for token in self.tokens:
				file.write(token.form+'\n')
			file.write("</tokens>")

class CompilationEngine:
	"""
	"""
	def __init__(self, tokens, output_file):
		self.tokens = tokens
		self.output_file = output_file
		self.tot = len(self.tokens)
		self.completeTokens = []
		self.cur_loc = 0
		self.classDec = ['static', 'field']
		self.funcDec = ['constructor', 'function', 'method']
		self.statements = ['let', 'if', 'while', 'do', 'return']
		self.op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
		self.unary_op =['-', '~']
		
	def run(self):
		self.completeTokens = []
		self.cur_loc = 0
		self.CompileClass()

	def next(self):
		if self.cur_loc >= self.tot:
			return None
		nex = self.tokens[self.cur_loc]
		self.cur_loc += 1
		return nex

	def peek(self):
		if self.cur_loc >= self.tot:
			return None
		nex = self.tokens[self.cur_loc]
		return nex

	def add(self, token):
		self.completeTokens.append(token)

	def CompileClass(self):
		self.add(UnTerminalToken('class', True)) # <class>
		self.add(self.next()) # class
		self.add(self.next()) # className
		self.add(self.next()) # {
		while self.peek().value in self.classDec:
			self.CompileClassVarDec()
		while self.peek().value in self.funcDec:
			self.CompileSubroutine()
		self.add(self.next()) # }
		self.add(UnTerminalToken('class', False)) # </class>

	def CompileClassVarDec(self):
		self.add(UnTerminalToken('classVarDec', True)) 
		self.add(self.next()) # (static | field)
		self.add(self.next()) # type
		self.add(self.next()) # varName
		while self.peek().value == ',':
			self.add(self.next()) # ,
			self.add(self.next()) # varName
		self.add(self.next()) # ;
		self.add(UnTerminalToken('classVarDec', False))

	def CompileSubroutine(self):
		self.add(UnTerminalToken('subroutineDec', True))
		self.add(self.next()) # (constructor | function | method)
		self.add(self.next()) # (void | type)
		self.add(self.next()) # subroutineName
		self.add(self.next()) # '('
		self.CompileParameterList()
		self.add(self.next()) # ')'
		self.add(UnTerminalToken('subroutineBody', True))
		self.add(self.next()) # '{'
		while self.peek().value == 'var':
			self.CompileVarDec()
		self.CompileStatements()
		self.add(self.next()) # '}'
		self.add(UnTerminalToken('subroutineBody', False))
		self.add(UnTerminalToken('subroutineDec', False))

	def CompileParameterList(self):
		self.add(UnTerminalToken('parameterList', True))
		if self.peek().value != ')':
			self.add(self.next()) # type
			self.add(self.next()) # varName
		while self.peek().value == ',':
			self.add(self.next()) # ,
			self.add(self.next()) # type
			self.add(self.next()) # varName
		self.add(UnTerminalToken('parameterList', False))

	def CompileVarDec(self):
		self.add(UnTerminalToken('varDec', True))
		self.add(self.next()) # var
		self.add(self.next()) # type
		self.add(self.next()) # varName
		while self.peek().value == ',':
			self.add(self.next()) # ,
			self.add(self.next()) # varName
		self.add(self.next()) # ;
		self.add(UnTerminalToken('varDec', False))

	def CompileStatements(self):
		self.add(UnTerminalToken('statements', True))
		while self.peek().value in self.statements:
			v = self.peek().value
			if v == 'if':
				self.CompileIf() 
			elif v == 'let':
				self.CompileLet()
			elif v == 'while':
				self.CompileWhile()
			elif v == 'do':
				self.CompileDo()
			else:
				self.CompileReturn()
		self.add(UnTerminalToken('statements', False))

	def CompileDo(self):
		self.add(UnTerminalToken('doStatement', True))
		self.add(self.next()) # do
		self.add(self.next()) # subroutineCall
		if self.peek().value == '(':
			self.add(self.next()) # '('
			self.CompileExpressionList()
			self.add(self.next()) # ')'
		elif self.peek().value == '.':
			self.add(self.next()) # '.'
			self.add(self.next()) # subroutineName
			self.add(self.next()) # (
			self.CompileExpressionList()
			self.add(self.next()) # )
		self.add(self.next()) # ;
		self.add(UnTerminalToken('doStatement', False))

	def CompileLet(self):
		self.add(UnTerminalToken('letStatement', True))
		self.add(self.next()) # let
		self.add(self.next()) # varName
		if self.peek().value == '[':
			self.add(self.next()) # '['
			self.CompileExpression()
			self.add(self.next()) # ']'
		self.add(self.next()) # =
		self.CompileExpression()
		self.add(self.next()) # ;
		self.add(UnTerminalToken('letStatement', False))

	def CompileWhile(self):
		self.add(UnTerminalToken('whileStatement', True))
		self.add(self.next()) # while
		self.add(self.next()) # (
		self.CompileExpression()
		self.add(self.next()) # )
		self.add(self.next()) # {
		self.CompileStatements()
		self.add(self.next()) # }
		self.add(UnTerminalToken('whileStatement', False))

	def CompileReturn(self):
		self.add(UnTerminalToken('returnStatement', True))
		self.add(self.next()) # return
		if self.peek().value != ';':
			self.CompileExpression()
		self.add(self.next()) # ;
		self.add(UnTerminalToken('returnStatement', False))

	def CompileIf(self):
		self.add(UnTerminalToken('ifStatement', True))
		self.add(self.next()) # if
		self.add(self.next()) # (
		self.CompileExpression()
		self.add(self.next()) # )
		self.add(self.next()) # {
		self.CompileStatements()
		self.add(self.next()) # }
		if self.peek().value == 'else':
			self.add(self.next()) # else
			self.add(self.next()) # {
			self.CompileStatements()
			self.add(self.next()) # }
		self.add(UnTerminalToken('ifStatement', False))

	def CompileExpression(self):
		self.add(UnTerminalToken('expression', True))
		self.CompileTerm()
		while self.peek().value in self.op:
			self.add(self.next()) # op
			self.CompileTerm()
		self.add(UnTerminalToken('expression', False))

	def CompileTerm(self):
		self.add(UnTerminalToken('term', True))	
		if self.peek().value == '(':
			self.add(self.next()) # (
			self.CompileExpression()
			self.add(self.next()) # )
		elif self.peek().value in self.unary_op:
			self.add(self.next()) # - or ~
			self.CompileTerm()
		else:
			self.add(self.next())
			if self.peek().value == '[':
				self.add(self.next()) # '['
				self.CompileExpression()
				self.add(self.next()) # ']'
			elif self.peek().value == '(':
				self.add(self.next()) # '('
				self.CompileExpressionList()
				self.add(self.next()) # ')'
			elif self.peek().value == '.':
				self.add(self.next()) # '.'
				self.add(self.next()) # subroutineName
				self.add(self.next()) # (
				self.CompileExpressionList()
				self.add(self.next()) # )
		self.add(UnTerminalToken('term', False))

	def CompileExpressionList(self):
		self.add(UnTerminalToken('expressionList', True))
		if self.peek().value != ')':
			self.CompileExpression()
			while self.peek().value == ',':
				self.add(self.next()) # ,
				self.CompileExpression()
		self.add(UnTerminalToken('expressionList', False))

	def save_file(self):
		with open(self.output_file, 'w') as file:
			for x in self.completeTokens:
				file.write(x.form + '\n')

class JackAnalyzer:
	"""
	JackAnalyzer is the first part of JackCompiler
	
	Its work contains three parts as follows:
	1. create a JackTokenizer according to the input Xxx.jack file
	2. use CompilationEngine to translate the tokens into grammatical tree
	3. output the Xxx.xml file
	"""
	def __init__(self, input_file):
		assert input_file[-4:] == "jack", "the input file must be Xxx.jack"
		self.input_file = input_file
		self.file_name = input_file[:-5]
		self.output_file = self.file_name + '1.xml'

	def analyze(self):
		tokenizer = JackTokenizer(self.input_file)
		tokenizer.tockenize()
		compileEngine = CompilationEngine(tokenizer.tokens, self.output_file)
		compileEngine.run()
		compileEngine.save_file()


def main():
	file = sys.argv[1]
	JackAnalyzer(file).analyze()

if __name__ == '__main__':
	main()