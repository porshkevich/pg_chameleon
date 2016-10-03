import re
import json
import sqlparse
from sqlparse.sql import Identifier
from sqlparse.tokens import Keyword, DDL

class sql_utility:
	"""
	Class sql_utility. Tokenise the sql statements captured by the mysql replication.
	Each statement is converted in dictionary being used by pg_engine.
	"""
	def __init__(self):
		self.statements=[]
		self.query_list=[]
		#re for query elements
		self.m_pkeys=re.compile(r'\w*(primary)\s*key', re.IGNORECASE)
		self.m_ukeys=re.compile(r'\w*(unique)\s*key', re.IGNORECASE)
		self.m_idx=re.compile(r'(key)|(unique)?\s*(index)', re.IGNORECASE)
		self.m_fkeys=re.compile(r'(constraint)?\n*\s*\w*\s*foreign key', re.IGNORECASE)
		self.m_nulls=re.compile(r'(not)?\s*(null)', re.IGNORECASE)
		self.m_autoinc=re.compile(r'(auto_increment)', re.IGNORECASE)
		
		#re for query type
		self.m_create=re.compile(r'\s*(create\s*table|index)\s*', re.IGNORECASE)
		
		
	
	def parse_column(self, col_def):
		col_dic={}
		col_list=col_def.split()
		if len(col_list)>1:
			col_dic["name"]=col_list[0]
			col_dic["type"]=col_list[1]
			nullcons=self.m_nulls.search(col_def)
			autoinc=self.m_autoinc.search(col_def)
			if nullcons:
				col_dic["null"]=nullcons.group(0)
			if autoinc:
				col_dic["autoinc"]="true"
		return col_dic
		
	def parse_group(self, token_dic):
		column_group=token_dic["group"]
		column_parsed=[]
		key_list=[]
		for column in column_group:
			column=re.sub(r'[\n]', '', column)
			column_list=column.split(',')
			for col_def in column_list:
				col_def=col_def.strip('(').strip()
				pkey=self.m_pkeys.match(col_def)
				ukey=self.m_ukeys.match(col_def)
				fkey=self.m_fkeys.match(col_def)
				idx=self.m_idx.match(col_def)
				"""if pkey:
					print "matched primary key: "+col_def
					print col_def
				elif ukey:
					print "matched unique key: "+col_def
				elif fkey:
					print "matched foreign key: "+col_def
				elif idx:
					print "matched index key: "+col_def
				else:"""
					#print "column definition: "+col_def
				col_dic=self.parse_column(col_def)
				if len(col_dic)>0:
					column_parsed.append(col_dic)
		return column_parsed
				

	def collect_tokens(self, tokens):
		token_dic={}
		group_list=[]
		for token in tokens:
			if token.is_whitespace():
				pass
			elif token.ttype is Keyword:
				pass
			elif token.ttype==None:
				if isinstance(token, Identifier):
					token_dic["identifier"]=token.value
				elif token.is_group():
					group_list.append(token.value)
		token_dic["group"]=group_list
		token_dic["group"]=self.parse_group(token_dic)
		return token_dic
		
	
	def parse_sql(self, sql_string):
		"""
			Splits the sql string in statements using the conventional end of statement marker ;
			A regular expression greps the words and parentesis and a split converts them in
			a list. Each list of words is then stored in the list token_list.
			
			:param sql_string: The sql string with the sql statements.
		"""
		self.statements=sqlparse.split(sql_string)
		for statement in self.statements:
			token_dic={}
			stat_cleanup=re.sub(r'/\*.*?\*/', '', statement, re.DOTALL)
			stat_cleanup=re.sub(r'--.*?\n', '', stat_cleanup)
			stat_cleanup=re.sub(r'[\b)\b]', ' ) ', stat_cleanup)
			stat_cleanup=re.sub(r'[\b(\b]', ' ( ', stat_cleanup)
			stat_cleanup=re.sub(r'[\b,\b]', ', ', stat_cleanup)
			stat_cleanup=re.sub(r'\n*', '', stat_cleanup)
			sql_clean=re.sub("\([\w*\s*]\)", " ",  stat_cleanup)
			parsed = sqlparse.parse(sql_clean)
			print sql_clean
			m=re.match(r'[^\w][(][)]', sql_clean, re.IGNORECASE)
			print m.groups()
			"""
			if len(parsed)>0:
				try:
					mcreate=self.m_create.match(sql_clean)
					command=mcreate.group(0)
					token_dic=self.collect_tokens(parsed[0])
					token_dic["command"]=command
					self.query_list.append(token_dic)
				except:
					pass
			"""
				
