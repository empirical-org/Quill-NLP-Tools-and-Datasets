# Subject Verb Agreement Model Construction

Construct a TensorFlow model that can detect subject-verb agreement errors.

## Running the model builder

### Prerequisites

You should have access to a database with a set of 'deflated' vectors in it by
this point. 

```bash
max=# select * from vectors limit 10;
  id   |                           vector                            | label
-------+-------------------------------------------------------------+-------
 98605 | {"indices": {"59": 1, "29": 1}, "reductions": 5555}         |     1
 98606 | {"indices": {"1": 1, "13": 1, "15": 1}, "reductions": 5555} |     1
 98607 | {"indices": {}, "reductions": 5555}                         |     0
 98608 | {"indices": {"6": 1}, "reductions": 5555}                   |     0
 98609 | {"indices": {"24": 1, "1": 1, "3": 2}, "reductions": 5555}  |     0
 98610 | {"indices": {}, "reductions": 5555}                         |     0
 98611 | {"indices": {"7": 1}, "reductions": 5555}                   |     1
 98612 | {"indices": {"57": 1}, "reductions": 5555}                  |     1
 98613 | {"indices": {"19": 1, "18": 1}, "reductions": 5555}         |     1
 98614 | {"indices": {"1": 1}, "reductions": 5555}                   |     0
 ```
 
This model constructor will
 
 1. inflate the vector into a numpy array
 2. train a tensorflow model based on those numpy vectors.

### Running it

[instructions in progress (sorry!)]

 

