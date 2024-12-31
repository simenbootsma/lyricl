import flet as ft
from glob import glob
from backend import *
import numpy as np


GUESSES = []
HINTS = []
GAVE_UP = False
USERNAME = None
STATS = {'won': 0, 'lost': 0, 'n_guesses': []}
ALWAYS_SHOW_WORD_LENGTH = False
AUTO_SCROLL = True
STILL_PLAYING = True

CATEGORY = 'top2000'
files = glob('static/data/songs/{:s}_processed/*.txt'.format(CATEGORY))
# files = [fn for fn in files if get_year(fn, CATEGORY) == 1978]
SONG_PATH = files[np.random.randint(len(files))]
MAX_HINTS = 5
COLORS = ["green" + str(n) for n in [50] + list(range(100, 1000, 100))]
COLORS += [COLORS[-1] for _ in range(100)]
LEFT_COL_WIDTH = 500
RIGHT_COL_WIDTH = 400
COL_SPACING = 100
FULL_WIDTH = LEFT_COL_WIDTH + COL_SPACING + RIGHT_COL_WIDTH
COL_HEIGHT = 450


def main(page: ft.Page):
    global GUESSES, HINTS, GAVE_UP, SONG_PATH, MAX_HINTS, STATS, USERNAME, ALWAYS_SHOW_WORD_LENGTH, AUTO_SCROLL, CATEGORY

    def reveal_year(e):
        year_row.controls = [ft.Text("Year: ", size=22, width=60), ft.Text(str(get_year(SONG_PATH, CATEGORY)), size=22)]
        year_row.update()

    def reveal_rank(e):
        rank_row.controls = [ft.Text("Rank: ", size=22, width=60),
                             ft.Text('#' + str(get_top2000_rank(SONG_PATH)), size=22)]
        rank_row.update()

    year_row = ft.Row([ft.Text("Year: ", size=22, width=60),
                       ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_year, width=50)], spacing=5)
    rank_row = ft.Row([ft.Text("Rank: ", size=22, width=60),
                       ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_rank, width=50)], spacing=5)
    if CATEGORY != 'top2000':
        rank_row.visible = False
        rank_row.disabled = True

    def scroll_to_first_occurrence(word):
        line_num = first_occurrence_line(SONG_PATH, word)
        if line_num is not None and AUTO_SCROLL:
            if line_num == 0:
                lyrics_box.scroll_to(0, duration=1000)
            else:
                lyrics_box.scroll_to(key='line{:d}'.format(line_num-1), duration=1000)
            if word in GUESSES:
                GUESSES.remove(word)
                GUESSES.append(word)
            update()

    def add_guess(e):
        global MAX_HINTS
        last_guess = guess_field.value

        if last_guess == 'extra hint pls':
            MAX_HINTS += 1
            hint_button.text = "Hint ({:d}/{:d})".format(MAX_HINTS - len(HINTS), MAX_HINTS)
            hint_button.disabled = False
            hint_button.update()
            update()
            return

        last_guess = [last_guess] if ' ' not in last_guess else last_guess.split(' ')
        for lg in last_guess:
            lg = remove_accents(lg)
            if (lg != '') and (lg not in GIVEN_WORDS + GUESSES) and (not all([c in 'oah' for c in lg])):
                GUESSES.append(lg)
                guess_column.controls.insert(2, ft.Row([ft.Text(str(len(GUESSES)), size=22),
                                                        ft.Container(ft.Text(lg, size=22), on_click=lambda e: scroll_to_first_occurrence(e.control.content.value), key="guess_"+lg),
                                                        ft.Text(str(number_of_occurrences(SONG_PATH, lg)), size=22)],
                                                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=RIGHT_COL_WIDTH))

        update()

        if AUTO_SCROLL:
            scroll_to_first_occurrence(last_guess[-1].lower().replace("'", ""))
            if len(last_guess) == 1 and last_guess[0].lower().replace("'", "") in GUESSES[:-1]:
                guess_column.scroll_to(key='guess_'+last_guess[0].lower().replace("'", ""), duration=500)

    def update():
        global STILL_PLAYING
        guess_column.update()
        guess_field.value = ''
        guess_field.update()
        lyrics_box.controls = generate_lyrics_rows(SONG_PATH)
        lyrics_box.update()
        guess_field.focus()

        prog_ring.value = percentage_guessed(SONG_PATH, GUESSES)
        prog_text.value = "{:.0f}%".format(100 * prog_ring.value)
        prog_ring.update()
        prog_text.update()

        if not STILL_PLAYING:
            hint_button.disabled = True
            hint_button.update()
            add_next_button()

    def add_next_button():
        give_up_next_button.content = next_button
        give_up_next_button.update()

    def give_hint(e):
        occ = occurrence_list(SONG_PATH)
        occ = [tup for tup in occ if (not is_word_guessed(tup[0], GUESSES)) and (not is_word_in_title(SONG_PATH, tup[0])) and (not all([c in 'oah' for c in tup[0]]))]
        ind = int((len(occ)-1) * 0.5 * (1 + (len(HINTS)+1)/MAX_HINTS))

        while ind >= len(occ):
            ind -= 1
        if ind < 0:
            return

        hint = occ[ind][0]
        HINTS.append(hint)
        hint_button.text = "Hint ({:d}/{:d})".format(MAX_HINTS - len(HINTS), MAX_HINTS)
        if len(HINTS) == MAX_HINTS:
            hint_button.disabled = True
        hint_button.update()

        # add hint to guess column
        GUESSES.append(hint)
        guess_column.controls.insert(2, ft.Row([ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=ft.Colors.AMBER_300),
                                                ft.Container(ft.Text(hint, size=22, color=ft.Colors.AMBER_300),
                                                             on_click=lambda ev: scroll_to_first_occurrence(hint), key="guess_"+hint),
                                                ft.Text(str(occ[ind][1]), size=22, color=ft.Colors.AMBER_300)],
                                               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=RIGHT_COL_WIDTH))

        update()

    def give_up(e):
        global GAVE_UP, STILL_PLAYING
        GAVE_UP = True
        close_alert(e)
        STILL_PLAYING = False
        update()

    def close_alert(e):
        give_up_alert.open = False
        e.control.page.update()

    def open_alert(e):
        e.control.page.overlay.append(give_up_alert)
        give_up_alert.open = True
        e.control.page.update()

    def next_song(e):
        global GUESSES, HINTS, GAVE_UP, SONG_PATH, STILL_PLAYING
        GUESSES, HINTS = [], []
        GAVE_UP = False

        give_up_next_button.content = give_up_button
        give_up_next_button.update()

        hint_button.text = "Hint ({:d}/{:d})".format(MAX_HINTS - len(HINTS), MAX_HINTS)
        hint_button.disabled = False
        hint_button.update()

        year_row.controls = [ft.Text("Year: ", size=22, width=60),
                             ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_year, width=50)]
        year_row.update()

        rank_row.controls = [ft.Text("Rank: ", size=22, width=60),
                             ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_rank, width=50)]
        if CATEGORY != 'top2000':
            rank_row.visible = False
            rank_row.disabled = True
        rank_row.update()

        guess_column.controls = guess_column.controls[:2]
        guess_column.update()

        SONG_PATH = files[np.random.randint(len(files))]

        STILL_PLAYING = True

        update()

    def open_menu(e):
        e.control.page.end_drawer = menu
        menu.open = True
        e.control.page.update()

    def dismiss_menu(e):
        # print(menu.open)
        menu.open = False
        e.control.page.update()

    def open_stats_dialog(e):
        e.control.page.overlay.append(stats_dialog)
        stats_dialog.open = True
        won, played = STATS['won'], STATS['won'] + STATS['lost']
        perc_won_text = "(--%)" if played == 0 else "({:.0f}%)".format(100 * won/played)
        if won == 0:
            min_g, avg_g, max_g = '-', '-', '-'
        else:
            min_g, avg_g, max_g = str(min(STATS['n_guesses'])), str(int(sum(STATS['n_guesses'])/len(STATS['n_guesses']))), str(max(STATS['n_guesses']))
        stats_dialog.content = ft.Column([ft.Row([ft.Icon(ft.Icons.BAR_CHART), ft.Text("Lyricl stats", size=22)]),
                                          ft.Divider(),
                                          ft.Text("Songs guessed", weight=ft.FontWeight.BOLD),
                                          ft.Text("{:d}/{:d}  ".format(won, played) + perc_won_text),
                                          ft.Text(''),
                                          ft.Text("Number of guesses", weight=ft.FontWeight.BOLD),
                                          ft.Row([ft.Text("Min."), ft.Text('Avg.'), ft.Text('Max.')],
                                                 width=200, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                          ft.Row([ft.Text(min_g), ft.Text(avg_g), ft.Text(max_g)],
                                                 width=200, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                          ])
        e.control.page.update()

    def toggle_auto_scroll(e):
        global AUTO_SCROLL
        AUTO_SCROLL = not AUTO_SCROLL

    def toggle_word_length(e):
        global ALWAYS_SHOW_WORD_LENGTH
        ALWAYS_SHOW_WORD_LENGTH = not ALWAYS_SHOW_WORD_LENGTH
        update()

    def change_category(e):
        global CATEGORY, SONG_PATH

        cats = ['top2000', 'kryst', 'hollands']
        cat = [c for c in cats if c in e.control.content.src][0]

        # print('changed category from {:s} to {:s}'.format(CATEGORY, cat))
        CATEGORY = cat
        song_files = glob('static/data/songs/{:s}_processed/*.txt'.format(CATEGORY))
        SONG_PATH = song_files[np.random.randint(len(song_files))]

        cats.remove(CATEGORY)
        category_menu.items = [
            ft.PopupMenuItem(content=ft.Image('static/{:s}_logo.png'.format(s), height=30),
                             on_click=change_category)
            for s in other_cats
        ]
        category_menu.content = ft.Image('static/{:s}_logo.png'.format(CATEGORY), height=30)
        category_menu.update()

        rank_row.visible = cat == 'top2000'
        rank_row.disabled = cat != 'top2000'
        rank_row.update()
        update()

    give_up_alert = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Are you sure you want to give up?"),
        actions=[
            ft.TextButton("Yes", on_click=give_up),
            ft.TextButton("No", on_click=close_alert),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        barrier_color=ft.Colors.with_opacity(0.3, ft.Colors.RED_500)
    )

    stats_dialog = ft.AlertDialog(content=ft.Column([ft.Text("Lyricl stats", size=22)]))

    give_up_button = ft.ElevatedButton('Give up', on_click=open_alert, bgcolor=ft.Colors.RED_800, color='white', width=80)
    next_button = ft.ElevatedButton('Next', icon=ft.Icons.NAVIGATE_NEXT, on_click=next_song, bgcolor=ft.Colors.BLUE_800, color='white', width=80)

    give_up_next_button = ft.AnimatedSwitcher(
        give_up_button,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=500,
        reverse_duration=100,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
    )

    menu_button = ft.IconButton(icon=ft.Icons.MENU, on_click=open_menu)
    menu = ft.NavigationDrawer(
        controls=[ft.Container(ft.Column([
            ft.Text('Show word length', weight=ft.FontWeight.BOLD, size=20),
            ft.Row([ft.Text("Always"), ft.Switch(on_change=toggle_word_length, value=not ALWAYS_SHOW_WORD_LENGTH), ft.Text("On hover")]),
            ft.Text(''),
            ft.Text('Auto-scroll', weight=ft.FontWeight.BOLD, size=20),
            ft.Row([ft.Text("Off"), ft.Switch(on_change=toggle_auto_scroll, value=AUTO_SCROLL), ft.Text("On")]),
            ft.Text(''),
            ft.TextButton('Show stats', on_click=open_stats_dialog, icon=ft.Icons.BAR_CHART)
        ], spacing=10), padding=20)],
        on_dismiss=dismiss_menu
    )

    lyrics_box = ft.Column(generate_lyrics_rows(SONG_PATH), width=LEFT_COL_WIDTH, height=COL_HEIGHT, scroll=ft.ScrollMode.ALWAYS)
    hint_button = ft.ElevatedButton('Hint ({:d}/{:d})'.format(MAX_HINTS, MAX_HINTS), on_click=give_hint, icon=ft.Icons.TIPS_AND_UPDATES)
    prog_ring = ft.ProgressRing(value=percentage_guessed(SONG_PATH, GUESSES), stroke_width=10, height=15, width=15, bgcolor='grey')
    prog_text = ft.Text("{:.0f}%".format(100 * prog_ring.value), size=22)

    guess_field = ft.TextField(hint_text='Enter guess', on_submit=add_guess)
    submit_button = ft.ElevatedButton('Submit', on_click=add_guess, height=50, width=80, style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10)))
    guess_column = ft.Column([
        ft.Row([guess_field, submit_button],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=RIGHT_COL_WIDTH),
        ft.Row([ft.Text('#', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Guess', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Hits', size=26, weight=ft.FontWeight.BOLD)],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=RIGHT_COL_WIDTH),
    ], width=RIGHT_COL_WIDTH, height=COL_HEIGHT, scroll=ft.ScrollMode.HIDDEN)

    button_row = ft.Row([hint_button, ft.Row([prog_ring, prog_text]), give_up_next_button], width=RIGHT_COL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    other_cats = ['top2000', 'kryst', 'hollands']
    other_cats.remove(CATEGORY)
    # category_menu = ft.PopupMenuButton(items=[
    #     ft.PopupMenuItem(content=ft.Image('static/{:s}_logo.png'.format(s), height=30), on_click=change_category)
    #     for s in other_cats
    # ], content=ft.Image('static/{:s}_logo.png'.format(CATEGORY), height=30))
    top2000_logo = ft.Image('static/top2000_logo.png', height=30)
    header_row = ft.Row([
        ft.Text("Lyricl", size=30, weight=ft.FontWeight.BOLD),
        top2000_logo,
        menu_button
    ], width=FULL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    layout = ft.SafeArea(ft.Column([
        header_row,
        ft.Divider(height=9, thickness=2),
        ft.Row([ft.Column([
            ft.Row([year_row, rank_row], spacing=50), lyrics_box]),
            ft.Column([button_row, guess_column], spacing=20)
        ], width=FULL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]))

    page.add(layout)
    page.window.height = 650
    page.window.width = 1100
    # page.scroll = ft.ScrollMode.HIDDEN
    page.update()


def generate_lyrics_rows(song_path):
    global GUESSES, GAVE_UP, STATS, ALWAYS_SHOW_WORD_LENGTH, STILL_PLAYING

    def show_length(e: ft.ControlEvent):
        if not ALWAYS_SHOW_WORD_LENGTH:
            txt = e.control.content
            if txt.bgcolor != '#00000000':
                txt.color = COLORS[len(txt.value)] if txt.color == 'black' else 'black'
            txt.update()

    def word_style(word, style):
        if style == 'redacted' and ALWAYS_SHOW_WORD_LENGTH:
            return {'color': 'black', 'bgcolor': COLORS[len(word)]}
        if style == 'redacted':
            return {'color': COLORS[len(word)], 'bgcolor': COLORS[len(word)]}
        elif style == 'won':
            return {'color': 'green', 'bgcolor': '#00000000'}
        elif style == 'lost':
            return {'color': 'red700', 'bgcolor': '#00000000'}
        elif style == 'last-guess':
            return {'color': 'orange900', 'bgcolor': '#00000000'}
        return {'color': 'white', 'bgcolor': '#00000000'}

    lyrics = process_song(song_path, GUESSES)

    # Check if game is won
    is_game_won = all([style != 'redacted' for _, style in lyrics[0][:lyrics[0].index(('-', ''))]])
    if is_game_won:
        lyrics = process_song(song_path, GUESSES, won=True)
        if STILL_PLAYING:
            STATS['n_guesses'].append(len(GUESSES))
            STATS['won'] += 1
            STILL_PLAYING = False

    # Check if player gave up
    if GAVE_UP:
        lyrics = process_song(song_path, GUESSES, lost=True)
        STATS['lost'] += 1

    title_row = ft.Row([ft.Container(ft.Text(word, **word_style(word, style), size=24), on_hover=show_length)
                        for word, style in lyrics[0]], spacing=3, wrap=True, key='line0')
    other_rows = [ft.Row([ft.Container(ft.Text(word, **word_style(word, style), size=18), on_hover=show_length)
                          for word, style in line], spacing=3, wrap=True, key='line{:d}'.format(i))
                  for i, line in enumerate(lyrics[1:])]
    return [title_row] + other_rows


if __name__ == '__main__':
    ft.app(main)

