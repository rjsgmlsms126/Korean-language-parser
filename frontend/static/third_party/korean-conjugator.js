/* the conjugate returns a conjugate verb, but it should be checked for tense, past tense will take present tense verb and then add something to the the verb, and then add an additional letter after */

/* Additional Functions */
// reference: http://www.programminginkorean.com/programming/hangul-in-unicode/composing-syllables-in-unicode/
// input: hangul character
// output: returns an array of components that make up the given hangul
// ex: breakdown('린') outputs [5,20,4]
const breakdown = (input) => {
  let total = parseInt(input.charCodeAt(0).toString(16), 16)

  const letterArray = []
  total -= 44032
  const initialValue = Math.floor(total / 588)
  letterArray.push(initialValue)
  total -= (588 * initialValue)
  const medialValue = Math.floor(total / 28)
  letterArray.push(medialValue)
  const finalValue = total - (28 * medialValue)
  if (finalValue > 0) {
    letterArray.push(finalValue)
  }
  return letterArray
}

// input: array of 2 or 3 numbers representing modern jamo (components) that make up a hangul syllable
// output: a hangul character
const combineSymbols = (input) => {
  let unicodeTotal = (input[0] * 588) + (input[1] * 28) + 44032
  if (input.length === 3) {
    unicodeTotal += input[2]
  }
  return String.fromCharCode(unicodeTotal)
}

const allInfo = {
  noun: {
    tense: ['subject', 'object']
  },
  adjective: {
    tense: ['present', 'past', 'future', 'prepared', 'truncated', 'conditional', 'state'],
    formality: ['formal', 'casual']
  },
  verb: {
    tense: ['present', 'past', 'future', 'present continuous', 'prepared', 'present truncated',
      'past truncated', 'future truncated', 'conditional', 'state'],
    formality: ['formal', 'casual']
  }
}

class Korean {
  getAllInfo () {
    return allInfo
  }

  conjugate (word, info) {
  // Format for rulesObject: { tense: 'Present', formality: 'Casual/Formal'}
  // TODO: test if word is verb, return to avoid switch
    let result = ''
    if (info.wordType && info.wordType.toLowerCase() === 'noun') {
      return this.doNoun(word, info.tense.toLowerCase())
    }
    // Else, conjugate adjective or verb
    switch (info.tense.toLowerCase()) {
      case 'present':
        result = this.doPresent(word)
        break
      case 'past':
        result = this.doPast(word)
        break
      case 'future':
        result = this.doFuture(word)
        break
      case 'present continuous':
        result = this.doPresentContinuous(word)
        break
      case 'prepared': {
        const futureConjugation = this.doFuture(word)
        // simply drop the ' 거야' at the end of future conjugation
        return futureConjugation.substring(0, futureConjugation.length - 3)
      }
      case 'truncated':
      case 'present truncated':
        return word.substring(0, word.length - 1)
      case 'past truncated': {
        const pastConjugation = this.doPast(word)
        return pastConjugation.substring(0, pastConjugation.length - 1)
      }
      case 'future truncated': {
        const futureConjugation = this.doFuture(word)
        return futureConjugation.substring(0, futureConjugation.length - 3)
      }
      case 'conditional':
        return this.doConditional(word)
      case 'state':
        return this.doState(word, info.wordType)
      default:
        return `Could not find any adjective/verb rules for ${info.tense}`
    }

    if (info.formality && info.formality.toLowerCase() === 'formal') {
      // for future tense, change 야 to 예 before making it formal
      if (info.tense.toLowerCase() === 'future') {
        return `${result.substring(0, result.length - 1)}예요`
      }
      return `${result}요`
    }
    return result
  }

  // Nouns
  doNoun (word, tense) {
    const wordLength = word.length
    // break down the last character to check if it has a bottom consonant
    const lastCharArray = breakdown(word[wordLength - 1])
    if (tense === 'subject') {
      if (lastCharArray.length > 2) {
        return `${word}이`
      }
      return `${word}가`
    } else if (tense === 'object') {
      if (lastCharArray.length > 2) {
        return `${word}을`
      }
      return `${word}를`
    }
    return `Could not find any noun rules for ${tense}`
  }

  // Adjectives and verbs
  doPresent (word) {
    const wordLength = word.length
    let conjugate = ''
    // if the ending is 'ha' then convert to 'hae'
    if (word[wordLength - 2] === '하') {
      conjugate = word.slice(0, wordLength - 2)
      return conjugate.concat('해')
    } else if (word[wordLength - 2] === '르') {
      const sliced = word.slice(0, wordLength - 2)
      let stem = []
      // when the stem word is longer than one letter
      if (sliced.length > 1) {
        conjugate = sliced.slice(0, sliced.length - 1)
        stem = breakdown(sliced.charAt(sliced.length - 1))
      } else {
        stem = breakdown(word.slice(0, wordLength - 2))
      }
      stem.push(8) // ㄹ
      const newSyllable = `${conjugate}${combineSymbols(stem)}`
      switch (stem[stem.length - 2]) {
        case 0:
        case 8:
          // ㅏ and ㅗ are followed by 라
          return newSyllable.concat('라')
        default:
          // other vowels are followed by 러
          return newSyllable.concat('러')
      }
    } else {
      /* breakdown the word to find out the 2nd to last character's letter */
      const brokeWord = breakdown(word[wordLength - 2])
      const brokeLength = brokeWord.length
      const syllableEnd = brokeWord[brokeLength - 1]
      const stemWord = word.slice(0, wordLength - 2)
      let newSyllable = brokeWord.slice(0, brokeLength - 1)

      // If it has a bottom consonant:
      if (brokeLength > 2) {
        const medialValue = brokeWord[brokeLength - 2]
        switch (syllableEnd) {
          case 1: // ㄱ, ㄴㅈ, ㄹ, ㄹㄱ
          case 5:
          case 8:
          case 9:
            switch (medialValue) { // Check the vowel
              case 0:
              case 8:
                // if ㅏ or ㅗ
                return `${word.slice(0, wordLength - 1)}아`
              default:
                // for any other vowel
                return `${word.slice(0, wordLength - 1)}어`
            }
          case 7: // ㄷ
            switch (medialValue) { // Check the vowel
              case 0:
              case 8:
                // if ㅏ or ㅗ
                if (stemWord) {
                  // if it has stemWord in front, replace ㄷ with: ㄹ (8)
                  newSyllable.push(8)
                  newSyllable = combineSymbols(newSyllable)
                  return `${stemWord + newSyllable}아`
                }
                return `${word.slice(0, wordLength - 1)}아`
              case 4:
              case 18:
                // if ㅓ or ㅡ, replace with: ㄹ (8)
                newSyllable.push(8)
                newSyllable = combineSymbols(newSyllable)
                return `${stemWord + newSyllable}어`
              default:
                // for all other vowels
                return `${word.slice(0, wordLength - 1)}어`
            }
          case 17: // ㅂ
            switch (medialValue) { // Check the vowel
              case 0:
              case 4:
              case 8:
              case 13:
              case 16:
                // if ㅏ,ㅓ,ㅕ,ㅗ,ㅜ,ㅟ remove ㅂ and add 워
                newSyllable = combineSymbols(newSyllable)
                return `${stemWord + newSyllable}워`
              default:
                // for all other vowels
                return `${word.slice(0, wordLength - 1)}어`
            }
          default:
            return `${word.slice(0, wordLength - 1)}어`
        }
      }

      // If it ends in a vowel
      switch (syllableEnd) {
        case 0:
        case 1:
        case 4:
          // if the vowel is ㅏor ㅓ leave alone
          return word.slice(0, wordLength - 1)
        case 8:
          // replace with: ㅘ (9)
          // concat back to word
          newSyllable.push(9)
          newSyllable = combineSymbols(newSyllable)
          return stemWord + newSyllable
        case 13:
          // 13 (ㅜ) convert to 14 (ㅝ)
          newSyllable.push(14)
          newSyllable = combineSymbols(newSyllable)
          if (wordLength <= 2) {
            return newSyllable
          }
          return stemWord + newSyllable
        case 18:
          if (stemWord) {
            // vowel ㅡ replace with ㅏ (0)
            newSyllable.push(0)
          } else {
            // vowel ㅡ replace with ㅓ (4)
            newSyllable.push(4)
          }
          newSyllable = combineSymbols(newSyllable)
          if (wordLength <= 2) {
            return newSyllable
          }
          return stemWord + newSyllable
        case 20:
          // vowel ㅣ replace with ㅕ(6)
          newSyllable.push(6)
          newSyllable = combineSymbols(newSyllable)
          if (wordLength <= 2) {
            return newSyllable
          }
          return stemWord + newSyllable
        default:
          // any other vowel
          conjugate = word.slice(0, wordLength - 1)
          return conjugate.concat('어')
      }
    }
  } // end of presentWord function

  doState (word, wordType) {
    const wordLength = word.length
    /* breakdown the word to find out the 2nd to last character's letter */
    const brokeWord = breakdown(word[wordLength - 2])
    const brokeLength = brokeWord.length
    const syllableEnd = brokeWord[brokeLength - 1]
    const stemWord = word.slice(0, wordLength - 2)
    let newSyllable = brokeWord.slice(0, brokeLength - 1)

    // If it has a bottom consonant:
    if (brokeLength > 2) {
      const medialValue = brokeWord[brokeLength - 2]
      switch (syllableEnd) {
        case 17: // ㅂ
          switch (medialValue) {
            case 0:
            case 4:
            case 8:
            case 13:
              // if ㅏ,ㅓ,ㅕ,ㅗ,ㅜ, remove ㅂ and add 운
              newSyllable = combineSymbols(newSyllable)
              return `${stemWord + newSyllable}운`
            default:
              // for all other vowels
              if (stemWord || (wordType && wordType.toLowerCase() === 'verb')) {
                return `${word.slice(0, wordLength - 1)}는`
              }
              return `${word.slice(0, wordLength - 1)}은`
          }
        default:
          if (stemWord || (wordType && wordType.toLowerCase() === 'verb')) {
            return `${word.slice(0, wordLength - 1)}는`
          }
          return `${word.slice(0, wordLength - 1)}은`
      }
    }
    // Else it ends in a vowel:
    brokeWord.push(4) // add ㄴ as bottom consonant
    return stemWord + combineSymbols(brokeWord)
  }

  doPresentContinuous (word) {
    return `${word.substring(0, word.length - 1)}고있어`
  }

  doPast (word) {
    const presentTense = this.doPresent(word)
    let origin = ''
    let brokenWord = ''

    if (!presentTense) {
      return 'conjugation error'
    }

    if (presentTense.length > 1) {
      origin = presentTense.slice(0, presentTense.length - 1)
      brokenWord = breakdown(presentTense.charAt(presentTense.length - 1))
    } else {
      brokenWord = breakdown(presentTense)
    }
    brokenWord.push(20)
    return `${origin}${combineSymbols(brokenWord)}어`
  }

  doFuture (word) {
    const preStem = word.slice(0, -2)
    const stem = breakdown(word[word.length - 2])
    if (stem.length < 3) { // does not have bottom consonant
      stem.push(8) // push ㄹ as bottom consonant
      return `${preStem}${combineSymbols(stem)} 거야`
    }

    // check the bottom consonant
    switch (stem[stem.length - 1]) {
      case 19: // ㅅ
        if (stem[stem.length - 2] === 18 ||
          stem[stem.length - 2] === 0
        ) { // special case: if medial jamo is 'ㅡ ㅏ'
          stem.pop()
          return `${preStem}${combineSymbols(stem)}을 거야`
        }
        return `${preStem}${combineSymbols(stem)}을 거야`
      case 17: // ㅂ
        if (stem[stem.length - 2] === 20) { // special case: if medial jamo is 'ㅣ'
          return `${preStem}${combineSymbols(stem)}을 거야`
        }
        stem.pop()
        return `${preStem}${combineSymbols(stem)}울 거야`
      case 8: // ㄹ
        return `${preStem}${combineSymbols(stem)} 거야`
      case 7: // ㄷ
        // This condition skips and thus handles the irregular case of ㅏㄷ like 닫다
        if (stem[stem.length - 2] !== 0 || preStem) {
          stem[stem.length - 1] = 8 // replace the consonant with ㄹ
        }
        return `${preStem}${combineSymbols(stem)}을 거야`
      default:
        return `${preStem}${combineSymbols(stem)}을 거야`
    }
  }

  doConditional (word) {
    const stem = breakdown(word[word.length - 2])
    const stemLen = stem.length
    const truncatedWord = word.substring(0, word.length - 1)
    if (stemLen < 3) { // does not have bottom consonant
      return truncatedWord
    }

    // irregular case:
    if (stem[stemLen - 1] === 7 && // if bottom consonant is ㄷ
      (stem[stemLen - 2] === 4 || stem[stemLen - 2] === 18)) { // if vowel is ㅓ or ㅡ
      stem[stemLen - 1] = 8 // replace it with ㄹ
    }
    return `${combineSymbols(stem)}으`
  }
} // end for class

export { Korean }
