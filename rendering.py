import re

def reorder_myanmar_syllable(syllable: str) -> str:
    CONSONANT = "က-အ"
    MEDIALS = "ျြွှ"
    VOWELS = "ါ-ဲေါ"
    TONES = "ံ-း"
    DIACRITICS = "္-်"
    PRE_VOWEL = "ေ"
    JOINERS = "‌‍"

    # Remove joiners
    # syllable = re.sub(f"[{JOINERS}]", "", syllable)

    # Step 1: Move pre-vowel (ေ) **after medials but before vowels**
    if PRE_VOWEL in syllable:
        # Extract pre-vowel
        syllable = syllable.replace(PRE_VOWEL, "")
        # Find first consonant cluster
        match = re.match(rf"([{CONSONANT}][{DIACRITICS}]*)([{MEDIALS}]*)", syllable)
        if match:
            base, medials = match.groups()
            rest = syllable[len(base + medials):]
            syllable = base + medials + PRE_VOWEL + rest

    # Step 2: Reorder components
    pattern = rf"([{CONSONANT}])([{MEDIALS}]*)([{VOWELS}]*)([{TONES}]*)([{DIACRITICS}]*)"

    def reorder_match(match):
        consonant, medials, vowels, tones, diacritics = match.groups()
        return consonant + medials + vowels + tones + diacritics

    return re.sub(pattern, reorder_match, syllable)



def split_myanmar_syllables(text: str):
    """
    Groups Myanmar characters into syllables based on Unicode rules.
    """
    CONSONANT = "က-အ"
    MEDIALS = "ျြွှ"
    VOWELS = "ါ-ဲ"
    TONES = "ံ-း"
    DIACRITICS = "္-်"
    PRE_VOWEL = "ေ"

    pattern = (
        rf"({PRE_VOWEL}?)"  # Optional pre-vowel (ေ)
        rf"([{CONSONANT}])"  # Main consonant
        rf"([{DIACRITICS}]*)"  # Optional diacritics like '္'
        rf"([{MEDIALS}]*)"  # Optional medial signs like 'ျ'
        rf"([{VOWELS}]*)"  # Optional vowels
        rf"([{TONES}]*)"  # Optional tone marks
        rf"([{DIACRITICS}]*)"  # Optional diacritics like '်'
    )
    # Find all Myanmar syllables and non-Myanmar text
    matches = re.finditer(pattern + "|.", text)  # Keep everything
    return [match.group() for match in matches]  # Re
    #return re.findall(pattern, text)

def reorder_myanmar_text(text: str) -> str:
    """
    Reorders Myanmar text by correctly processing syllables.
    """
    syllables = split_myanmar_syllables(text)

    with open("myanmar_reordering_tmp.txt", "w", encoding="utf-8") as file:
        for syl in syllables:
            file.write("Input Text: " + ''.join(syl) + "\n")

    reordered_syllables = ["".join(reorder_myanmar_syllable("".join(syl))) for syl in syllables]
    return "".join(reordered_syllables)
