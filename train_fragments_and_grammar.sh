export PYTHONPATH=.
export CUDA_VISIBLE_DEVICES=0
python scripts/quillgrammar/combine_fragments_and_grammar_data.py new_comprehension.tsv data/raw/notw_sentences.txt
python -m spacy train config_fragment_grammar.cfg --output fragment-grammar-model-binary-mixeddata/ --paths.train grammar-fragment-train --paths.dev dev.spacy --gpu-id 0
python scripts/test_fragments.py fragment-grammar-model-binary-mixeddata/model-best/ ./scripts/data/fragments2.tsv 0.5
