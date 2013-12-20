query-phamerator
==========
1. Introduction
----------
Phamerator is a tool created and maintained by Dr. Steve Cresawn of James Madison Univeristy. Phamerator provides provides useful tools for comparative analysis of mycobacteriophage genomes stored in a MySQL database<sup>1</sup>. One feature Phamerator does not include is the ability to retreive the sequences of specific genes from this databse. query-phamerator is an add on script designed to provide this feature by retrieving sequence information from this database and storing it in FASTA files.

2. Design
----------
**2.1 Program information and requirements**

query-phamerator is written in Python 2.7 and depends on the following packages:
- MySQLdb <sup>2</sup>
- BioPython <sup>3</sup>
- pygtk <sup>4</sup>

All other packages used are found in the standard library. The script is found in `query_phamerator.py`.

**2.2 Phamerator database structure**

Phamerator uses a MySQL database which holds gene information of more than 400 phages. This data is organized into 10 tables of which query-phamerator accesses 3: `gene`, `phage`, and `pham`. As expected, `gene` holds information about genes, `phage` holds information about the phages, and `pham` holds information about the phams. 

Each phage is given a unique ID when added to the database which can be used to cross-reference information from different tables. This ID is stored in the column `PhageID` in both `gene` and `phage`. Similarly, each gene added to the database is given a unique ID which is stored in the column `GeneID` in `gene` and `pham`. These two columns are the only columns consistent among the tables. 

`gene` contains 

3. References
----------
1. Cresawn, Steven G., Matt Bogel, Nathan Day, Deborah Jacobs-Sera, Roger W. Hendrix, and Graham F. Hatfull. 2011. “Phamerator: A Bioinformatic Tool for Comparative Bacteriophage Genomics.” BMC Bioinformatics 12 (1) (October 12): 395. doi:10.1186/1471-2105-12-395.
2. http://mysql-python.sourceforge.net/
3. http://biopython.org/wiki/Main_Page
4. http://pygtk.org/
