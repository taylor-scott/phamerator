#Copyright (C) <year> <copyright holders>

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in 
#the Software without restriction, including without limitation the rights to 
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
#of the Software, and to permit persons to whom the Software is furnished to do 
#so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all 
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

#!/usr/bin/env python
import os,time,sys,argparse
from datetime import datetime
import MySQLdb as mysql
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import pygtk
import gtk
pygtk.require("2.0")

db = mysql.connect(host='localhost',user='root',passwd='phage',db='Mycobacteriophage_Draft')

class Query:
	"""Class for searching for retrieving FASTA files for phamerator queries.

	Methods:
	disp_query
	main_menu
	menu_options
	log
	make_fasta_files
	get_gene_list
	start

	"""
	def __init__(self, q_id=None, phages=None,clusters=None,phams=None,aa=0,o=True):
		if q_id is None:
			q_id = time.time()

		if phages is None:
			phages = []

		if clusters is None:
			clusters = []

		if phams is None:
			phams = []

		self.id = q_id
		self.phages = phages
		self.clusters = clusters
		self.phams = phams
		self.aa = aa
		self.o=o
		#self.gene_list (populated by self.get_gene_list()) is a dictionary of the format {<PhageID or pham#>:[<list of GeneIDs>]}
		self.gene_list={}
		#User organization preference
		self.organization=0
		self.fasta_directory = os.path.join("FASTA-files",str(self.id))
		self.written_fastas="Root directory: %s\n"%self.fasta_directory
		#Basic logging
		self.log("Query started.")

	def __str__(self):
		return "Query ID: %s,phages=%s,clusters=%s,phams=%s,aa=%s,o=%s"%(self.id,self.phages,self.clusters,self.phams,self.aa,self.o)

	def log(self,logtext):
		"""Write text to log file.

		Arguments:
		'logtext' (str) (required) The text to be logged.

		"""
		if not os.path.exists("FASTA-files"): os.makedirs("FASTA-files")
		if not os.path.exists(os.path.join("FASTA-files","logs")): os.makedirs(os.path.join("FASTA-files","logs"))	
		f = open(os.path.join("FASTA-files","logs","%s.txt"%self.id),"a")
		dtime = datetime.now().strftime("%Y-%M-%d %H:%m:%S")
		#Logs are of the format [Timestamp] Query id: Log text
		log = "[%s] %s: %s\n" % (dtime,self.id,logtext)
		f.write(log)
		f.close()

	def make_fasta_files(self):
		"""Write gene information to FASTA files"""
		#Create a database instance
		cursor = db.cursor()
		#Create directory "FASTA-files" if it does not already exist
		if not os.path.exists("FASTA-files"): os.makedirs("FASTA-files")
		#Convert the id to a string
		id_str = str(self.id)
		#Create directory <id_str> if it does not already exist
		if not os.path.exists(os.path.join("FASTA-files",id_str)):os.makedirs(os.path.join("FASTA-files",id_str))
		#The FASTA files will be output to "FASTA-files/<id_str>"

		#Iterate through <self.gene_list> (generated by self.get_gene_list())
		for name,gene_list in self.gene_list.items():
			#Create a local list to store  gene information
			recs=[]
			if self.o==True:
				#Retrieve cluster information if necessary
				query = "SELECT Cluster FROM phage WHERE name='%s'"%name
				self.log("Query executed: %s"%query)
				cursor.execute(query)
				cluster = cursor.fetchone()[0]
				cluster = "Singleton" if cluster==None else cluster
			#Iterate through list of genes
			for g in gene_list:
				if self.aa != 0:
					#Unlike amino acid sequences, nucleotide sequences for genes are not stored in the 'gene' table. The phage's nucleotide sequence must be retrieved. Sequences for specific genes are extracted using the start and stop codon values stored in the 'gene' table
					query = "SELECT sequence FROM phage WHERE PhageID=ANY(SELECT DISTINCT(PhageID) FROM gene WHERE GENEID='%s')"%g
					self.log("Query executed: %s"%query)
					cursor.execute(query)
					n_seq = cursor.fetchone()[0]
				#Retrieve the PhageID, gene name, start position, stop position, start codon, stop codon, orientation, and amino acid sequence for each gene in <gene_list>. 
				query = "SELECT PhageID,Name,Start,Stop,StartCodon,StopCodon,Orientation,Translation FROM gene WHERE GeneID='%s'"%g
				self.log("Query executed: %s"%query)
				cursor.execute(query)
				#Iterate through the results
				for r in cursor.fetchall():
					if self.aa == 0:
						#Store amino acid sequence as 'Seq' type from BioPython. 
						seq = Seq(r[7],IUPAC.protein)
						#Record information about the gene, including the gene id, the phage name (PhageID), and a basic description.
						this_rec=SeqRecord(seq,id="%s|"%(r[1]),name=r[0],description="Amino acid sequence of gene %s from phage %s|%s|%s|%s"%(r[1],r[0],r[6],r[2],r[3]))
					else:
						#Store nucleotide sequence as 'Seq' type from BioPython. <r[2]> and <r[3]> reference the start and stop positions of the gene. 
						seq = Seq(n_seq[r[2]:r[3]],IUPAC.unambiguous_dna)
						#Corrects nucleotide sequence of genes that overlap the origin of replication
						if r[2]>r[3]:
							seq = Seq(n_seq[r[2]:]+n_seq[:r[3]], IUPAC.unambiguous_dna)
						#Transcribe the sequence if searching for RNA sequences
						if self.aa == 2:
							seq = seq.transcribe()
						#Build  record
						if r[6]=="F":
							this_rec=SeqRecord(seq,id="%s|"%(r[1]),name=r[0],description="Nucleotide sequence of gene %s from %s|%s|%s|%s"%(r[1],r[0],r[6],r[2],r[3]))
						#Translate the gene if it is a reverse gene
						elif r[6]=="R":
							this_rec=SeqRecord(seq.reverse_complement(),id="%s|"%(r[1]),name=r[0],description="Nucleotide sequence of gene %s from %s|%s|%s|%s"%(r[1],r[0],r[6],r[2],r[3]))
					#Append the current <this_rec> to the list of <recs> for the current phage or pham (<p>)
					recs.append(this_rec)
			#Organized by phage
			if self.o==True:
				#Create folder structure. FASTA files will be stored in 'FASTA-files/<cluster>/(<subcluster>/)<name>.fasta'			
				if cluster == 'Singleton':
					if not os.path.exists(os.path.join("FASTA-files",id_str,'Singleton')):os.makedirs(os.path.join("FASTA-files",id_str,"Singleton"))
					file_name = os.path.join("FASTA-files",id_str,"Singleton","%s.fasta"%name)
				else:
					if not os.path.exists(os.path.join("FASTA-files",id_str,cluster[0])):os.makedirs(os.path.join("FASTA-files",id_str,cluster[0]))
					if len(cluster)>1:
						if not os.path.exists(os.path.join("FASTA-files",id_str,cluster[0],cluster)):os.makedirs(os.path.join("FASTA-files",id_str,cluster[0],cluster))
						#The filename and path for the phage's fasta file
						file_name = os.path.join(cluster[0],cluster,"%s.fasta"%name)
					else:
						file_name = os.path.join(cluster[0],"%s.fasta"%name)
				#Write the gene information to a fasta file. SeqIO.write() returns an int of the number of genes recorded.
				write_fasta = SeqIO.write(recs,os.path.join(self.fasta_directory,file_name),"fasta")
				#Tell the user where to find the fasta file and how many genes were recorded
				self.written_fastas += "Phage %s's FASTA file created in %s. %s genes logged\n"%(name,file_name,write_fasta)
			#Organized by pham
			else:
				#Filename and path for the pham's fasta file
				file_name = "%s.fasta"%name
				write_fasta = SeqIO.write(recs,os.path.join(self.fasta_directory,file_name),"fasta")
				self.written_fastas += "Pham %s's FASTA file created in %s. %s genes logged\n"%(name,file_name,write_fasta)
	def get_gene_list(self):
		#Should the results be sorted by phage or by pham?
		#try:
		#	self.o = not bool(int(raw_input("[0] Phage\n[1] Pham\nOrder FASTA files by: ")))
		#except ValueError as error:
		#	print "Sorry, you have entered an invalid option. Please try again."
		#	self.log("Error: %s"%error)
		#	self.get_gene_list()
		#except Exception as error:
		#	print "Sorry an unexpected error has occured. Please restart the program and try again. The error has been logged."
		#	self.log("ERROR: %s"%error)			
		#Begin to build query. Will return a list of PhageIDs
		query = "SELECT DISTINCT(PhageID),cluster,name FROM phage"
		#Expand cluster list into list of subclusters
		cursor = db.cursor()
		cluster_list = []
		if len(self.clusters)>0:
			query += " WHERE "
			for c in self.clusters:
				if c != "Singleton":
					#Search for all clusters that are similar to each user defined cluster (e.g. 'F' becomes ['F1','F2'])
					c_query = "SELECT DISTINCT(Cluster) FROM phage WHERE Cluster LIKE '{}%'".format(c)
					self.log("Query executed: %s"%c_query)
					cursor.execute(c_query)
					results = cursor.fetchall()
					#Iterate over the retrieved subclusters
					for i in results:
						#Add results to a new list of clusters and subclusters if they do not already exist
						cluster_list.append(i[0])
			cluster_list = set(cluster_list)
			if len(cluster_list)>0:
				#Accounts for quirk in tuple->str conversion: str(('x')) = 'x'. str(('x','y')) = "('x','y')"
				cluster_list=tuple(cluster_list)
				if len(cluster_list)==1:
					cluster_list="('%s')"%cluster_list[0]
				elif len(cluster_list)>1:
					cluster_list=str(cluster_list)
				#Add cluster parameters to query
				query += "Cluster IN %s"%cluster_list

		if "Singleton" in self.clusters:
			if len(cluster_list)>0:
				query += "OR "
			#Singletons are stored in the 'phage' table with a NULL value in the 'cluster' column.
			query += "cluster IS NULL"

		if len(self.phages)>0 and len(self.clusters)>0:
			query += " OR "
		elif len(self.phages)>0 and len(self.clusters)==0:
			query += " WHERE "
		#Add phage parameters to query
		if len(self.phages)==1:
				query += "Name='%s'"%self.phages[0]
		elif len(self.phages)>1:
				query += "Name IN %s"%str(tuple(self.phages))
		self.log("Executed query: %s" % query)
		cursor.execute(query)
		#Iterate through results. Will retrieve list of genes for each PhageID returned with the previous query
		for r in cursor.fetchall():
			#Store cluster information in a local variable
			cluster = "Singleton" if r[1] is None else r[1]
			#Begin building query. Will return a list of GeneIDs
			query = "SELECT GeneID,pham.name FROM gene JOIN pham USING (GeneID) WHERE PhageID='%s'"%r[0]
			if len(self.phams)==1:
				query += " AND pham.name='%s'"%self.phams[0]
			elif len(self.phams)>1:
				query += " AND pham.name IN %s"%str(tuple(self.phams))
			#Order genes by start position
			query += " ORDER BY start"
			self.log("Executed query: %s"%query)
			cursor.execute(query)
			#Iterate through the list of GeneIDs
			for g in cursor.fetchall():
				#If organizing by phage
				if self.o is True:
					#Store a list of genes as a dictionary value corresponding to the appropriate dictionary key. <r[0]> corresponds to the name of the phage
					if r[2] in self.gene_list:
						self.gene_list[r[2]].append(g[0])
					else:
						self.gene_list[r[2]]=[g[0]]
				#If organizing by pham		
				else:
					#Store a list of genes a a dictionary value corresponding to the appropriate dictionary key <g[1]> corresponds to the pham number
					if g[1] in self.gene_list:
						self.gene_list[g[1]].append(g[0])
					else:
						self.gene_list[g[1]]=[g[0]]

		#Close database connection
		cursor.close()
		return True
		#Create the FASTA files
		#try:
		#	self.make_fasta_files()
		#except Exception as error:
		#	print "Sorry an unexpected error has occured. Please restart the program and try again. The error has been logged."
		#	self.log("ERROR: %s"%error)
		#	raise

class gtkMain:
	def __init__(self):
		glade = "test2.glade"
		self.builder = gtk.Builder()
		self.builder.add_from_file(glade)
		self.window = self.builder.get_object("window1")
		#phageList = builder.get_object("allPhageList")
		#for phage in phage_list:
		#	phageList.append(phage)

		dic = {"on_window1_destroy":gtk.main_quit,"on_cancelButton_clicked":gtk.main_quit,"on_searchButton_clicked":self.search}
		self.builder.connect_signals(dic)
		self.window.show_all()

	def search(self,widget):
		dialog = gtk.Dialog("Searching",self.window,gtk.DIALOG_MODAL)
		dialog.set_deletable(False)
		dialog.set_default_size(300,150)
		progressLabel = gtk.Label("<b><span size='12000'>Searching</span></b>")
		progressLabel.set_use_markup(True)
		dialog.vbox.pack_start(progressLabel)
		
		dialog.show_all()
		while gtk.events_pending():
   			gtk.main_iteration(False)
		phageEntry = self.builder.get_object("phageEntry")
		clusterEntry = self.builder.get_object("clusterEntry")
		phamEntry = self.builder.get_object("phamEntry")
		aaRadio = [radio.get_active() for radio in self.builder.get_object("aaRadio").get_group()][::-1].index(True)
		oRadio = self.builder.get_object("organizeFiles").get_active()

		phageList = filter(None,[param.strip() for param in phageEntry.get_text().split(",")])
		clusterList = filter(None,[param.strip() for param in clusterEntry.get_text().split(",")])
		phamList = filter(None,[param.strip() for param in phamEntry.get_text().split(",")])

		query = Query(phages=phageList,clusters=clusterList,phams=phamList,aa=aaRadio,o=oRadio)
		print query
		query.get_gene_list()
		query.make_fasta_files()

		dialog.set_deletable(True)
		progressLabel.set_text("<b><span size='12000'>Search Complete</span></b>")
		progressLabel.set_use_markup(True)
		textBuffer = gtk.TextBuffer()
		textBuffer.set_text(query.written_fastas)
		textView = gtk.TextView(buffer=textBuffer)
		textView.set_editable(False)

		scrolledWindow = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolledWindow.add_with_viewport(textView)
		dialog.vbox.pack_start(scrolledWindow)
		dialog.show_all()

		


if __name__ == "__main__":
	mainWindow = gtkMain()
	gtk.main()