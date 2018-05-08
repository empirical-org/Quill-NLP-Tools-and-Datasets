
# Why our Subject Verb Agreement Model Sucks.

Here at Quill.org we have been working on improved sentence feedback for
students who hope to become better writers.  A part of this initiative is
detecting subject-verb agreement errors, unintentional tense shifts, and errors
within verb phrases such as double modal errors, ("You might should put that
pretty bike away.") or bad pairings ("have be").  I group all of these layers
under the catch-all title, Subject Verb Agreement, and often abreviate it to
SVA. The English language is full of intracacies that make SVA error recognition
and feedback difficult; this is a short post-mortem on why our last tensorflow
model failed so miserably.  This week will be spent creating a new model,
hopefully one that can better serve our students!  Update soon.

## The method

### First we gathered a set of correct sentences, and a set with errors 

In order to build a successful machine learning model, our strategy was to start
with seed sentence's from Project Gutenberg children's books. Literary licence
gives authors some freedom from grammar, but children's books tend to take less
advantage of that which was to our benefit. In all, we extracted more than 800,000
sentences and explored many of them manually to test our hypothesis. Despite all
being classified as children's books by Project Gutenberg, a good number of the
books had Flesh-Kincaid reading scores well into the 9th and 10th grade levels.
Our exploration of the data, along with that fact, convinced me that these
sentences would include a large enough portion of English grammar to be
suitable.

After the sentences were selected, we created a set of 'mangled sentences' by
changing the tense of single verb at a time in a correct sentence to all of its
alternatives. While this method is not sure to produce incorrect sentences, it
is extremely likely to for multiverb sentences because along with any number of
other problems, a sloppy tense shift is a near certainty.  Because Quill.org
already had a very successful Subject-Verb agreement checker for sentences with
a single verb phrase, we decided that we would continue to use our old
rule-based AI for checking single-verb sentences, and use the model for more
complex sentences.  From the 800,000 correct sentences, we created ~13 million
mangled sentences. 

### Then we reduced the sentences

'Reduction' is the word I came up with to describe the 'important' parts of a
sentence that we extract that can be used to train a neural net after being
translated into tensors. (This might not be the right word -- I am rather new to
this). In the case of SVA, we must decide if the verb agrees with the subject
(and the other verbs too really). This means that subjects and verbs are really
the only important information in the sentence.  It's also incredibly important
that we pair the correct subject with its verb phrase. ("They were at the park
while I was at the beach" is fine -- "I" has to agree with "was" but not with
"were" so this sentence is correct). 

For my methodolgy, I chose to pair the noun chunks with the verb phrases and
then change the literal noun into either 'SG' or 'PL' (singular or plural) and
change the verb literal into a hash of its tenses using the tenses method in the
python pattern library. I left pronouns alone since they have funky rules. Here
is an example of how it works,

```py
tenses('am')
# => [('present', 1, 'singular', 'indicative', 'imperfective')]
sha256(str(tenses('am'))).hexdigest()
# => '6b37717f3391631a174b04eba76ba908596c2b79f33256bfec458cd7d63578a4'
```

A sentence like, 'Kate is the better poet.' would generate a single reduction,
`tenses('is') > 'SG'`. Other sentences might have 2, 3, or more reductions.  Out
of around 1.6 million sentences we selected to reduce, ~5500 unique reductions
were found with the top reductions being found in thousands of sentences.

To train our models we then vectorize each sentence, which essentially means
representing it as an array of its reductions. Then, based on which reductions
are correlated with correct and incorrect sentences, the black-box of our neural
net can learn to make informed decisions.

We trained our model, and tested it. Testing revealed we were able to catch
errors with somewhere between 70 and 80 percent accuracy.  That might sound
suitable, but trust us, it wasn't.

### So why did it suck?

Stupid in, stupid out.

Our model was missing some critical information, and that is why it did so
poorly. **Our reductions didn't just 'reduce' the problem, they were changing it
entirely.** So what did we miss?

1. **Irregulars**. Out of the top 100 most common verbs in English, more than
   half are irregular in the way they shift tenses. Who would have guessed they
   were irregular in other ways too,

   → I am going running [✓]
   → I am swimming running [✘]

   Going and swimming have the same tenses, but going follows different rules
   than the word swimming. Go has so many grammar rules surrounding it that it
   has [its own Wikipedia page](https://en.wikipedia.org/wiki/Go_(verb)) 

   Verbs like 'Go' shouldn't be tensified, they should just be themselves.

2. **Action / Being verbs**. Another tense shift nightmare comes with action
   verbs and their more zen counterparts.

   → We were swimming. [✓]
   → We swam swimming. [✘]

   Tenses aside (swam and were have identical tenses according to pattern.en),
   these sentences have little in common. One is standard, the other is at best
   a reduntant mess if a comma were inserted after swam.

   → I want candy. [✓]
   → I be candy. [✘]

   Here is another even more egregious offender, the second has a clear subject
   verb agreement error, whereas the first is perfectly fine (albeit a bit
   hedonistic).  How dare we treat these sentences the same!

3. **Names**. Trusting the pattern library to check subjects for plurality was
   one of our greatest mistakes. It recognizes names like 'James' and even
   'Alice' as plural, creating dangerous situations.

   → James is tired. [✓]
   → The cars is broken. [✘]

   Interpreting James as plural here creates a disasterous reduction linking
   plural 3rd person nouns to the verb 'is', which as our example shows, is
   clearly incorrect.

4. **Mood**. Sentences can have different moods. Indicatives express factual
   information, imperatives issue commands, and the subjunctive deals in
   hypotheticals. What might be allowed for one mood, might not be in another.

   → He talks as if **he were an expert**. [✓]
   → **He were an expert.** [✘]

   The verb phrase is the same, but while it works in the subjunctive, it
   doesn't go over well in the indicative.

   → Pick up your clothes. [✓]
   → Your mom, pick up your clothes, is sad.  [✘]

   The subject in the first sentence is an implied 'You', and in the second, is
   'your mom'.  Our reductions though each include 'Pick' with no subject. In
   the indicative an unpaired verb should be in participle form ('Picking'), but in
   imperative form, the infinitive is the only style of verb that will do.

5. **Poor sentence simplification**. Sentences must be simplified before
   reducing them.  Removing modifiers, joining compound subjects, and  replacing
   infinitive phrases acting as subjects with gerunds are a few clean-up moves
   that make life a lot easier. 

   → To swim is fun. → is > swim →  is ✘ swim 

   If we change the infinitive in the subject to swimming we end up with the
   equivalent (and less awkward) sentence,

   → The cars is broken. [✘]
   → Swimming is fun. → is > swimming →  is ✓ swimming 
   
   We can grade it correctly.

  Compound subjects are also a bear. Take
  
   → Sleeping in the backseat of the car, Katherine and John snored.

   This could be converted to,

   → Sleeping in the backseat of the car, they snored. [✓]

   But how to know that the subject wasn't 'the car, Katherine and John'? 

   It's important to remove prepositional phrases so we don't get,

   → Sleeping in the backseat of they snored. [✘]
   
   Instead, we end up with,

   → Sleeping, they snored. [✓]

   What a pleasure to vectorize a 3 word sentence!


With these 5 major mistakes in mind, we hope to greatly improve the efficacy of
our model. Whether we will be able to accurately extract all this information
remains to be seen.  I have high hopes.

Updates soon.

Quill.org.
