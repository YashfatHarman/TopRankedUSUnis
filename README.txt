A small project done back in 2016/2017. Wanted to mine some data about top US universities from online, and to analyze it. The data was collected through following steps:
1. First, top ranked 200 university names, and some basic infromation about location, enrollment etc was extracted from USNews website.
2. Then for each university, corresponding wikipedia page was mined and some additional information (for example, endowment) was collected.
3. Finally, annual research expenditure for each university was collected from an NSF report.

After the date from various sources are joined and cleaned, the answer of the following questions were looked for:
1. What single piece of data is the most correlated to ranking?
2. What are the outliers?
3. By region of country, which feature is most important for higher education: ranking, and cost? Which region has the best universities, and which region is the most affordable? 

The data extraction and cleaning part was quite thorough, the data wa even stored in a SQLite database so that they can be queried later easily. The analysis part didn't go into much detail at that time.

In retrospect, I probably would use pandas now. The questions are still relevant, and I plan to return to the project and complete the analysis. Till then.

Shafayat Rahman
2019


 
