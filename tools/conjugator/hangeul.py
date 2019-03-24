# -*- coding: utf-8 -*-

# (C) 2010 Dan Bravender - licensed under the AGPL 3.0

class Geulja(str):
    '''Geulja is used to track modifications that have been made to
        characters. Currently, it keeps track of characters' original
        padchims (for ㄷ -> ㄹ irregulars) and if the character has
        no padchim but should be treated as if it does (for ㅅ 
        irregulars). When substrings are extracted the Geulja class 
        keeps these markers for the last character only.
     '''
    hidden_padchim = False
    original_padchim = None
    
    def __getitem__(self, index):
        g = Geulja(str.__getitem__(self, index))
        # only keep the hidden padchim marker for the last item
        if index == -1:
            g.hidden_padchim = self.hidden_padchim
            g.original_padchim = self.original_padchim
        return g

def is_hangeul(character):
    assert len(character) == 1, 'is_hangeul only checks characters with a length of 1'

    if ord(character) >= ord('가') and ord(character) <= ord('힣'):
        return True
    return False

def find_vowel_to_append(string):
    for character in reversed(string):
        if character in ['뜨', '쓰', '트']:
            return '어'
        if vowel(character) == 'ㅡ' and not padchim(character):
            continue
        elif vowel(character) in ['ㅗ', 'ㅏ', 'ㅑ']:
            return '아'
        else:
            return '어'
    return '어'

# Equations lifted directly from:
# http://www.kfunigraz.ac.at/~katzer/korean_hangul_unicode.html

def join(lead, vowel, padchim=None):
    '''join returns the unicode character that is composed of the
       lead, vowel and padchim that are passed in.
    '''
    lead_offset = ord(lead) - ord('ᄀ')
    vowel_offset = ord(vowel) - ord('ㅏ')
    if padchim:
        padchim_offset = ord(padchim) - ord('ᆨ')
    else:
        padchim_offset = -1
    return chr(padchim_offset + (vowel_offset) * 28 + (lead_offset) * 588 + \
                  44032 + 1)

def lead(character):
    '''lead returns the first consonant in a geulja
    '''
    return chr(int((ord(character) - 44032) / 588) + 4352)

def vowel(character):
    padchim_character = padchim(character)
    # padchim returns a character or True if there is a hidden padchim, 
    # but a hidden padchim doesn't make sense for this offset
    if not padchim_character or padchim_character == True:
        padchim_offset = -1
    else:
        padchim_offset = ord(padchim_character) - ord('ᆨ')
    return chr(int(((ord(character) - 44032 - padchim_offset) % 588) / 28)+ \
                  ord('ㅏ'))

def padchim(character):
    '''padchim returns the unicode padchim (the bottom) of a geulja.
    '''
    if getattr(character, 'hidden_padchim', False):
        return True
    if getattr(character, 'original_padchim', False):
        return character.original_padchim
    p = chr(((ord(character) - 44032) % 28) + ord('ᆨ') - 1)
    if ord(p) == 4519:
        return None
    else:
        return p

def match(character, l='*', v='*', p='*'):
    '''match is a helper function that simplifies testing if
       geulja match patterns. * is used to represent any vowel or
       consonant.
    '''
    return (lead(character) == l or l == '*') and \
           (vowel(character) == v or v == '*') and \
           (padchim(character) == p or p == '*')
