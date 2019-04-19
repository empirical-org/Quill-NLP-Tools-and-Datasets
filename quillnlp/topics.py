from gensim.corpora import Dictionary
from gensim.models import LdaModel


def get_topics_in_document(tokens, dictionary, model):
    return model[dictionary.doc2bow(tokens)]


def print_topics(model):
    for (topic, words) in model.print_topics():
        print(topic+1, ":", words)


def find_topics(token_lists, num_topics=10):
    """ Find the topics in a list of texts with Latent Dirichlet Allocation. """
    dictionary = Dictionary(token_lists)
    print('Number of unique words in original documents:', len(dictionary))

    dictionary.filter_extremes(no_below=2, no_above=0.7)
    print('Number of unique words after removing rare and common words:', len(dictionary))

    corpus = [dictionary.doc2bow(tokens) for tokens in token_lists]
    model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, chunksize=100, passes=5, random_state=1)

    print_topics(model)

    return model, dictionary