import pandas as pd

GIVEN_WORDS = ['a', 'the', 'an', 'no', 'when', 'over', 'under', 'are', 'of', 'with', 'than', 'then', 'or', 'as',
                 'from', 'in', 'out', 'and', 'which', 'is', 'across', 'after', 'about', 'where', 'into', 'but', 'along',
                 'have', 'on', 'been', 'from', 'until', 'since', 'among', 'if', 'be', 'to', 'that', 'this', 'between',
                 'off']
CHARACTERS = [',', '.', '\n', '(', ')', '"', '-', ' ', '?', '!', '&']


def tuple_for_word(word, guesses):
    is_last_guess = len(guesses) > 0 and (word.lower().replace("'", "") == guesses[-1].replace("'", ""))
    is_good_guess = is_word_guessed(word, guesses)
    n = len(word) - len(str(len(word)))
    redacted = ' ' * n + str(len(word))
    cls = '' if is_good_guess else 'redacted'
    if is_last_guess:
        cls = 'last-guess'
    wrd = word if is_good_guess else redacted

    # Handle all oooh, ahhh ahah, ahah, ohoh
    if all([c in 'oah' for c in word]):
        wrd, cls = word, ''
    return wrd, cls


def is_word_guessed(word, guesses):
    apo_less_guess = [g.replace("'", "") for g in guesses]
    word = word.lower()
    if word in guesses or word in GIVEN_WORDS:
        return True
    word = word.replace("'", "")
    if word in apo_less_guess or word in GIVEN_WORDS:
        return True
    return False


def is_word_in_title(filepath, word):
    with open(filepath, 'r') as f:
        text = f.read()
    title = text.split('\n')[0]
    title = title.lower().replace("'", "")
    for c in CHARACTERS:
        title = title.replace(c, ' ')
    return word in title


def number_of_occurrences(filepath, word):
    with open(filepath, 'r') as f:
        text = f.read()
    text = text.lower().replace("'", "")
    for c in CHARACTERS:
        text = text.replace(c, ' ')
    all_words = text.split(' ')
    word = word.lower().replace("'", "")
    return sum([w == word for w in all_words])


def first_occurrence_line(filepath, word):
    word = word.lower().replace("'", "")
    with open(filepath, 'r') as f:
        text = f.read()
    lines = text.split('\n')
    for i, ln in enumerate(lines):
        ln = ln.lower().replace("'", "")
        for c in CHARACTERS:
            ln = ln.replace(c, " ")
        ln = " " + ln + " "
        if " " + word + " " in ln:
            return i
    return None  # word does not occur


def occurrence_list(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    text = text.lower().replace("'", "")
    for c in CHARACTERS:
        text = text.replace(c, ' ')
    all_words = text.split(' ')
    count = {}
    for w in all_words:
        count[w] = 1 if w not in count else count[w] + 1
    return sorted([(w, c) for w, c in count.items()], key=lambda x: x[1])


def percentage_guessed(filepath, guesses):
    with open(filepath, 'r') as f:
        text = f.read()
    text = text.lower().replace("'", "")
    for c in CHARACTERS:
        text = text.replace(c, ' ')
    all_words = text.split(' ')
    n_shown = sum([is_word_guessed(w, guesses) for w in all_words])
    return n_shown/len(all_words)


def process_song(filepath, guesses=None, won=False, lost=False):
    if guesses is None:
        guesses = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    lines[-1] += '\n'

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
                tup = tuple_for_word(temp, guesses)
                if (won or lost) and tup[1] == 'redacted':
                    tup = (temp, 'won' if won else 'lost')
                cur_line.append(tup)
                temp = ''
                wc += 1
            else:
                temp += c
        lyrics.append(cur_line)
    return lyrics


def get_year(filepath):
    rank = get_top2000_rank(filepath)
    df = pd.read_excel('NPORadio2-Top-2000-2024.xlsx', engine='openpyxl')
    year = df[df['Notering'] == rank]['Jaartal'].values[0]
    return year


def get_top2000_rank(filepath):
    return int(filepath[-8:-4])


if __name__ == "__main__":
    process_song('static/data/songs/song4.txt')


