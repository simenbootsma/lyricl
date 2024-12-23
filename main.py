import flet as ft
from glob import glob
from backend import *
import numpy as np


GUESSES = []
HINTS = []
GAVE_UP = False

files = glob('static/data/songs/Top2000/*.txt')
SONG_PATH = files[np.random.randint(len(files))]
COLORS = ["green" + str(n) for n in [50] + list(range(100, 1000, 100))]
COLORS += [COLORS[-1] for _ in range(50)]
LEFT_COL_WIDTH = 500
RIGHT_COL_WIDTH = 400
COL_SPACING = 100
FULL_WIDTH = LEFT_COL_WIDTH + COL_SPACING + RIGHT_COL_WIDTH
COL_HEIGHT = 500


def main(page: ft.Page):
    global GUESSES, HINTS, GAVE_UP, SONG_PATH

    def reveal_year(e):
        year_row.controls = [ft.Text("Year: ", size=22, width=60), ft.Text(str(get_year(SONG_PATH)), size=22)]
        year_row.update()

    def reveal_rank(e):
        rank_row.controls = [ft.Text("Rank: ", size=22, width=60),
                             ft.Text('#' + str(get_top2000_rank(SONG_PATH)), size=22)]
        rank_row.update()

    year_row = ft.Row([ft.Text("Year: ", size=22, width=60),
                       ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_year, width=50)], spacing=5)
    rank_row = ft.Row([ft.Text("Rank: ", size=22, width=60),
                       ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_rank, width=50)], spacing=5)

    def add_guess(e):
        last_guess = guess_field.value
        last_guess = [last_guess] if ' ' not in last_guess else last_guess.split(' ')
        for lg in last_guess:
            if lg != '' and lg not in GIVEN_WORDS + GUESSES:
                GUESSES.append(lg)
                guess_column.controls.insert(2, ft.Row([ft.Text(str(len(GUESSES)), size=22), ft.Text(lg, size=22),
                                                        ft.Text(str(number_of_occurrences(SONG_PATH, lg)), size=22)],
                                                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300))
        update()

    def update():
        guess_column.update()
        guess_field.value = ''
        guess_field.update()
        lyrics_box.controls, status = generate_lyrics_rows(SONG_PATH)
        lyrics_box.update()
        guess_field.focus()

        prog_ring.value = percentage_guessed(SONG_PATH, GUESSES)
        prog_text.value = "{:.0f}%".format(100 * prog_ring.value)
        prog_ring.update()
        prog_text.update()

        if not status:
            add_next_button()

    def add_next_button():
        give_up_next_button.content = next_button
        give_up_next_button.update()

    def give_hint(e):
        occ = occurrence_list(SONG_PATH)
        occ = [tup for tup in occ if not is_word_guessed(tup[0], GUESSES) and not is_word_in_title(SONG_PATH, tup[0])]
        ind = int((len(occ)-1) * (len(HINTS)+6)/8)
        hint = occ[ind][0]
        HINTS.append(hint)
        hint_button.text = "Hint ({:d}/3)".format(3 - len(HINTS))
        if len(HINTS) == 3:
            hint_button.disabled = True
        hint_button.update()

        # add hint to guess column
        GUESSES.append(hint)
        guess_column.controls.insert(2, ft.Row([ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=ft.Colors.AMBER_300),
                                                ft.Text(hint, size=22, color=ft.Colors.AMBER_300),
                                                ft.Text(str(occ[ind][1]), size=22, color=ft.Colors.AMBER_300)],
                                               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300))

        update()

    def give_up(e):
        global GAVE_UP
        GAVE_UP = True
        close_alert(e)
        update()

    def close_alert(e):
        give_up_alert.open = False
        e.control.page.update()

    def open_alert(e):
        e.control.page.overlay.append(give_up_alert)
        give_up_alert.open = True
        e.control.page.update()

    def next_song(e):
        global GUESSES, HINTS, GAVE_UP, SONG_PATH
        GUESSES, HINTS = [], []
        GAVE_UP = False

        give_up_next_button.content = give_up_button
        give_up_next_button.update()

        SONG_PATH = files[np.random.randint(len(files))]

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

    lyrics_box = ft.Column(generate_lyrics_rows(SONG_PATH)[0], width=LEFT_COL_WIDTH, height=COL_HEIGHT, scroll=ft.ScrollMode.ALWAYS)
    hint_button = ft.ElevatedButton('Hint (3/3)', on_click=give_hint, icon=ft.Icons.TIPS_AND_UPDATES)
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
    ], width=RIGHT_COL_WIDTH, height=COL_HEIGHT, scroll=ft.ScrollMode.ADAPTIVE)

    button_row = ft.Row([hint_button, ft.Row([prog_ring, prog_text]), give_up_next_button], width=RIGHT_COL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    layout = ft.SafeArea(ft.Column([
        ft.Row([ft.Text("Lyricl", size=30, weight=ft.FontWeight.BOLD), ft.Row([ft.Image('static/top2000_logo.png', height=30), ft.Text(" edition", size=26)])], width=FULL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=9, thickness=2),
        ft.Row([ft.Column([
            ft.Row([year_row, rank_row], spacing=50), lyrics_box]),
            ft.Column([button_row, guess_column], spacing=20)
        ], width=FULL_WIDTH, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]))

    page.add(layout)
    page.window.height = 600
    page.window.width = 1100
    page.scroll = ft.ScrollMode.HIDDEN
    page.update()


def generate_lyrics_rows(song_path):
    global GUESSES, GAVE_UP

    def show_length(e: ft.ControlEvent):
        txt = e.control.content
        if txt.bgcolor != '#00000000':
            txt.color = COLORS[len(txt.value)] if txt.color == 'black' else 'black'
        txt.update()

    def word_style(word, style):
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
    still_playing = True

    # Check if game is won
    is_game_won = all([style != 'redacted' for _, style in lyrics[0][:lyrics[0].index(('-', ''))]])
    if is_game_won:
        lyrics = process_song(song_path, GUESSES, won=True)
        still_playing = False

    # Check if player gave up
    if GAVE_UP:
        lyrics = process_song(song_path, GUESSES, lost=True)
        still_playing = False

    title_row = ft.Row([ft.Container(ft.Text(word, **word_style(word, style), size=24), on_hover=show_length)
                        for word, style in lyrics[0]], spacing=3, wrap=True)
    other_rows = [ft.Row([ft.Container(ft.Text(word, **word_style(word, style), size=18), on_hover=show_length)
                          for word, style in line], spacing=3, wrap=True) for line in lyrics[1:]]
    return [title_row] + other_rows, still_playing


if __name__ == '__main__':
    ft.app(main)

