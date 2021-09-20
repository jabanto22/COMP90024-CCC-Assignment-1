import pandas as pd
import json
from mpi4py import MPI
import collections
from collections import Counter
import datetime, time

def read_melb_grid():
    """
        Read and extract grid id and coordinates from melbGrid.json
        and return a dictionary containing the extracted data.
    """
    grid_coordinates = {}
    with open('melbGrid.json', 'r', encoding="utf8") as f:
        features = json.load(f)['features']
        for feature in features:
            grid_coordinates[feature['properties']['id']] = feature['properties']
    f.close()
    return grid_coordinates


def read_sentiment_scores():
    """
        Read and extract word-sentiments, phrase-sentiments, and their corresponding scores
        and return a dictionary containing the extracted data.
    """
    with open("AFINN.txt", 'r') as f:
        sentiment_score = {}
        line = f.readline()
        while line:
            sentiment = ""
            for word in line.split():
                try:
                    int(word)
                    sentiment_score[sentiment.rstrip()] = int(word)
                except:     
                    sentiment += word + " "
            line = f.readline()
    f.close()  
    return sentiment_score


def process_tweets(size, rank):
    """
        Read and extract grid and tweets from Twitter file.
        Send the tweets to slaves to compute the tweet count and sentiment scores.
    """
    print ("Job started in", name, processor_name, rank, "on", datetime.datetime.now())
    with open('bigTwitter.json', 'r', encoding="utf8") as f:   
        for i, line in enumerate(f):
            # send data to processor rank
            if i%size == rank:
                line = line.rstrip("]" + "[" + "," + "\n") 
                try:
                    j = json.loads(line)['value']
                    grid = get_tweet_grid(j['geometry']['coordinates'], grid_dict)
                    # process tweets that belong within the boundaries of the grid
                    if not grid is None:
                        process_tweet([grid,j['properties']['text']], score_dict)
                except:
                    # continue reading even if an incorrectly formatted json statement is read
                    continue
    f.close()
    print ("Process ended in", name, processor_name, rank, "on", datetime.datetime.now())
    
    
def process_tweet(text, score_dict): 
    """ 
        Compute the sentiment score of the tweet on a grid location.
    """ 
    cell = text[0]   
    tokens = text[1].lower().split()
    i = 0   
    token = "" 
    # maxMatch the sentiments extracted from the tweets 
    while i < len(tokens):  
        token = tokens[i].lstrip(''''"''').rstrip('''!,?.'"''') 
        for j in range(len(tokens), i, -1):
            # search for the longest sentiment (phrase) after removing valid punctuation marks  
            # at the end of the phrase and quotation marks enclosing the phrase
            tmp_token = (' '.join(t for t in tokens[i:j])).lstrip(''''"''').rstrip('''!,?.'"''')
            if tmp_token in score_dict and len(tmp_token) > len(token):  
                token = tmp_token
                break
                
        if len(token.split()) > 0:
            if token in score_dict: 
                cell_sentiment_score[cell] += score_dict[token]
            i += len(token.split())
        # if there is no token after preprocessing add 1 instead of length of token   
        # to avoid infinite loop
        else:
            i += 1


def get_tweet_grid(coordinates, grid_coord):   
    """ 
        Identify the grid location of tweet coordinates.
        Count the number of tweets in grid locations.
    """ 
    grid = None
    x = coordinates[0]
    y = coordinates[1]
    for cell in grid_coord:
        if grid_coord[cell]['xmin'] < x <= grid_coord[cell]['xmax'] and \
        grid_coord[cell]['ymin'] < y <= grid_coord[cell]['ymax']:
            grid = cell
            cell_twt_cnt[cell] += 1
            break  
    return grid


def aggregate_results(twt_count, twt_sentiment):
    """
        Aggregate the tweet count and sentiment scores as a single dataframe
        sorted on grid/cell names.
    """
    gather_tweet_count = Counter() 
    for count in twt_count: 
        gather_tweet_count.update(count)   
        
    gather_sentiment_scores = Counter()
    for sent in twt_sentiment:
        gather_sentiment_scores.update(sent) 

    # Merge the sentiment scores with tweet count   
    grid_sentiment_score_dict = {} 
    for key in gather_tweet_count:
        grid_sentiment_score_dict[key] = {'#Total Tweets':gather_tweet_count[key],  
            '#Overall Sentiment Score':gather_sentiment_scores[key]} 
    grid_sentiment_score = pd.DataFrame(grid_sentiment_score_dict).transpose()

    # sort by grid names
    sorted_grid = grid_sentiment_score.sort_index()
    sorted_grid.sort_index(axis=1, ascending=False, inplace=True)
    return sorted_grid


if __name__ == "__main__":
    """ 
        Start process from here.   
        Set start time from this point.
    """ 
    start_time = time.time() 

    # Initialize tweet count, sentiment score, grid, and sentiment-score dictionary  
    cell_twt_cnt = collections.defaultdict(int)
    cell_sentiment_score = collections.defaultdict(int)
    grid_dict = read_melb_grid()   
    score_dict = read_sentiment_scores()

    # Initialize MPI
    comm = MPI.COMM_WORLD

    # get MPI size, rank, and processor name
    size = comm.Get_size()
    rank = comm.Get_rank()
    name = comm.Get_name()
    processor_name = MPI.Get_processor_name()

    # read and process twitter data
    process_start_time = time.time()
    process_tweets(size, rank)
    process_stop_time = time.time() 
    
    # Block until all processes finish search 
    # then gathers the tweet and sentiment counts from each slave
    comm.barrier()
    gather_count = comm.gather(cell_twt_cnt, root=0)   
    gather_sentiment = comm.gather(cell_sentiment_score, root=0)

    # Aggregate the tweet count and sentiment score dictionaries at master node
    # and print the results and processing times
    if rank == 0:

        aggregate_start_time = time.time()
        results = aggregate_results(gather_count, gather_sentiment)
        aggregate_stop_time = time.time()

        # print out the results
        print("Total tweets and sentiment score on each grid:")  
        print(results)

        # print out processing times
        process_time = process_stop_time - process_start_time   
        aggregate_time = aggregate_stop_time - aggregate_start_time
        total_time = time.time() - start_time
        
        print("Total processing time of twitter data:", round(process_time,3),"sec")   
        print("Total result aggregation time:", round(aggregate_time,3), "sec")
        print("Total time:", round(total_time,3), "sec")
