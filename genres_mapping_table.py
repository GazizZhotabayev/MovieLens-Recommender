def genres(folder):
    '''
        movies data has genres like 'Action | Adventure | Comedy'
        the point of this script is to break down all the individual genres
        and then to get a mapping table between these unique values and all the possible combinations
        so in the end we have a 2-column table like

        Genre ... Genre Combination
        Action ... Action
        Action ... Action | Adventure
        Action ... Action | Adventure | Comedy
        Action ... Action | Comedy
        ...
        Adventure ... Action | Adventure
        ...

        this table is needed for the Power BI portion - a simple way for the user to filter their recommendations by unique genres
    '''
    import pandas as pd
    from itertools import product
    #read in genre data
    df = pd.read_table(folder + 'movies.dat', engine = 'python', sep = '::', header = None,
                       names = ['Movie ID', 'Name', 'Genre']).drop(columns = ['Movie ID', 'Name']).drop_duplicates()
    
    genre_combos = df['Genre'].unique() #get all possible genre combinations
    unique_genres = list(set([i for combo in genre_combos for i in combo.split('|')])) #get all unique genres
    d = {genre: [] for genre in unique_genres} #create a dictionary the keys of which will be column 1 and the values column 2 of our end table
    for combo in df['Genre']:
        for genre in d:
            if genre in combo: d[genre].append(combo)

    for k in d:
        d[k] = sorted(d[k])
        
    new_df = pd.DataFrame(columns = ['Genre', 'Genre Combinations']) #create the output dataframe
    for genre in unique_genres: #add in all the dictionary genre / genre combination pairs to it
        for combo in d[genre]:
            new_df = new_df.append(pd.DataFrame(data = {'Genre': [genre], 'Genre Combinations': [combo]}))

    new_df.to_csv(folder + "genre_combos.csv", index = False)
    return new_df
