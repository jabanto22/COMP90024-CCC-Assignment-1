# COMP90024-CCC-Assignment-1
Cluster and Cloud Computing Assignment 1 – The Happiest City

## Problem Description
Your task in this programming assignment is to implement a simple, parallelized application leveraging the University of Melbourne HPC facility SPARTAN. Your application will use a large Twitter dataset, a grid/mesh for Melbourne and a simple dictionary of terms related to sentiment scores. Your objective is to calculate the sentiment
score for the given cells and hence to calculate the area of Melbourne that has the happiest/most miserable people!

The files to be used in this assignment are:
* bigTwitter.json
  * this is the main 14Gb+ JSON file to use for your final analysis and report write up, i.e., do not use the bigTwitter.json file for software development and testing. Note that this data covers several cities in Australia (not just Melbourne).
* smallTwitter.json
  * smallTwitter.json this a 35Mb+ JSON file that can be used for testing;
* tinyTwitter.json
  * tinyTwitter.json this a small JSON file that should be used for initial testing
  * You may also decide to use the smaller JSON files on your own PC/laptop to start with.
* AFINN.txt
  * contains a list of words with a score related to the sentiment of the word, i.e., the extent that the words are happy or sad. For example:
```
abandon -2 
abandoned -2 
abandons -2 
…
happy +3 
…
sad -2
```
* melbGrid.json
  * includes the latitudes and longitudes of a range of gridded boxes as illustrated in the figure below, i.e., the latitude and longitude of each of the corners of the boxes is given in the file.
  ![melbGrid.png](https://github.com/jabanto22/COMP90024-CCC-Assignment-1/blob/main/melbGrid.PNG?raw=true)
  
Your assignment is to (eventually!) search the large Twitter data set (bigTwitter.json) and using just the tweet text and the tweet location (lat/long) that contain exact matches of the terms in the AFINN.txt file, count the total number of tweets in a given cell and aggregate the sentiment score for each grid cell for all of the data. The final
result will be a score for each cell with the following format, where the numbers are obviously representative.
```
Cell  #Total Tweets #Overal Sentiment Score 
A1      11,111              +123
A2      22,222              -234
A3      33,333              +345
A4      44,444              -456
… 
D3      55,555              +678
D4      66,666              -789
D5      77,777              +890
```

Only exact matches are required for the tweet text. Thus “#abandon” or “@abandon” or “abandoning” or “abandon23” or “abandon-COMP90024” etc are not an exact match and can be ignored. If a word ends in one of the following forms of punctuation: ! , ? . ’ ” then it can be regarded as an exact match, e.g. “COMP90024 is a course you should not abandon!” would match on “abandon”. A tweet may have multiple matches, e.g., “Sad to abandon COMP90024” would score -4 (-2 abandon, -2 sad). The words should be treated as case insensitive, e.g., “Abandon” and “abandon” and “AbAnDoN” can be considered as the same word and hence a match.

If a tweet occurs right on the border of two cells, e.g., exactly between the B1/B2 cell border then assume the tweet occurs in B1 (i.e., to the cell on the left). If a tweet occurs exactly on the border between B2/C2 then assume the
tweet occurs in C2 (i.e., to the cell below).

Your application should allow a given number of nodes and cores to be utilized. Specifically, your application should be run once to search the bigTwitter.json file on each of the following resources:
* 1 node and 1 core;
* 1 node and 8 cores;
* 2 nodes and 8 cores (with 4 cores per node).

The resources should be set when submitting the search application with the appropriate SLURM options. 

## Final packaging and delivery 
You should write a brief report on the application – no more than 4 pages!, outlining how it can be invoked, i.e. it should include the scripts used for submitting the job to SPARTAN, the approach you took to parallelize your code, and describe variations in its performance on different numbers of nodes and cores. Your report should also include a single graph (e.g. a bar chart) showing the time for execution of your solution on 1 node with 1 core, on 1 node with 8 cores and on 2 nodes with 8 cores.
