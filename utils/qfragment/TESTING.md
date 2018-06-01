# TESTING

This document outlines the testing strategy for qfragment.


## Sentence types

### Sentence fragments.

Currently these types of questions give students a partial sentence and they are
asked to complete it (no sentence fragment question is in production - though
many are in Alpha and have been answered thousands of times). Typically,
students are instructed to add 1-3 words to complete the sentence.

In its current form, the feedback is not always very good. For example, one
question asks students to make the incomplete sentence 'After the football game
ended' into a complete sentence.  Here are some screenshots from my attempts.


![](photos/correct-marked-wrong-comma-missing.png)
*Here, I am missing a comma after the introductory phrase.  It's not so much a
mistake as a stylistic choice - many books don't add a comma after an
introcuctory phrase if the phrase is only a few words. The feedback given is
poor.  It doesn't reflect my error (which could probably be ignored in young
writers!).*

![](photos/correct-marked-wrong.png)
*Here, my answer is entirely correct. Unfortunately, by changing the sentence
order I have upset the computer terribly.  It thinks I am missing an action word
which I obviously am not, and a person or thing doing the action... clearly
James!*

![](photos/correct-feedback.png)
*Finally, I've gotten one correct! Or at least I think I have.  I get no
feedback at all.*


**Most common student errors:** Despite the imperfection of the current fragments
lessons, we do have some data on student responses.  Here are the things
students struggle with.

 1. Answering at all.  Many students will just try to submit the question as
   given.
 2. Subject-verb agreement. Some students seem to think that changing the tense
    of a verb could fix a sentence fragment.  ie, "After the game ends.".
 3. Capitalization. Many students tried capitalizing a letter to fix the
    sentence.
 4. Useless word or comma addition.  Students will add an adjective, adverb, or
    comma somewhere in the sentence hoping that this will change it into a
    sentence. Prepositional phrases are also common additions.
 5. Bad word order. 
   

With these errors in mind, here is some baseline on how well the new detector
works.

 * While we were swimming at the lake...
  1. While we were swimming at the lake, a fish bit me. [INCORRECT][SVA ERROR]
      - bit is an irregular, including irregulars 'as is' could solve this
  2. While we were swimming at the lake, we saw a fish.
  3. While we were swimming at the lake we saw a fish.
  4. We were swimming at the lake.
  5. While we were swimming, at the lake. [INCORRECT][NO ERROR]
      - Rule based model handles this (single verb)
  6. While we were swimming at the lake, it began to rain. [INCORRECT][SVA ERROR]
      - began is an irregular, including irregulars 'as is' could solve this
  7. While we were swimming at the lake, we had a picnic.
  8. We went swimming at the lake.
  9. While we were swimming at the lake, something happened.
  10. While we were swimming at the lake, something happening.
  11. While we were swimming at the lake we seen a snake.
      - seen is an irregular, including irregulars 'as is' could solve this
  12. While we were swimming at the lake, we seen a snake. [INCORRECT][NO ERROR]
  13. While we were swimming at the lake, we seen fish. [INCORRECT][NO ERROR]
  14. It happen while we were swimming at the lake.
  15. It happened while we were swimming at the lake.
  16. While we were swimming at the lake, we see fish in the water.
  17. While we were swimming at the lake, we saw fish in the water.
  18. While we were swimming at the lake, we seen fish in the water. [INCORRECT][NO ERROR]
      - seen is an irregular, including irregulars 'as is' could solve this
  19. While we were swimming at the lake, we swam laps in the water.
  20. o

# be, have, do, say, make, go, take, come, see, get.

The ten most commonly used verbs in english and ALL irreguar.

If we continued the list it would be

  1.     be
  2.     have
  3.     do
  4.     say
  5.     go
  6.     can
  7.     get
  8.     would
  9.     make
  10.    know
  11.    will
  12.    think
  13.    take
  14.    see
  15.    come
  16.    could
  20.    find
  21.    give
  22.    tell
  24.    may
  25.    should
  30.    feel
  31.    become
  32.    leave
  33.    put
  34.    mean
  35.    keep
  36.    let
  37.    begin
  43.    might
  45.    hear
  47.    run
  52.    hold
  53.    bring
  55.    must
  56.    write
  58.    sit
  59.    stand
  60.    lose
  61.    pay
  62.    meet
  65.    set
  66.    learn
  68.    lead
  69.    understand
  74.    speak
  75.    read
  78.    spend
  79.    grow
  82.    win
  88.    buy
  92.    send
  94.    build
  96.    fall
  97.    cut

More than half of the top 100 most common verbs are irregular! Here are some
more errors we can produce.

* While we were the lake...
  - '...we learn some math.' is marked wrong.  (GOOD) 
  - '...we ran some laps.' is marked right. (GOOD)
  - '...we seen some fish.' is marked right too. (WRONG!)
  - '...we been chilling.' is marked right too. (WRONG!)
  - '...we begun the ceremony' is marked right too. (WRONG!)
  - '...we bitten a cracker.' is marked right too. (WRONG!)
  
All these have these verbs have the same tenses according to the pattern library
- and none of them should ever directly follow the subject.  They each require
an auxilary verb like 'were' before them. Of course, you shouldn't really use
'were' before 'been' or 'begun' (ever) though you could use it in front of
'bitten' or 'seen'.

WAIT: because our generator only replaces single words, it doesn't have any
examples of reductions that are ALWAYS wrong. 

For example, take, the original sentence

`We have never seen those brave soldiers again.`

It's single-verb so it would go to the rule based system, but it's variations
would be

`We have never see/sees/seeing/saw those brave soldiers again.`

This shows us that the have-seen combination style is good (yay). And that the
have-see/sees/seeing/saw one is probably bad.


`We never saw those brave soldiers again.`


Another issue: 

Take
`One of the guinea-pigs was never seen again, and the same with the tortoise
when we have done his shell with vermilion paint.`

It's a fine sentence up until the comma, but we would end up marking two
reductions 'was never seen again' and 'when we have done'







































