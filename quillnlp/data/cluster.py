from typing import List

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline


def cluster(list_of_texts: List[str], num_clusters: int=3) -> List[int]:
    """
    Cluster a list of texts into a given number of clusters,
    based on their tf-idf-weighted bag-of-word vectors.

    Args:
        list_of_texts: a list of untokenized texts
        num_clusters: the target number of clusters

    Returns: a list with the cluster id for each text, e.g. [0,1,0,0,2,2,1]
    """
    pipeline = Pipeline([
        ("vect", CountVectorizer()),
        ("tfidf", TfidfTransformer()),
        ("clust", KMeans(n_clusters=num_clusters))
    ])

    try:
        clusters = pipeline.fit_predict(list_of_texts)
    except ValueError:
        clusters = list(range(len(list_of_texts)))

    return clusters


def cluster_embeddings(embeddings: List[np.ndarray], num_clusters: int) -> List[int]:
    """
    Cluster a list of embeddings into a given number of clusters.

    Args:
        embeddings: a list of (dense) embeddings
        num_clusters: the target number of clusters

    Returns: a list with the cluster id for each text, e.g. [0,1,0,0,2,2,1]
    """
    clusterer = KMeans(n_clusters=num_clusters)
    clusters = clusterer.fit_predict(embeddings)
    return clusters

