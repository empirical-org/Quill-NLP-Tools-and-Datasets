# Fragments


Quill recognizes 6 main types of fragments,

 1. Subordinate clause fragments
 2. Participle phrase fragments
 3. Infinitive phrase fragments
 4. Afterthought fragments
 5. Lonely verb fragments
 6. Apositive fragments


Therefore, this fragments directory contains 6 folders, one for each of the 6
fragment types.  They contain arbitrary numbers of text files that have the
pattern of a sentence followed by a fragment where the fragment is derived from
the sentence above. The text files can be nested in folders within the top level
folder. The below is an example.

```txt
The man ate the red pear.
The red pear.
The woman ate the yellow apple.
The yellow apple.
```


The fragment type will mirror that of the folder it is contained in.

# Using the combined document generator

Along with the 6 fragment type folders, the top level also contains a script for
generating combination documents. The combination documents have the same
structure as those containeed in the folders, but include the entire contents of
a folder in a single file.  These combined documents can be useful for training
models. By default, they have the extention .combined.txt and are ignored by
version control.

```bash
./create_combination -d directory/
```
