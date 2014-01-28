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

The table `gene` contains the columns `GeneID`, `PhageID`, `Start`, `Stop`, and `Name`, `Translation` and `Orientation`. Every row corresponds to a gene. `Start`, and `Stop` are of type `mediumint` and contain the start and stop locations of the gene in the respective phage's genome. The column `Translation` stores the amino acid sequence of the gene. `Orientation` (type `enum(F,R)`) contains the orientation of the gene and `Name` is the name of the gene. `GeneID`, and `PhageID` can be used to cross-reference this table with the `phage` and `pham` tables.

The table `pham` contains 3 columns (`GeneID`, `name`, and `orderAdded`) of which `GeneID` and `name` are used in query-phamerator. `GeneID` corresponds to a gene from the table `gene` and `name` holds the pham number of this gene.

**2.3 Retrieving gene information**

query-phamerator retrieves gene sequences by building a MySQL query from user inputs. Users can retrieve gene information from specific phams, phages, clusters, or any combination of the three. Blank fields do not affect the search query (i.e. if phams is left blank gene information from all phams will be retrieved). Users can also specify they type of sequence retrieved (DNA, RNA, or amino acid) and they can also choose to organize the retrieved sequences by cluster/phage or by pham. These options are passed to the class `Query` as the variables `self.phams`, `self.phages`, `self.clusters`, `self.aa`, and `self.o` respectively. The values 0, 1, and 2 for `self.aa` correspond to amino acid, DNA, and RNA respectively. The values of True and False for `self.o` correspond to a cluster/phage organization and a pham organization respectively.

When a search is run the first function called is `Query.get_gene_list`. This function assembles a list of genes (specifically, `GeneID`s) from the parameters specified by the user by building a MySQL query. The function begins by first assembling a list of phages from which to retrieve gene information. This list is used to retreive the list of genes. The genes are stored in a dictionary, with keys of either pham number or phage name depending on the user organization choice. This dictionary is stored in `Query.gene_list`.

The function `make_fasta_files` uses the dictionary of genes to create FASTA files of the gene sequences. The program creates folders and files for the appropriate organizational structure (e.g. each cluster will have a folder and each phage will have a .fasta file under the phage/cluster organizational structure). The program uses BioPython to collect, store, and manipulate sequences. 

3. References
----------
1. Cresawn, Steven G., Matt Bogel, Nathan Day, Deborah Jacobs-Sera, Roger W. Hendrix, and Graham F. Hatfull. 2011. “Phamerator: A Bioinformatic Tool for Comparative Bacteriophage Genomics.” BMC Bioinformatics 12 (1) (October 12): 395. doi:10.1186/1471-2105-12-395.
2. http://mysql-python.sourceforge.net/
3. http://biopython.org/wiki/Main_Page
4. http://pygtk.org/
