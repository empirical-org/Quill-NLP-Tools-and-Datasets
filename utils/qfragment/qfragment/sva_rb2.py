#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Rule based system for  detecting subject-verb agreement errors (V2)"""


'''
# Strategy

1. Drop adjectives, adverbs, determiners
2. Extract verb phrases and the noun they refer to
3. For each noun-verb pair, check that the noun and verb agree.

Hypothesis:
    We should be able to accurately determine SVA errors in past and present
    imperfective and present progressive indicative mood sentences. 

Baseline:
    - We can't detect that 'We seen some fish' is wrong.
    - We CAN detect 'I is a bad boy.'
    - '"While we were swimming at the lake, we seen some fish." flies under the
      radar
    - "While we were swimming at the lake, we begun the ceremony." does too.
    - We can't detect "While we were swimming at the lake, we bitten a cracker."
    - Or, "While we were swimming at the lake, we been chilling."
    - "He agreed me." is marked right.
    - "A fish bit me." is marked wrong.
    - "He walked store." is marked right.

Why do these errors exist?
    - We don't record if the verb is transitive or intransitive
        * most act as both, but only can pair with certain other verbs, "walk it
          back" is ok "walk the dog" is fine. "walk the store" is wrong. "Dance
          the potion" is wrong, "Dance the night away" is fine. 


TODO: finish this file



'''
