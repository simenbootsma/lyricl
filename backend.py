import pandas as pd

GIVEN_WORDS = ['a', 'the', 'an', 'no', 'when', 'over', 'under', 'are', 'of', 'with', 'than', 'then', 'or', 'as',
                 'from', 'in', 'out', 'and', 'which', 'is', 'across', 'after', 'about', 'where', 'into', 'but', 'along',
                 'have', 'on', 'been', 'from', 'until', 'since', 'among', 'if', 'be', 'to', 'that', 'this', 'between',
                 'off']
CHARACTERS = [',', '.', '\n', '(', ')', '"', '-', ' ', '?', '!']


def tuple_for_word(word, guesses):
    is_last_guess = len(guesses) > 0 and word.lower() == guesses[-1]
    is_good_guess = is_word_guessed(word, guesses)
    n = len(word) - len(str(len(word)))
    redacted = ' ' * n + str(len(word))
    cls = '' if is_good_guess else 'redacted'
    if is_last_guess:
        cls = 'last-guess'
    wrd = word if is_good_guess else redacted
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


def number_of_occurences(filepath, word):
    with open(filepath, 'r') as f:
        text = f.read()
    text = text.lower().replace("'", "")
    for c in CHARACTERS:
        text = text.replace(c, ' ')
    all_words = text.split(' ')
    word = word.lower().replace("'", "")
    return sum([w == word for w in all_words])


def process_song(filepath, guesses=None):
    if guesses is None:
        guesses = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    dash_ind = lines[0].index('-')
    lines[0] = lines[0][dash_ind+1:] + '  -  ' + lines[0][:dash_ind]

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


def get_year(song_path):
    rank = get_top2000_rank(song_path)
    df = pd.read_excel('NPORadio2-Top-2000-2024.xlsx', engine='openpyxl')
    year = df[df['Notering'] == rank]['Jaartal'].values[0]
    return year


def get_top2000_rank(song_path):
    return int(song_path[-8:-4])


if __name__ == "__main__":
    process_song('static/data/songs/song4.txt')


