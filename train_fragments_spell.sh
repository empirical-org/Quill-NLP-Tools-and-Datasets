export PYTHONPATH=.
export CUDA_VISIBLE_DEVICES=0
python scripts/quillgrammar/generate_fragments.py /mnt/fragments/new_comprehension.tsv /mnt/notw/notw_sentences.txt
python -m spacy train config_textcat.cfg --output fragment-model/ --paths.train train.spacy --paths.dev dev.spacy --gpu-id 0
