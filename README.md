# OSINT-analysis-data-engineering
A data engineering project that cleans and transforms MITRE ATT&CK STIX data and KEV data.

# generate.py
This file reads in all three domains of MITRE STIX data (enterprise, mobile, and ICS) and writes it into excel files that are stored in the 'raw' directory; I made this so I did not have to query MITRE every time I wanted to run the code to test it. This file should be run first as it generates the files the other .py files depend on. The 'raw' directory also contains a CSV mapping artifact from https://center-for-threat-informed-defense.github.io/mappings-explorer/external/kev/ that is used to cross-reference with the enterprise domain data. 

# comparison.py
This file compares the mobile and enterprise domains to identify common techniques between the two domains. It generates 3 dataframes: techniques found in the enterprise domain and not in the mobile domain, techniques in the mobile domain not in the enterprise domain, and techniques found in both domains. I added a new column, "parent techniques", to capture more similarities. This column treats subtechniques as their parent techniques (Example: T1458.002 gets treated as T1548).

That being said, there still were not any common attacker techniques between the two domains. My code is still there, though, in case anyone wants it.

# examples_mitigations_detections.py
This file goes through each attacker technique and counts references to that technique in the excel sheets containing the examples, mitigations, and detections for all attacker behavior. It generates 3 dataframes, one for each domain, that provides the number of occurrences, known mitigations, and known detections of each attacker technique.

# add_columns.py
This is the biggest file that extracts data from existing columns and creates new ones for better readability. The new columns I added are as follows:

All 3 domains:
  • associated codes, commands, programs - I noticed that in several descriptions of attacker techniques, many of the CLI commands and programs used in the technique were encased in <code></code> blocks. I wrote a regular expression to extract the commands and programs within the blocks and listed them in their own separate column named "associated codes, commands, and programs". I may have missed a few that were not encased in <code></code>, but I believe I got most of them.
  • associated and/or followup techniques - I also noticed that the majority of the descriptions also contain links to other attacker behaviors that were used as follow-up attacks or otherwise associated. I wrote a regular expression to extract these as well and put them into the "associated and/or followup techniques" column.
  • updated citations - This is not a new column but an update of an existing column. I saw that the descriptions of some techniques contained citations that were not present in the "relationship citations" column, so I extracted the citations from the descriptions and added them to the citations column after checking if the new citations were already present.
  • cleaned description - Using SpaCy and regular expressions, I removed all the text in the descriptions that I deemed unnecessary or contained information already present in another column. This included links, citations, the "Adversary/Adversaries may" at the start of most descriptions, punctuation, and stop words. I also lemmatized all words in the description. 
  • most common verbs - Using the cleaned description, I made a new column containing the 5 most common verbs present in each description.
  • most common nouns - Same as the "most common verbs" column, but with nouns.

Mobile domain only:
  • is subtechnique - I noticed that while the data for the enterprise domain contained columns that specified if a technique is a subtechnique and what its parent technique is, while the mobile domain lacked it. This was strange, since some of the techniques in the mobile domain had the ".00X" notation that was indicative of a subtechnique (example: T1406.001). So I went ahead and made an "is subtechnique" column just like the one in the enterprise domain data.
  • subtechnique of - To keep things consistent with the enterprise domain data, I also specified which technique the subtechniques belonged to and put them in the "subtechnique of" column.

Enterprise domain only:
  • CVEs that allow this technique - I came across a mapping artifact file on https://center-for-threat-informed-defense.github.io/mappings-explorer/external/kev/ that contained known common vulnerabilities and exposures (CVE) and indicated which attacker technique they allow for. For example, the Deserialization of Untrusted Data vulnerability (CVE-2023-40044) allows for the Indirect Command Execution behavior (T1202) with the reasoning being "Zero-day .NET deserialization vulnerability that allows an adversary to make an HTTP POST request to a vulnerable WS_FTP Server and execute commands". I cross-referenced the enterprise domain data with this mapping artifact to compile a list of CVEs for each attacker technique that allowed that attacker technique to be executed. 
