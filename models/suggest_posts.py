import pandas as pd
from collections import defaultdict

from surprise import SVD, Reader, Dataset

def transform_to_rating(interaction_type):
    if (interaction_type == 'VIEW'): return 1
    if (interaction_type == 'LIKE'): return 2
    if (interaction_type == 'REPOST'): return 3


def transform_data(data):
    data = data.rename(columns={'type': 'rating'})
    data['rating'] = data['rating'].apply(transform_to_rating)
    data = data.groupby(['userId', 'postId']).sum().reset_index()

    return data


def get_top_n(predictions, id, n=10):
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    recs = top_n.get(id)
    return [iid for (iid, _) in recs]


def get_suggested(data, userId):
    algo = SVD()

    reader = Reader(rating_scale=(1, 6))
    data = Dataset.load_from_df(data, reader)

    train_set = data.build_full_trainset()
    test_set = train_set.build_anti_testset()

    algo.fit(train_set)
    predictions = algo.test(test_set)

    top_n = get_top_n(predictions, userId, n=100)

    return top_n


def suggest_posts(connection, userId):
    SELECT_INTERACTIONS = """SELECT \"userId\", \"postId\", type FROM public.interactions"""

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_INTERACTIONS)
            result = cursor.fetchall()
            interactions = pd.DataFrame(result, columns=['userId', 'postId', 'type'])

    interactions = transform_data(interactions)
    
    

    return get_suggested(interactions, userId)