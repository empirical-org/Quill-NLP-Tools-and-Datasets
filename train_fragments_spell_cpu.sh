export PYTHONPATH=.
export CUDA_VISIBLE_DEVICES=-1
python scripts/quillgrammar/generate_fragments.py /mnt/fragments/new_comprehension.tsv /mnt/notw/notw_sentences.txt
python -m spacy train config_textcat.cfg --output fragment-model/ --paths.train train.spacy --paths.dev dev.spacy
python scripts/test_fragments.py fragment-model/model-best/ /mnt/fragment-test-fine/fragments.tsv 0.5
