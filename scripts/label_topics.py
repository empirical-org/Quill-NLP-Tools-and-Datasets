import csv
import random
import numpy as np

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC, SVC
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.calibration import CalibratedClassifierCV

#input_file = "scripts/data/surge_barriers_because.tsv"
input_file = "scripts/data/whaling_so.tsv"

TRAIN_SIZE = 50
stopwords = stopwords.words("english")


def read_file(filename):
    data = []
    with open(filename) as i:
        reader = csv.reader(i, delimiter="\t")
        for line in reader:
            data.append(line)

    return data

data = read_file(input_file)


def classify(data):

    random.shuffle(data)

    train_data = data[:TRAIN_SIZE]
    test_data = data[TRAIN_SIZE:]

    train_texts, train_labels = zip(*train_data)
    test_texts, test_labels = zip(*test_data)

    preprocessing = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1, 5), analyzer='char_wb',
                                 max_df=0.5)),
        ('tfidf', TfidfTransformer(use_idf=False))
    ])

    preprocessing.fit_transform(train_texts)
    train_preprocessed = preprocessing.transform(train_texts)
    test_preprocessed = preprocessing.transform(test_texts)

    classifier = LinearSVC()
    #classifier = LogisticRegression(multi_class="ovr")

    classifier.fit(train_preprocessed, train_labels)
    predictions = classifier.predict(test_preprocessed)

    accuracy = np.mean(predictions == test_labels)
    print(accuracy)
    return accuracy


def classify_with_clustering(data):

    texts, labels = zip(*data)

    preprocessing = Pipeline([
        ('vect', CountVectorizer(ngram_range=(1, 5), analyzer='char_wb',
                                 max_df=0.5)),
        ('tfidf', TfidfTransformer(use_idf=False))
    ])

    preprocessing.fit_transform(texts)
    texts_preprocessed = preprocessing.transform(texts)

    clusterer = KMeans(n_clusters=TRAIN_SIZE)
    clusters = clusterer.fit_predict(texts_preprocessed)

    train_data = []
    test_data = []

    seen_clusters = set()
    train_indices = set()

    data_and_clusters = list(enumerate(list(zip(clusters, data))))
    random.shuffle(data_and_clusters)

    for idx, (cluster, item) in data_and_clusters:
        if cluster not in seen_clusters:
            seen_clusters.add(cluster)
            train_data.append(item)
            train_indices.add(idx)
        else:
            test_data.append(item)

    train_texts, train_labels = zip(*train_data)
    test_texts, test_labels = zip(*test_data)

    preprocessing.fit_transform(train_texts)
    train_preprocessed = preprocessing.transform(train_texts)
    test_preprocessed = preprocessing.transform(test_texts)

    classifier = LinearSVC()
    classifier.fit(train_preprocessed, train_labels)

    predictions = classifier.predict(test_preprocessed)

    accuracy = np.mean(predictions == test_labels)

    cv_classifier = CalibratedClassifierCV(classifier, cv="prefit")
    cv_classifier.fit(train_preprocessed, train_labels)

    all_predictions = classifier.predict(preprocessing.transform(texts))
    all_cv_predictions = cv_classifier.predict_proba(preprocessing.transform(texts))

    in_top_two = []
    for idx, (item, prediction, probs, correct_label) in enumerate(list(zip(data, all_predictions, all_cv_predictions, labels))):

        sorted_indices = np.argsort(probs)[::-1]  # reverse sort
        prediction_prob = probs[list(classifier.classes_).index(prediction)]

        for class_index in sorted_indices:
            second_guess = classifier.classes_[class_index]
            second_guess_prob = probs[class_index]
            if second_guess != prediction:
                break

        is_train = idx in train_indices
        print(f"{item[0]}\t{is_train}\t{prediction}\t{prediction_prob}\t{second_guess}\t{second_guess_prob}")
        if not is_train:
            #print(item)
            #print("C", correct_label)
            #print("P", prediction)
            #print("S", second_guess)
            #print("--")

            in_top_two.append([correct_label == prediction or correct_label == second_guess])

    second_accuracy = np.mean(in_top_two)
    print(accuracy, second_accuracy)

    return accuracy, second_accuracy


accuracies = []
accuracies2 = []
for _ in range(1):
    acc1, acc2 = classify_with_clustering(data)
    accuracies.append(acc1)
    accuracies2.append(acc2)

print("Mean accuracy:", np.mean(accuracies))
print("Mean accuracy2:", np.mean(accuracies2))


