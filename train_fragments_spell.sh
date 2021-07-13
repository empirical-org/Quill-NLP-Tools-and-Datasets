python scripts/quillgrammar/generate_fragments.py
python -m spacy train config_textcat.cfg --output fragment-model/ --paths.train train.spacy --paths.dev dev.spacy --gpu-id 0
