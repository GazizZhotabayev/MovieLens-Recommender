# MovieLens Recommender - System

What I implemented here is a recommender system that’s using item-based collaborative filtering. The basic idea behind it is - if you say two movies both suck / are both mediocre / are both awesome - then this is pointing to some real similarity between the two. In other words, the fact that the same user (you) gave them the same rating, means that this pair of movies clearly both cater (or both do not cater) to the same kind of taste (yours). Now extrapolate this to thousands of users - one can get a pretty good estimation for which two movies go together.

## Source

The data comes from the [MovieLens 10M+ dataset](https://grouplens.org/datasets/movielens/10m/)

## Computing the similarity score

You can take a look at the Python code I've used to compute the similarity scores between every possible pair of movies. The high level rundown is:
1. Import the data into a Spark dataframe
2. Self-join it on the User ID (we only want to get pairs of movies that were watched by the same user) 
3. Group by each movie pair and compute the cosine similarity between them

## DAX code to get the top recommended movies

```
_Top Movies = 
VAR Selected_Movie = [_Selected Movie]
VAR Threshold = IF(ISBLANK(N_Users_Threshold[_N Users Threshold]), 100, N_Users_Threshold[_N Users Threshold])
VAR Table1 =
    FILTER(
        ALL('Similarity Matrix'),
        'Similarity Matrix'[Movie ID_y] = Selected_Movie
        && 'Similarity Matrix'[n_users] >= Threshold
        && RELATED('Genres (to LookUp)'[Genres]) IN VALUES('Genre Mapping'[Genre Combinations])
        )
VAR ANS =
    CONCATENATEX(
        TOPN(10, Table1, [cos_similarity], DESC),
        RELATED(Movies[Name]),
        UNICHAR(10)
    )
RETURN
    IF(
        ISBLANK(ANS),
        "Sorry, looks like there isn't a movie that's been watched with '" & LOOKUPVALUE(Movies[Name], Movies[Movie ID], Selected_Movie) & "' by enough users. Try lowering the user threshold or broadening the scope of genres.",
        ANS
        )
```
