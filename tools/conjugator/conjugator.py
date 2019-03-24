# -*- coding: utf-8 -*-

# (C) 2010 Dan Bravender - licensed under the AGPL 3.0

from hangeul import join, lead, vowel, padchim, find_vowel_to_append, match, Geulja
from pronunciation import pronunciation

def no_padchim_rule(characters):
    '''no_padchim_rule is a helper function for defining merges where a 
        character will take the padchim of a merged character if the first 
        character doesn't already have a padchim, .e.g. 습 -> 가 + 습니다 -> 갑니다.
     '''
    def rule(x, y):
        if not padchim(x[-1]) and y[0] in characters:
            return ('borrow padchim', x[:-1] + join(lead(x[-1]), 
                                                    vowel(x[-1]), 
                                                    padchim(y[0])) +
                                       y[1:])
    return rule

def vowel_contraction(vowel1, vowel2, new_vowel):
    '''vowel contraction is a helper function for defining common contractions 
        between a character without a padchim and a character that starts with 
        u'ᄋ', e.g. ㅐ + ㅕ -> ㅐ when applied to 해 + 였 yields 했.
     '''
    def rule(x, y):
        if match(x[-1], '*', vowel1, None) and \
           match(y[0], 'ᄋ', vowel2):
            return ('vowel contraction [%s + %s -> %s]' % 
                               (vowel1, vowel2, new_vowel),
                    x[:-1] + 
                    join(lead(x[-1]), 
                         new_vowel, 
                         padchim(y[0])) + 
                    y[1:])
    return rule

def drop_l(x, y):
    if padchim(x[-1]) == 'ᆯ':
        conjugation.reasons.append('drop ㄹ')
        return x[:-1] + join(lead(x[-1]), vowel(x[-1])) + y

def drop_l_and_borrow_padchim(x, y):
    if padchim(x[-1]) == 'ᆯ':
        conjugation.reasons.append('drop %s borrow padchim' % padchim(x[-1]))
        return x[:-1] + join(lead(x[-1]),
                             vowel(x[-1]),
                             padchim(y[0])) + y[1:]
def insert_eh(characters):
    def rule(x, y):
        if padchim(x[-1]) and y[0] in characters:
            return ('padchim + consonant -> insert 으', x + '으' + y)
    return rule

# merge rules is a list of rules that are applied in order when merging a verb 
#             stem with a tense ending
merge_rules = []

merge_rules.append(no_padchim_rule(['을', '습', '읍', '는', '음']))

merge_rules.append(lambda x, y: padchim(x[-1]) == 'ᆯ' and y[0] == '음' and \
                   ['ㄹ + ㅁ -> ᆱ', x[:-1] + join(lead(x[-1]), vowel(x[-1]), 'ᆱ')])

# vowel contractions
merge_rules.append(vowel_contraction('ㅐ', 'ㅓ', 'ㅐ'))
merge_rules.append(vowel_contraction('ㅡ', 'ㅓ', 'ㅓ'))
merge_rules.append(vowel_contraction('ㅜ', 'ㅓ', 'ㅝ'))
merge_rules.append(vowel_contraction('ㅗ', 'ㅏ', 'ㅘ'))
merge_rules.append(vowel_contraction('ㅚ', 'ㅓ', 'ㅙ'))
merge_rules.append(vowel_contraction('ㅙ', 'ㅓ', 'ㅙ'))
merge_rules.append(vowel_contraction('ㅘ', 'ㅓ', 'ㅘ'))
merge_rules.append(vowel_contraction('ㅝ', 'ㅓ', 'ㅝ'))
merge_rules.append(vowel_contraction('ㅏ', 'ㅏ', 'ㅏ'))
merge_rules.append(vowel_contraction('ㅡ', 'ㅏ', 'ㅏ'))
merge_rules.append(vowel_contraction('ㅣ', 'ㅓ', 'ㅕ'))
merge_rules.append(vowel_contraction('ㅓ', 'ㅓ', 'ㅓ'))
merge_rules.append(vowel_contraction('ㅓ', 'ㅣ', 'ㅐ'))
merge_rules.append(vowel_contraction('ㅏ', 'ㅣ', 'ㅐ'))
merge_rules.append(vowel_contraction('ㅑ', 'ㅣ', 'ㅒ'))
merge_rules.append(vowel_contraction('ㅒ', 'ㅓ', 'ㅒ'))
merge_rules.append(vowel_contraction('ㅔ', 'ㅓ', 'ㅔ'))
merge_rules.append(vowel_contraction('ㅕ', 'ㅓ', 'ㅕ'))
merge_rules.append(vowel_contraction('ㅏ', 'ㅕ', 'ㅐ'))
merge_rules.append(vowel_contraction('ㅖ', 'ㅓ', 'ㅖ'))
merge_rules.append(vowel_contraction('ㅞ', 'ㅓ', 'ㅞ'))

# Don't append 으 to ㄹ irregulars

merge_rules.append(lambda x, y: padchim(x[-1]) == 'ᆯ' and y[0] == '면' and \
                   ('join', x + y))


# 으 insertion
merge_rules.append(insert_eh(['면', '세', '십']))

# default rule - just append the contents
merge_rules.append(lambda x, y: ('join', x + y))

def apply_rules(x, y, verbose=False, rules=[]):
    '''apply_rules concatenates every element in a list using the rules to 
        merge the strings
     '''
    for i, rule in enumerate(rules):
        output = rule(x, y)
        if output:
            conjugation.reasons.append('%s (%s + %s -> %s)' % 
                                       (output[0] and output[0] or '', 
                                        x, 
                                        y, 
                                        output[1]))
            return output[1]

merge = lambda x, y: apply_rules(x, y, rules=merge_rules, verbose=False)

class conjugation:
    '''conjugation is a singleton decorator that simply builds a list of 
        all the conjugation rules
     '''
    def __init__(self):
        self.tenses = {}
        self.tense_order = []
        self.reasons = []

    def perform(self, infinitive, regular=False):
        '''perform returns the result of the application of all of the
            conjugation rules on one infinitive
         '''
        results = []
        for tense in self.tense_order:
            self.reasons = []
            c = self.tenses[tense](infinitive, regular)
            p = pronunciation(c)
            tense = tense.replace('_', ' ')
            results.append((tense, c, p, self.reasons))
        return results
    
    def __call__(self, f):
        self.tense_order.append(f.__name__)
        self.tenses.update({f.__name__: f})
        return f

conjugation = conjugation()

both_regular_and_irregular = [
    '일', '곱', '파묻', '누르', '묻', '이르',
    '되묻', '썰', '붓', '들까불', '굽', '걷',
    '뒤까불', '까불'
]

not_p_irregular = dict([('털썩이잡', True), ('넘겨잡', True), ('우접', True), ('입', True), ('맞접', True), ('문잡', True), ('다잡', True), ('까뒤집', True), ('배좁', True), ('목잡', True), ('끄집', True), ('잡', True), ('옴켜잡', True), ('검잡', True), ('되순라잡', True), ('내씹', True), ('모집', True), ('따잡', True), ('엇잡', True), ('까집', True), ('겹집', True), ('줄통뽑', True), ('버르집', True), ('지르잡', True), ('추켜잡', True), ('업', True), ('되술래잡', True), ('되접', True), ('좁디좁', True), ('더위잡', True), ('말씹', True), ('내뽑', True), ('집', True), ('걸머잡', True), ('휘어잡', True), ('꿰입', True), ('황잡', True), ('에굽', True), ('내굽', True), ('따라잡', True), ('맞뒤집', True), ('둘러업', True), ('늘잡', True), ('끄잡', True), ('우그려잡', True), ('어줍', True), ('언걸입', True), ('들이곱', True), ('껴잡', True), ('곱 접', True), ('훔켜잡', True), ('늦추잡', True), ('갈아입', True), ('친좁', True), ('희짜뽑', True), ('마음잡', True), ('개미잡', True), ('옴씹', True), ('치잡', True), ('그러잡', True), ('움켜잡', True), ('씹', True), ('비집', True), ('꼽', True), ('살잡', True), ('죄입', True), ('졸잡', True), ('가려잡', True), ('뽑', True), ('걷어잡', True), ('헐잡', True), ('돌라입', True), ('덧잡', True), ('얕잡', True), ('낫잡', True), ('부여잡', True), ('맞붙잡', True), ('걸입', True), ('주름잡', True), ('걷어입', True), ('빌미잡', True), ('개잡', True), ('겉잡', True), ('안쫑잡', True), ('좁', True), ('힘입', True), ('걷잡', True), ('바르집', True), ('감씹', True), ('짓씹', True), ('손잡', True), ('포집', True), ('붙잡', True), ('낮잡', True), ('책잡', True), ('곱잡', True), ('흉잡', True), ('뒤집', True), ('땡잡', True), ('어림잡', True), ('덧껴입', True), ('수줍', True), ('뒤잡', True), ('꼬집', True), ('예굽', True), ('덮쳐잡', True), ('헛잡', True), ('되씹', True), ('낮추잡', True), ('날파람잡', True), ('틀어잡', True), ('헤집', True), ('남의달잡', True), ('바로잡', True), ('흠잡', True), ('파잡', True), ('얼추잡', True), ('손꼽', True), ('접', True), ('차려입', True), ('골라잡', True), ('거머잡', True), ('후려잡', True), ('머줍', True), ('넉장뽑', True), ('사로잡', True), ('덧입', True), ('껴입', True), ('얼입', True), ('우집', True), ('설잡', True), ('늦잡', True), ('비좁', True), ('고르잡', True), ('때려잡', True), ('떼집', True), ('되잡', True), ('홈켜잡', True), ('내곱', True), ('곱씹', True), ('빼입', True), ('들이굽', True), ('새잡', True), ('이르집', True), ('떨쳐입', True)])
not_s_irregular = dict([('내솟', True), ('빗', True), ('드솟', True), ('비웃', True), ('뺏', True), ('샘솟', True), ('벗', True), ('들이웃', True), ('솟', True), ('되뺏', True), ('빼앗', True), ('밧', True), ('애긋', True), ('짜드라웃', True), ('어그솟', True), ('들솟', True), ('씻', True), ('빨가벗', True), ('깃', True), ('벌거벗', True), ('엇', True), ('되빼앗', True), ('웃', True), ('앗', True), ('헐벗', True), ('용솟', True), ('덧솟', True), ('발가벗', True), ('뻘거벗', True), ('날솟', True), ('치솟', True)])

not_d_irregular = dict([('맞받', True), ('내딛', True), ('내리받', True), ('벋', True), ('뒤닫', True), ('주고받', True), ('공얻', True), ('무뜯', True), ('물어뜯', True), ('여닫', True), ('그러묻', True), ('잇닫', True), ('덧묻', True), ('되받', True), ('뻗', True), ('올리닫', True), ('헐뜯', True), ('들이닫', True), ('활걷', True), ('겉묻', True), ('닫', True), ('창받', True), ('건네받', True), ('물손받', True), ('들이받', True), ('강요받', True), ('내리벋', True), ('받', True), ('이어받', True), ('부르걷', True), ('응받', True), ('검뜯', True), ('인정받', True), ('내려딛', True), ('내쏟', True), ('내리뻗', True), ('너름받', True), ('세받', True), ('내 돋', True), ('돌려받', True), ('쥐어뜯', True), ('껴묻', True), ('본받', True), ('뒤받', True), ('강종받', True), ('내리닫', True), ('떠받', True), ('테받', True), ('내받', True), ('흠뜯', True), ('두남받', True), ('치받', True), ('부르돋', True), ('대받', True), ('설굳', True), ('처닫', True), ('얻', True), ('들이돋', True), ('돋', True), ('죄받', True), ('쏟', True), ('씨받', True), ('딱장받', True), ('치걷', True), ('믿', True), ('치벋', True), ('버림받', True), ('북돋', True), ('딛', True), ('치고받', True), ('욱걷', True), ('물려받', True), ('뜯', True), ('줴뜯', True), ('넘겨받', True), ('안받', True), ('내뻗', True), ('내리쏟', True), ('벋딛', True), ('뒤묻', True), ('뻗딛', True), ('치뻗', True), ('치닫', True), ('줄밑걷', True), ('굳', True), ('내닫', True), ('내림받', True)])

not_h_irregular = dict([('들이좋', True), ('터놓', True), ('접어놓', True), ('좋', True), ('풀어놓', True), ('내쌓', True), ('꼴좋', True), ('치쌓', True), ('물어넣', True), ('잇닿', True), ('끝닿', True), ('그러넣', True), ('뽕놓', True), ('낳', True), ('내리찧', True), ('힘닿', True), ('내려놓', True), ('세놓', True), ('둘러놓', True), ('들놓', True), ('맞찧', True), ('잡아넣', True), ('돌라쌓', True), ('덧쌓', True), ('갈라땋', True), ('주놓', True), ('갈라놓', True), ('들이닿', True), ('집어넣', True), ('닿', True), ('의좋', True), ('막놓', True), ('내놓', True), ('들여놓', True), ('사놓', True), ('썰레놓', True), ('짓찧', True), ('벋놓', True), ('찧', True), ('침놓', True), ('들이찧', True), ('둘러쌓', True), ('털어놓', True), ('담쌓', True), ('돌라놓', True), ('되잡아넣', True), ('끌어넣', True), ('덧놓', True), ('맞닿', True), ('처넣', True), ('빻', True), ('뻥놓', True), ('내리쌓', True), ('곱놓', True), ('설레발놓', True), ('우겨넣', True), ('놓', True), ('수놓', True), ('써넣', True), ('널어놓', True), ('덮쌓', True), ('연닿', True), ('헛놓', True), ('돌려놓', True), ('되쌓', True), ('욱여넣', True), ('앗아넣', True), ('올려놓', True), ('헛방놓', True), ('날아놓', True), ('뒤놓', True), ('업수놓', True), ('가로놓', True), ('맞놓', True), ('펴놓', True), ('내켜놓', True), ('쌓', True), ('끙짜놓', True), ('들이쌓', True), ('겹쌓', True), ('기추놓', True), ('넣', True), ('불어넣', True), ('늘어놓', True), ('긁어놓', True), ('어긋놓', True), ('앞넣', True), ('눌러놓', True), ('땋', True), ('들여쌓', True), ('빗놓', True), ('사이좋', True), ('되놓', True), ('헛불놓', True), ('몰아넣', True), ('먹놓', True), ('밀쳐놓', True), ('살닿', True), ('피새놓', True), ('빼놓', True), ('하차놓', True), ('틀어넣', True)])

not_l_euh_irregular = dict([('우러르', True), ('따르', True), ('붙따르', True), ('늦치르', True), ('다다르', True), ('잇따르', True), ('치르', True)])

not_l_irregular = dict()

def after_last_space(infinitive):
    return infinitive.split(' ')[-1]

def is_s_irregular(infinitive, regular=False):
    if regular: 
        return False
    return match(infinitive[-1], '*', '*', 'ᆺ') and \
           not not_s_irregular.get(after_last_space(infinitive), False)

def is_l_irregular(infinitive, regular=False):
    if regular:
        return False
    return match(infinitive[-1], '*', '*', 'ᆯ') and \
           not not_l_irregular.get(after_last_space(infinitive), False)

def is_l_euh_irregular(infinitive, regular=False):
    if regular:
        return False
    return match(infinitive[-1], 'ᄅ', 'ㅡ', None) and \
           not not_l_euh_irregular.get(after_last_space(infinitive), False)

def is_h_irregular(infinitive, regular=False):
    if regular:
        return False
    return (padchim(infinitive[-1]) == 'ᇂ' or infinitive[-1] == '러') and \
           not not_h_irregular.get(after_last_space(infinitive), False)

def is_p_irregular(infinitive, regular=False):
    if regular:
        return False
    return match(infinitive[-1], '*', '*', 'ᆸ') and \
           not not_p_irregular.get(after_last_space(infinitive), False)

def is_d_irregular(infinitive, regular=False):
    if regular:
        return False
    return match(infinitive[-1], '*', '*', 'ᆮ') and \
           not not_d_irregular.get(after_last_space(infinitive), False)

verb_types = {
    'ㅅ 불규칙 동사 (irregular verb)': is_s_irregular,
    'ㄹ 불규칙 동사 (irregular verb)': is_l_irregular,
    '르 불규칙 동사 (irregular verb)': is_l_euh_irregular,
    'ㅎ 불규칙 동사 (irregular verb)': is_h_irregular,
    'ㅂ 불규칙 동사 (irregular verb)': is_p_irregular,
    'ㄷ 불규칙 동사 (irregular verb)': is_d_irregular
}

def verb_type(infinitive):
    for irregular_name, func in verb_types.items():
        if func(base(infinitive)):
            return irregular_name
    return 'regular verb'

@conjugation
def base(infinitive, regular=False):
    if infinitive[-1] == '다':
        return infinitive[:-1]
    else:
        return infinitive

@conjugation
def base2(infinitive, regular=False):
    infinitive = base(infinitive, regular)
    
    if infinitive == '아니':
        infinitive = Geulja('아니')
        infinitive.hidden_padchim = True
        return infinitive
    
    if infinitive == '뵙':
        return '뵈'
    
    if infinitive == '푸':
        return '퍼'
    
    new_infinitive = infinitive
    if is_h_irregular(infinitive, regular):
        new_infinitive = merge(infinitive[:-1] + 
                               join(lead(infinitive[-1]),
                                    vowel(infinitive[-1])),
                               '이')
        conjugation.reasons.append('ㅎ irregular (%s -> %s)' % (infinitive,
                                                                new_infinitive))
    # ㅂ irregular
    elif is_p_irregular(infinitive, regular):
        # only some verbs get ㅗ (highly irregular)
        if infinitive in ['묻잡'] or infinitive[-1] in ['돕', '곱']:
            new_vowel = 'ㅗ'
        else:
            new_vowel = 'ㅜ'
        new_infinitive = merge(infinitive[:-1] + 
                               join(lead(infinitive[-1]), 
                                    vowel(infinitive[-1])),
                               join('ᄋ', new_vowel))
        conjugation.reasons.append('ㅂ irregular (%s -> %s)' % (infinitive, 
                                                                new_infinitive))
    # ㄷ irregular
    elif is_d_irregular(infinitive, regular):
        new_infinitive = Geulja(infinitive[:-1] + join(lead(infinitive[-1]), 
                                                       vowel(infinitive[-1]), 
                                                       'ᆯ'))
        new_infinitive.original_padchim = 'ᆮ'
        conjugation.reasons.append('ㄷ irregular (%s -> %s)' % (infinitive,
                                                                new_infinitive))
    elif is_s_irregular(infinitive, regular):
        new_infinitive = Geulja(infinitive[:-1] + join(lead(infinitive[-1]), 
                                                       vowel(infinitive[-1])))
        new_infinitive.hidden_padchim = True
        conjugation.reasons.append('ㅅ irregular (%s -> %s [hidden padchim])' % 
                                   (infinitive, new_infinitive))
    return new_infinitive

@conjugation
def base3(infinitive, regular=False):
    infinitive = base(infinitive, regular)
    if infinitive == '아니':
        return '아니'
    if infinitive == '푸':
        return '푸'
    if infinitive == '뵙':
        return '뵈'
    if is_h_irregular(infinitive, regular):
        return infinitive[:-1] + join(lead(infinitive[-1]), vowel(infinitive[-1]))
    elif is_p_irregular(infinitive, regular):
        return infinitive[:-1] + join(lead(infinitive[-1]), vowel(infinitive[-1])) + '우'
    else:
        return base2(infinitive, regular)

@conjugation
def declarative_present_informal_low(infinitive, regular=False, further_use=False):
    infinitive = base2(infinitive, regular)
    if not further_use and ((infinitive[-1] == '이' and not getattr(infinitive, 'hidden_padchim', False)) or \
                            infinitive == '아니'):
        conjugation.reasons.append('야 irregular')
        return infinitive + '야'
    # 르 irregular
    if regular and infinitive == '이르':
        return '일러'

    if is_l_euh_irregular(infinitive, regular):
        new_base = infinitive[:-2] + join(lead(infinitive[-2]), 
                                          vowel(infinitive[-2]), 'ᆯ')
        if infinitive[-2:] in ['푸르', '이르']:
            new_base = new_base + join('ᄅ', 
                                       vowel(find_vowel_to_append(new_base)))
            conjugation.reasons.append('irregular stem + %s -> %s' % 
                                       (infinitive, new_base))
            return infinitive + '러'
        elif find_vowel_to_append(infinitive[:-1]) == '아':
            new_base += '라'
            conjugation.reasons.append('르 irregular stem change [%s -> %s]' %
                                       (infinitive, new_base))
            return new_base
        else:
            new_base += '러'
            conjugation.reasons.append('르 irregular stem change [%s -> %s]' %
                                       (infinitive, new_base))
            return new_base
    elif infinitive[-1] == '하':
        return merge(infinitive, '여')
    elif is_h_irregular(infinitive, regular):
        return merge(infinitive, '이')
    return merge(infinitive, find_vowel_to_append(infinitive))

@conjugation
def declarative_present_informal_high(infinitive, regular=False):
    infinitive = base2(infinitive, regular)
    if (infinitive[-1] == '이' and not getattr(infinitive, 'hidden_padchim', False)) or \
       infinitive == '아니':
        conjugation.reasons.append('에요 irregular')
        return infinitive + '에요'
    return merge(declarative_present_informal_low(infinitive, regular, further_use=True), '요')

@conjugation
def declarative_present_formal_low(infinitive, regular=False):
    if is_l_irregular(base(infinitive), regular):
        return drop_l_and_borrow_padchim(base(infinitive, regular), '는다')
    return merge(base(infinitive, regular), '는다')

@conjugation
def declarative_present_formal_high(infinitive, regular=False):
    if is_l_irregular(base(infinitive), regular):
        return drop_l_and_borrow_padchim(base(infinitive, regular), '습니다')
    return merge(base(infinitive, regular), '습니다')

@conjugation
def past_base(infinitive, regular=False):
    ps = declarative_present_informal_low(infinitive, regular, further_use=True)
    if find_vowel_to_append(ps) == '아':
        return merge(ps, '았')
    else:
        return merge(ps, '었')

@conjugation
def declarative_past_informal_low(infinitive, regular=False):
    return merge(past_base(infinitive, regular), '어')

@conjugation
def declarative_past_informal_high(infinitive, regular=False):
    return merge(declarative_past_informal_low(infinitive, regular), '요')

@conjugation
def declarative_past_formal_low(infinitive, regular=False):
    return merge(past_base(infinitive, regular), '다')

@conjugation
def declarative_past_formal_high(infinitive, regular=False):
    return merge(past_base(infinitive, regular), '습니다')

@conjugation
def future_base(infinitive, regular=False):
    if is_l_irregular(base(infinitive, regular)):
        return drop_l_and_borrow_padchim(base3(infinitive, regular), '을')
    return merge(base3(infinitive, regular), '을')

@conjugation
def declarative_future_informal_low(infinitive, regular=False):
    return merge(future_base(infinitive, regular), ' 거야')

@conjugation
def declarative_future_informal_high(infinitive, regular=False):
    return merge(future_base(infinitive, regular), ' 거예요')

@conjugation
def declarative_future_formal_low(infinitive, regular=False):
    return merge(future_base(infinitive, regular), ' 거다')

@conjugation
def declarative_future_formal_high(infinitive, regular=False):
    return merge(future_base(infinitive, regular), ' 겁니다')

@conjugation
def declarative_future_conditional_informal_low(infinitive, regular=False):
    return merge(base(infinitive, regular), '겠어')

@conjugation
def declarative_future_conditional_informal_high(infinitive, regular=False):
    return merge(base(infinitive, regular), '겠어요')

@conjugation
def declarative_future_conditional_formal_low(infinitive, regular=False):
    return merge(base(infinitive, regular), '겠다')

@conjugation
def declarative_future_conditional_formal_high(infinitive, regular=False):
    return merge(base(infinitive, regular), '겠습니다')

@conjugation
def inquisitive_present_informal_low(infinitive, regular=False):
    return merge(declarative_present_informal_low(infinitive, regular), '?')

@conjugation
def inquisitive_present_informal_high(infinitive, regular=False):
    return merge(declarative_present_informal_high(infinitive, regular), '?')

@conjugation
def inquisitive_present_formal_low(infinitive, regular=False):
    infinitive = base(infinitive, regular)
    if is_l_irregular(infinitive, regular):
        return drop_l(infinitive, '니?')
    return merge(infinitive, '니?')

@conjugation
def inquisitive_present_formal_high(infinitive, regular=False):
    infinitive = base(infinitive, regular)
    if is_l_irregular(infinitive, regular):
        return drop_l_and_borrow_padchim(infinitive, '습니까?')
    return merge(infinitive, '습니까?')

@conjugation
def inquisitive_past_informal_low(infinitive, regular=False):
    return declarative_past_informal_low(infinitive, regular) + '?'

@conjugation
def inquisitive_past_informal_high(infinitive, regular=False):
    return merge(declarative_past_informal_high(infinitive, regular), '?')

@conjugation
def inquisitive_past_formal_low(infinitive, regular=False):
    return merge(past_base(infinitive, regular), '니?')

@conjugation
def inquisitive_past_formal_high(infinitive, regular=False):
    return merge(past_base(infinitive, regular), '습니까?')

@conjugation
def imperative_present_informal_low(infinitive, regular=False):
    return declarative_present_informal_low(infinitive, regular)

@conjugation
def imperative_present_informal_high(infinitive, regular=False):
    if is_l_irregular(base(infinitive, regular)):
        return drop_l(base3(infinitive, regular), '세요')
    return merge(base3(infinitive, regular), '세요')

@conjugation
def imperative_present_formal_low(infinitive, regular=False):
    return merge(imperative_present_informal_low(infinitive, regular), '라')

@conjugation
def imperative_present_formal_high(infinitive, regular=False):
    if is_l_irregular(base(infinitive, regular)):
        return drop_l(base3(infinitive, regular), '십시오')
    return merge(base3(infinitive, regular), '십시오')

@conjugation
def propositive_present_informal_low(infinitive, regular=False):
    return declarative_present_informal_low(infinitive, regular)

@conjugation
def propositive_present_informal_high(infinitive, regular=False):
    return declarative_present_informal_high(infinitive, regular)

@conjugation
def propositive_present_formal_low(infinitive, regular=False):
    return merge(base(infinitive, regular), '자')

@conjugation
def propositive_present_formal_high(infinitive, regular=False):
    infinitive = base(infinitive)
    if is_l_irregular(infinitive, regular):
        return drop_l_and_borrow_padchim(base3(infinitive, regular), '읍시다')
    return merge(base3(infinitive, regular), '읍시다')

@conjugation
def connective_if(infinitive, regular=False):
    return merge(base3(infinitive, regular), '면')

@conjugation
def connective_and(infinitive, regular=False):
    infinitive = base(infinitive, regular)
    return merge(base(infinitive, regular), '고')

@conjugation
def nominal_ing(infinitive, regular=False):
    return merge(base3(infinitive, regular), '음')
