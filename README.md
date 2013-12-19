query-phamerator
==========
1. Introduction
----------
Phamerator is a tool created and maintained by Dr. Steve Cresawn of James Madison Univeristy. Phamerator provides provides useful tools for comparative analysis of mycobacteriophage genomes stored in a MySQL database (Cresawn 2011). One feature Phamerator does not include is the ability to retreive the sequences of specific genes from this databse. query-phamerator is an add on script designed to provide this feature by retrieving sequence information from this database and storing it in FASTA files.

2. Design
----------
query-phamerator is written in Python 2.7 and depends on the following packages:
- MySQLdb
- BioPython
- pygtk
- gtk

All other packages used are found in the standard library.

3. References
----------
1. Cresawn, Steven G., Matt Bogel, Nathan Day, Deborah Jacobs-Sera, Roger W. Hendrix, and Graham F. Hatfull. 2011. “Phamerator: A Bioinformatic Tool for Comparative Bacteriophage Genomics.” BMC Bioinformatics 12 (1) (October 12): 395. doi:10.1186/1471-2105-12-395.
