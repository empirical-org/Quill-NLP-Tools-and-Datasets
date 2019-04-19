from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline


def cluster(list_of_texts, num_clusters=3):
    """
    Cluster a list of texts into a predefined number of clusters.

    :param list_of_texts: a list of untokenized texts
    :param num_clusters: the predefined number of clusters
    :return: a list with the cluster id for each text, e.g. [0,1,0,0,2,2,1]
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