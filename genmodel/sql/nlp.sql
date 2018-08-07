
/* NLP JOBS OBJECT STORE */
CREATE TABLE IF NOT EXISTS nlpjobs (
  id serial PRIMARY KEY NOT NULL,
  data jsonb,
  created timestamp with time zone default now(),
  updated timestamp with time zone default now()
);

/* NLP DATA OBJECT STORE */
CREATE TABLE IF NOT EXISTS nlpdata (
  id serial PRIMARY KEY NOT NULL,
  name varchar UNIQUE,
  data jsonb,
  created timestamp with time zone default now(),
  updated timestamp with time zone default now()
);

/* explanation:
A jobs object store is shared for all nlp jobs. NLP jobs may use data, or
produce data, another object store is therefore extant to store data that might
be shared. 

For example, 

take a job called nlp-catsort-job, which generates a model that can, given
arbitrary text, determine if it is a name that would be good for a cat. The job
has 3 steps,

  1. load data
  2. preprocess
  3. train tensorflow model

Load Data.

First we must add a bunch of cat names to our database, 1.6 million of them.
Since we might use this cat data in a different job also, it will be stored in
the data object store.

INSERT INTO nlp-data (name, data) VALUES (
  'cat_names', '["gigi", "fifi", "sweetie", "Jamie   ", "Hunter", "hunter", "grahm", ...]'); 

Great, we've inserted our 1.6 million cat names into the database.

Preprocess.

Next we have to preprocess.  Trailing whitespace, capitalization, duplicate
removal, etc. We can easily grab out cat names dataset and use it for all our
needs.  Then we can add the preprocessed data to our job (since it was generated
by our job after all and will be used by the job). or to the data object store
if that is more sensible. For now, let's imagine that we have a distributed
system that pre-processes the cat names in parallel. Everytime a cat name is
preprocessed it
  
  1. gets added to a queue to be written to the database by a single writer.
  2. gets written to the database

This order ensures that the object representing the current run of the job is
not being updated in two places at once.

UPDATE nlp-jobs
SET data = jsonb_set(
  data::jsonb,
  array['preprocessed_cat_names'],
  (data->'preprocessed_cat_names')::jsonb || '["jamie"]'::jsonb) 
WHERE id = 7;

Train.

To train, all we might have to do is read from the generated data. This might
involve adding temporary indexes before running select statements.
*/
