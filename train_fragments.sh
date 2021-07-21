export PYTHONPATH=.
export CUDA_VISIBLE_DEVICES=-1
python scripts/quillgrammar/generate_fragments.py new_comprehension.tsv notw_sentences.txt
python -m spacy train config_textcat_cpu.cfg --output fragment-model/ --paths.train train.spacy --paths.dev dev.spacy
python scripts/test_fragments.py fragment-model/model-best/ fragments.tsv 0.5
