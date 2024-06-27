import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


def get_suggested(user_id, user_item_matrix, model, k=5, n_neighbors=5):
    # Находим ближайших соседей
    distances, indices = model.kneighbors(user_item_matrix.loc[user_id].values.reshape(1, -1), n_neighbors=n_neighbors+1)
    
    # Извлекаем идентификаторы ближайших соседей (кроме самого пользователя)
    similar_users = [user_item_matrix.index[i] for i in indices.flatten() if user_item_matrix.index[i] != user_id]
    
    recommendations = defaultdict(float)
    
    for similar_user in similar_users:
        for item in user_item_matrix.columns:
            if user_item_matrix.loc[user_id, item] == 0 and user_item_matrix.loc[similar_user, item] > 0:
                recommendations[item] += 1 / (distances.flatten()[similar_users.index(similar_user) + 1] + 1e-10)  # Добавляем малое значение для избежания деления на 0
    
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_recommendations[:k]]


def suggest_follows(connection, userId):
    SELECT_FOLLOWS = """SELECT "followedById", "followingId" FROM public."Follows"
    ORDER BY "followedById" ASC, "followingId" ASC """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_FOLLOWS)
            result = cursor.fetchall()
            follows = pd.DataFrame(result, columns=["followedById", "followingId"])


    # Создаем матрицу взаимодействий
    user_item_matrix = follows.pivot_table(index='followedById', columns='followingId', aggfunc='size', fill_value=0)

    # Обучаем модель NearestNeighbors
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(user_item_matrix)

    suggested = get_suggested(userId, user_item_matrix, model, k=7)

    return suggested