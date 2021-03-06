import re

def compile(sqssFile, variablesFile):

	#with open(variablesFile, 'r') as variables, open(sqssFile, 'r') as sqss, open(qssFile, 'w') as outputFile:

	with open(variablesFile, 'r') as variables, open(sqssFile, 'r') as sqss:
		output = sqss.read()
		lines = variables.readlines()

		for line in lines:
			# skip empty lines
			if not line.strip():
				continue

			splits = line.split(':')
			key = splits[0].strip() + ';'	# this prevent $grey being confused with $grey-dark but means the variable must be followed by a semi-colon
			value = splits[1].strip()

			# remove lines that start with a comment //
			output = re.sub(re.compile("//.*?\n" ) ,"" , output)
			# remove all occurance streamed comments (/*COMMENT */) from string
			output = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,output) 
			# replace variable found in line
			output = output.replace(key,value)

		print output
		return output

