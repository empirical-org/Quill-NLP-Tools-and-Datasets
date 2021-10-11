from quillnlp.corpora.notw import read_sentences

corpus_dir = '/home/yves/data/newsoftheworld/'
notw_sentences = read_sentences(corpus_dir, n=1000000)

with open('notw_sentences.txt', 'w') as o:
    for sentence in notw_sentences:
        o.write(sentence + '\n')
