import flet as ft
from glob import glob
from backend import *
import numpy as np


GUESSES = []


def main(page: ft.Page):
    global GUESSES

    files = glob('static/data/songs/Top2000/*.txt')
    song_path = files[np.random.randint(len(files))]
    # song_path = 'static/data/songs/Top2000/song0269.txt'


    def add_guess(e):
        last_guess = guess_field.value
        last_guess = [last_guess] if ' ' not in last_guess else last_guess.split(' ')
        for lg in last_guess:
            if lg != '' and lg not in GIVEN_WORDS + GUESSES:
                GUESSES.append(lg)
                guess_column.controls.insert(2, ft.Row([ft.Text(str(len(GUESSES)), size=22), ft.Text(lg, size=22),
                                                        ft.Text(str(number_of_occurences(song_path, lg)), size=22)],
                                                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300))
        guess_column.update()
        guess_field.value = ''
        guess_field.update()
        lyrics_box.controls = generate_lyrics_rows(song_path)
        lyrics_box.update()
        guess_field.focus()

    def reveal_year(e):
        year_row.controls = [ft.Text("Year: ", size=22, width=60), ft.Text(str(get_year(song_path)), size=22)]
        year_row.update()

    def reveal_rank(e):
        rank_row.controls = [ft.Text("Rank: ", size=22, width=60), ft.Text('#' + str(get_top2000_rank(song_path)), size=22)]
        rank_row.update()

    year_row = ft.Row([ft.Text("Year: ", size=22, width=60), ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_year, width=50)], spacing=5)
    rank_row = ft.Row([ft.Text("Rank: ", size=22, width=60), ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE, on_click=reveal_rank, width=50)], spacing=5)
    lyrics_box = ft.Column(generate_lyrics_rows(song_path), width=500, height=3000)

    guess_field = ft.TextField(hint_text='Enter guess', on_submit=add_guess)
    guess_column = ft.Column([
        ft.Row([guess_field, ft.ElevatedButton('Submit', on_click=add_guess, height=50)],
               alignment=ft.alignment.top_right),
        ft.Row([ft.Text('#', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Guess', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Hits', size=26, weight=ft.FontWeight.BOLD)],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
    ], width=400, height=3000)

    layout = ft.SafeArea(ft.Column([
        ft.Row([ft.Text("Lyricl ", size=30), ft.Row([ft.Image('static/top2000_logo.png', height=30), ft.Text(" edition", size=26)])], width=1000, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(height=9, thickness=2),
        ft.Row([ft.Column([ft.Row([year_row, rank_row], spacing=50), lyrics_box]), guess_column], width=1000, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]))

    page.add(layout)
    page.window.height = 800
    page.window.width = 1100
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.update()


def generate_lyrics_rows(song_path):
    global GUESSES

    def show_length(e: ft.ControlEvent):
        txt = e.control.content
        if txt.bgcolor == 'grey':
            txt.color = 'white' if txt.color == 'grey' else 'grey'
        txt.update()

    word_style = {'': {'color': 'white', 'bgcolor': '#00000000'}, 'redacted': {'color': 'grey', 'bgcolor': 'grey'}, 'last-guess': {'color': 'red', 'bgcolor': '#00000000'}}
    lyrics = process_song(song_path, GUESSES)
    title_row = ft.Row([ft.Container(ft.Text(word, **(word_style[style]), size=24), on_hover=show_length)
                        for word, style in lyrics[0]], spacing=3)
    other_rows = [ft.Row([ft.Container(ft.Text(word, **word_style[style], size=18), on_hover=show_length)
                          for word, style in line], spacing=3) for line in lyrics[1:]]
    return [title_row] + other_rows


if __name__ == '__main__':
    ft.app(main)

