from collections import defaultdict
from typing import List

import numpy as np
from sklearn.cluster import KMeans
from scipy import spatial


def select_diverse_embeddings(embeddings: List[np.ndarray], target_num: int) -> List[int]:
    """
    Select a subset of embeddings from a list that maximize diversity.

    Args:
        embeddings: a list of (dense) embeddings
        target_num: the number of embeddings that will be selected

    Returns: a list with the indexes of the embeddings that have been selected

    """

    # Cluster the embeddings in the given number of clusters
    clusterer = KMeans(n_clusters=target_num)
    clusters = clusterer.fit_predict(embeddings)

    # Group the embeddings by cluster id
    cluster_items = defaultdict(list)
    for idx, cluster in enumerate(clusters):
        cluster_items[cluster].append(idx)

    # For every cluster, identify the center and select the embedding that is most
    # similar to this center.
    diverse_indexes = []
    for cluster in range(target_num):
        cluster_center = clusterer.cluster_centers_[cluster]

        similarities = []
        for item_idx in cluster_items[cluster]:
            similarity = 1 - spatial.distance.cosine(embeddings[item_idx], cluster_center)
            similarities.append(similarity)

        most_central_item_idx = cluster_items[cluster][similarities.index(max(similarities))]
        diverse_indexes.append(most_central_item_idx)

    return diverse_indexes
