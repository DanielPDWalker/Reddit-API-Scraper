# Reddit API Scraper

This is a script made specifcally to scrape, through the Reddit API, the SpaceX subreddit's lauches wiki page. 

It pulls out the tables it needs, then cleans the data of markdown, whitespace ect. It then takes the headings of the tables and saves them in a list for later use, and saves the main data of the table into another list. I then used numpy to make a numpy array which I then reshaped and turned into a pandas dataframe using the previously saved headings. It then exports the dataframes to a csv file, (it adds an index), and puts a timestamp for when the script was run into the filename of the output csv.
