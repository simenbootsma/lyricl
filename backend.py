GIVEN_WORDS = ['a', 'the', 'an', 'no', 'when', 'over', 'under', 'are', 'of', 'with', 'than', 'then', 'or', 'as',
                 'from', 'in', 'out', 'and', 'which', 'is', 'across', 'after', 'about', 'were', 'into', 'but', 'along',
                 'have', 'on', 'been', 'from', 'until', 'since', 'among', 'if', 'be', 'to', 'that', 'this', 'between',
                 'had', 'down', 'up', 'off', 'being', "i", "i'm", "don't", "wasn't", "haven't", "aren't", "shouldn't", "can't", "couldn't"]
CHARACTERS = [',', '.', '\n', '(', ')', '"', '-', ' ', '?', '!']


def tuple_for_word(word, guesses):
    is_last_guess = len(guesses) > 0 and word.lower() == guesses[-1]
    n = len(word) - 1
    redacted = '-' * (n - n // 2) + str(len(word)) + '-' * (n // 2)
    cls = '' if word.lower() in guesses + GIVEN_WORDS else 'redacted'
    if is_last_guess:
        cls = 'last-guess'
    wrd = word if word.lower() in guesses + GIVEN_WORDS else redacted
    return wrd, cls


def number_of_occurences(filepath, word):
    with open(filepath, 'r') as f:
        text = f.read()
    text = text.lower()
    for c in CHARACTERS:
        text = text.replace(c, ' ')
    words = text.split(' ')
    return sum([w == word.lower() for w in words])


def process_song(filepath, guesses=None):
    if guesses is None:
        guesses = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    lyrics = []
    for i, ln in enumerate(lines):
        temp = ''
        cur_line = []
        wc = 0
        for j, c in enumerate(ln[:-1]):
            if c in CHARACTERS:
                cur_line.append((c, ''))
                wc += 1
            elif ln[j+1] in CHARACTERS:
                temp += c
                cur_line.append(tuple_for_word(temp, guesses))
                temp = ''
                wc += 1
            else:
                temp += c
        lyrics.append(cur_line)
    return lyrics


if __name__ == "__main__":
    process_song('static/data/songs/song4.txt')


