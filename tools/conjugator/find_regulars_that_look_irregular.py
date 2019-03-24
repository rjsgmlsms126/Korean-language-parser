# -*- coding: utf-8 -*-

from conjugator import *
import time

import sqlite3

c = sqlite3.connect('korean_verbs.sqlite3')

def is_s_irregular(infinitive):
    return match(base(infinitive)[-1], '*', '*', 'ᆺ')

def is_l_irregular(infinitive):
    return match(base(infinitive)[-1], 'ᄅ', 'ㅡ', None)

def is_h_irregular(infinitive):
    return (padchim(base(infinitive)[-1]) == 'ᇂ' or base(infinitive)[-1] == '러')

def is_p_irregular(infinitive):
    return match(base(infinitive)[-1], '*', '*', 'ᆸ')

def is_d_irregular(infinitive):
    return match(base(infinitive)[-1], '*', '*', 'ᆮ')

irregular_types = {
    'ㅅ irregular': is_s_irregular,
    'ㄹ irregular': is_l_irregular,
    'ㅎ irregular': is_h_irregular,
    'ㅂ irregular': is_p_irregular,
    'ㄷ irregular': is_d_irregular
}

both_regular_and_irregular = [
    '일다',
    '곱다',
    '파묻다',
    '누르다',
    '묻다',
    '이르다',
    '되묻다',
    '썰다',
    '붓다',
    '들까불다',
    '굽다',
    '걷다',
    '뒤까불다',
    '이다',
    '까불다'
]

from collections import defaultdict
results = defaultdict(lambda: [])

data = c.execute('select infinitive.word, conj.word from entry infinitive inner join entry conj on conj.infinitive_id = infinitive.id and conj.verb_tense_id = 2 where infinitive.infinitive_id = 0').fetchall()

for infinitive, conjugated in data:
    if infinitive in both_regular_and_irregular:
        continue
    for irregular_name, func in irregular_types.items():
        if func(infinitive):
            if declarative_present_informal_low(infinitive, True) == conjugated:
                results['not ' + irregular_name].append(infinitive[:-1])

# I just wanted to use pprint... but man... Python and unicode => :-(
# Python 3 makes me happy... unicode everywhere as it should be...
# but I can't use it everywhere yet ;-)

for key, value in results.items():
    print("'%s': [%s]".encode('utf-8') % (key, ', '.join(["(u'%s', True)" % x for x in list(set(value))])))

