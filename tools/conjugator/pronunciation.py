# -*- coding: utf-8 -*-

# (C) 2009 Dan Bravender - licensed under the AGPL 3.0

from hangeul import join, lead, vowel, padchim, is_hangeul
from functools import reduce

padchim_to_lead = {
    'ᆨ': 'ᄀ',
    'ᆩ': 'ᄁ',
    'ᆫ': 'ᄂ',
    'ᆮ': 'ᄃ',
    'ᆯ': 'ᄅ',
    'ᆷ': 'ᄆ',
    'ᆸ': 'ᄇ',
    'ᆺ': 'ᄉ',
    'ᆻ': 'ᄊ',
    'ᆼ': 'ᄋ',
    'ᆽ': 'ᄌ',
    'ᆾ': 'ᄎ',
    'ᆿ': 'ᄏ',
    'ᇀ': 'ᄐ',
    'ᇁ': 'ᄑ',
    'ᇂ': 'ᄒ'
}

def move_padchim_to_replace_eung(x, y):
    if padchim(x[-1]) in list(padchim_to_lead.keys()) and lead(y[0]) == 'ᄋ':
        return (x[:-1] + join(lead(x[-1]),
                             vowel(x[-1])),
                join(padchim_to_lead[padchim(x[-1])],
                     vowel(y[0]),
                     padchim(y[0])) + \
                y[1:])


def change_padchim_pronunciation(to, changers):
    def rule(x, y):
        if padchim(x[-1]) in changers:
            return (x[:-1] + join(lead(x[-1]),
                                 vowel(x[-1]),
                                 to),
                    y)
    return rule

def consonant_combination_rule(x_padchim='*', y_lead='*', 
                               new_padchim='*', new_lead='*',
                               y_vowel=None):
    def rule(x, y):
        if y_vowel and vowel(y[0]) != y_vowel:
            return
        if (padchim(x[-1]) == x_padchim or x_padchim == '*') and \
           (lead(y[0]) == y_lead or y_lead == '*'):
            return (x[:-1] + join(lead(x[-1]),
                                 vowel(x[-1]), 
                                 new_padchim == '*' and padchim(x[-1]) or new_padchim),
                    join(new_lead == '*' and lead(y[0]) or new_lead,
                         vowel(y[0]),
                         padchim(y[0])) + \
                    y[1:])
    return rule

# WARNING: Please be careful when adding/modifying rules since padchim 
#          and lead characters are different Unicode characters. Please see:
#          http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html


# Rules from http://en.wikibooks.org/wiki/Korean/Advanced_Pronunciation_Rules

# merge rules is a list of rules that are applied in order when merging 
#             pronunciation rules
merge_rules = []

def skip_non_hangeul(x, y):
    if not is_hangeul(x[-1]):
        return (x, y, True)

merge_rules.append(skip_non_hangeul)

merge_rules.append(consonant_combination_rule('ᇂ', 'ᄋ', None, 'ᄋ'))

# ㄱㄴ becomes ㅇㄴ
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄂ', 'ᆼ', 'ᄂ'))
# ㄱㅁ becomes ㅇㅁ
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄆ', 'ᆼ', 'ᄆ'))
# ㅋㄴ becomes ㅇㄴ
merge_rules.append(consonant_combination_rule('ᆿ', 'ᄂ', 'ᆼ', 'ᄂ'))
# ㅋㅁ becomes ㅇㅁ
merge_rules.append(consonant_combination_rule('ᆿ', 'ᄆ', 'ᆼ', 'ᄆ'))
# ㄷㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆮ', 'ᄂ', 'ᆫ', 'ᄂ'))
# ㄷㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᆮ', 'ᄆ', 'ᆫ', 'ᄆ'))
# ㅅㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆺ', 'ᄂ', 'ᆫ', 'ᄂ'))
# ㅆㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆻ', 'ᄂ', 'ᆫ', 'ᄂ'))
# ㅅㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᆺ', 'ᄆ', 'ᆫ', 'ᄆ'))
# ㄱ ㅆ becomes ㄱ ㅆ
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄉ', 'ᆨ', 'ᄊ'))
# ㅈㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆽ', 'ᄂ', 'ᆫ', 'ᄂ'))
#ㅈㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᆽ', 'ᄆ', 'ᆫ', 'ᄆ'))
#ㅊㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆾ', 'ᄂ', 'ᆫ', 'ᄂ'))
#ㅊㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᆾ', 'ᄆ', 'ᆫ', 'ᄆ'))
#ㅌㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᇀ', 'ᄂ', 'ᆫ', 'ᄂ'))
#ㅌㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᇀ', 'ᄆ', 'ᆫ', 'ᄆ'))
# ㅎㄴ becomes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄂ', 'ᆫ', 'ᄂ'))
# ㅎㅁ becomes ㄴㅁ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄆ', 'ᆫ', 'ᄆ'))
# ㅂㄴ becomes ㅁㄴ
merge_rules.append(consonant_combination_rule('ᆸ', 'ᄂ', 'ᆷ', 'ᄂ'))
#ㅂㅁ becomes ㅁㅁ
merge_rules.append(consonant_combination_rule('ᆸ', 'ᄆ', 'ᆷ', 'ᄆ'))
#ㅍㄴ becomes ㅁㄴ
merge_rules.append(consonant_combination_rule('ᇁ', 'ᄂ', 'ᆷ', 'ᄂ'))
#ㅍㅁ becomes ㅁㅁ
merge_rules.append(consonant_combination_rule('ᇁ', 'ᄆ', 'ᆷ', 'ᄆ'))
# ㄱㅎ becomes ㅋ
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄒ', None, 'ᄏ'))
# ㅎㄱ becomes ㅋ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄀ', None, 'ᄏ'))
# ㅎㄷ becomes ㅌ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄃ', None, 'ᄐ'))
# ㄷㅎ becomes ㅌ
merge_rules.append(consonant_combination_rule('ᆮ', 'ᄒ', None, 'ᄐ'))
# ㅂㅎ becomes ㅍ
merge_rules.append(consonant_combination_rule('ᆸ', 'ᄒ', None, 'ᄑ'))
# ㅎㅂ becomes ㅍ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄇ', None, 'ᄑ'))
# ㅈㅎ becomes ㅊ
merge_rules.append(consonant_combination_rule('ᆽ', 'ᄒ', None, 'ᄎ'))
# ㅎㅈ becomes ㅊ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄌ', None, 'ᄎ'))
# ㅎㅅ becomes ㅆ
merge_rules.append(consonant_combination_rule('ᇂ', 'ᄉ', None, 'ᄊ'))
#ㄷ이 becomes 지
merge_rules.append(consonant_combination_rule('ᆮ', 'ᄋ', None, 'ᄌ',
                                              y_vowel='ㅣ'))
#ㅌ이 becomes 치
merge_rules.append(consonant_combination_rule('ᇀ', 'ᄋ', None, 'ᄎ', 
                                              y_vowel='ㅣ'))
#ㄱㄹ becomes ㅇㄴ
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄅ', 'ᆼ', 'ᄂ'))
#ㄴㄹ becomes ㄹㄹ // TODO: (not sure how to fix this) also sometimes ㄴㄴ
merge_rules.append(consonant_combination_rule('ᆫ', 'ᄅ', 'ᆯ', 'ᄅ'))
# ㅁㄹ becomes ㅁㄴ
merge_rules.append(consonant_combination_rule('ᆷ', 'ᄅ', 'ᆷ', 'ᄂ'))
# ㅇㄹ becomes ㅇㄴ
merge_rules.append(consonant_combination_rule('ᆼ', 'ᄅ', 'ᆼ', 'ᄂ'))
# ㅂㄹ becomes ㅁㄴ
merge_rules.append(consonant_combination_rule('ᆸ', 'ᄅ', 'ᆷ', 'ᄂ'))
# ㅅ ㅎ becomes ㅌ
merge_rules.append(consonant_combination_rule('ᆺ', 'ᄒ', None, 'ᄐ'))

# 받침 followed by ㅇ: replace ㅇ with 받침 (use second 받침 if there are two). Otherwise, 받침 followed by consonant:
merge_rules.append(move_padchim_to_replace_eung)

#    * ㄱ, ㅋ: like ㄱ
#    * ㄷ, ㅅ, ㅈ, ㅊ, ㅌ, ㅎ: like ㄷ
#    * ㅂ, ㅍ: like ㅂ

# Double padchim rules
merge_rules.append(consonant_combination_rule('ᆱ', 'ᄋ', 'ᆯ', 'ᄆ'))
merge_rules.append(consonant_combination_rule('ᆱ', '*', 'ᆷ', '*'))

merge_rules.append(consonant_combination_rule('ᆶ', '*', None, 'ᄅ'))

merge_rules.append(consonant_combination_rule('ᆬ', 'ᄋ', 'ᆫ', 'ᄌ'))
merge_rules.append(consonant_combination_rule('ᆬ', '*', 'ᆫ', '*'))

# 학교 -> 학꾜
merge_rules.append(consonant_combination_rule('ᆨ', 'ᄀ', 'ᆨ', 'ᄁ'))

# 밥솥-> 밥쏟
merge_rules.append(consonant_combination_rule('ᆸ', 'ᄉ', 'ᆸ', 'ᄊ'))

# 있습니다 -> 이씀니다
merge_rules.append(consonant_combination_rule('ᆻ', 'ᄉ', None, 'ᄊ'))

merge_rules.append(change_padchim_pronunciation(changers=('ᆺ', 'ᆻ', 'ᆽ', 'ᆾ', 'ᇀ', 'ᇂ'), to='ᆮ'))

merge_rules.append(change_padchim_pronunciation(changers=('ᇁ',), to='ᆸ'))

merge_rules.append(consonant_combination_rule('ᆮ', 'ᄃ', None, 'ᄄ'))

merge_rules.append(lambda x, y: (x, y))

def apply_rules(x, y):
    '''apply_rules concatenates every element in a list using the rules to 
        merge the strings
     '''
    for i, rule in enumerate(merge_rules):
        merge = rule(x, y)
        if merge and len(merge) == 3:
            x, y, stop = merge
            if stop:
                return x + y
        elif merge:
            x, y = merge
    return x + y

def pronunciation(word):
    # Adding a null character to the end of the string and stripping it off
    # so that rules that require more than one character still get called
    return reduce(apply_rules, iter(word + chr(0)))[:-1]
