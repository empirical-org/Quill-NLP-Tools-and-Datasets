
# Language Tool Notes

Language Tool is an open source proof­reading service.  It is good at a few
things, and has some areas where it is not so good.

## Fragment detection

Language Tool lets a lot of fragments slide by, but is good at giving feedback
for some type of fragments.

### Subordinate Clause Fragments

Language tool is good at detecting these, and good at giving feedback.
Quill does not excel at detecting this type of fragment currently.

### Participle Phrase Fragments

Neither language tool nor quill do a good job of detecting these types of
Fragments.

### Infinitive Phrase Fragments

Neither Language Tool nor quill do a good job of detecting these types of
Fragments.

### Afterthought Fragments

Languag Tool is not good at detecting these.  Quill gives sentences like these
low scores, but doesn't always fail them. Perhaps better corpora could solve
this issue.

### Lonely Verb Fragments

#### Examples of lonely verb fragments
- Should have been driving with more care.
- Sobbed in the driver's seat.
- Always disobeying the speed limit.

#### Possible fixes
- James sobbed in the driver's seat.
- Selena should have been driving with more care.
- Amy is always disobeying the speed limit.
- John left his dishes on the pathio and let the raccoons, opossums, and
  armadillos that visit the yard eat the leftovers.

Language Tool is not good at detecting these. Quill is not either.  Quill will
assume neither the initial fragment, nor the possible fix are a sentence.

### Appositive Fragments

Language Tool is not good at detecting these.  Quill is pretty good at
detecting these types of sentences, though it does throw some false negatives.

### False negatives

Quill has many sentences that it declares fragments, even though they are
actually sentences.  Sentences with appositives are on this list, and many other
sentence types.

## Consideations

For the is_sentence functionality, is a false positive (Quill thinks a fragment
is sentence) or a false negative (Quill thinks a sentence is a fragment) worse?
