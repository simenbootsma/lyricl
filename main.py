import flet as ft
from backend import *


GUESSES = []


def main(page: ft.Page):
    global GUESSES

    song_path = 'static/data/songs/Top2000/song0269.txt'

    def add_guess(e):
        last_guess = guess_field.value
        last_guess = [last_guess] if ' ' not in last_guess else last_guess.split(' ')
        for lg in last_guess:
            GUESSES.append(lg)
            guess_column.controls.insert(2, ft.Row([ft.Text(str(len(GUESSES)), size=22), ft.Text(lg, size=22),
                                                    ft.Text(str(number_of_occurences(song_path, lg)), size=22)],
                                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300))
        guess_column.update()
        guess_field.value = ''
        guess_field.update()
        lyrics = process_song(song_path, GUESSES)
        lyrics_box.controls = [ft.Row([ft.Text(word, **word_style[style]) for word, style in line], spacing=3) for line in lyrics]
        lyrics_box.update()
        guess_field.focus()

    def show_length(e):
        print('tap')
        print(e.target)

    word_style = {'': {'color': 'white'}, 'redacted': {'color': 'grey', 'bgcolor': 'grey'}, 'last-guess': {'color': 'red'}}
    lyrics = process_song(song_path, GUESSES)
    lyrics_box = ft.Column([
        ft.Row([ft.Text(word, **word_style[style], on_tap=show_length) for word, style in line], spacing=3) for line in lyrics
    ])

    guess_field = ft.TextField(hint_text='Enter guess', on_submit=add_guess)
    guess_column = ft.Column([
        ft.Row([guess_field, ft.ElevatedButton('Submit', on_click=add_guess, height=50)],
               alignment=ft.alignment.top_right),
        ft.Row([ft.Text('#', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Guess', size=26, weight=ft.FontWeight.BOLD),
                ft.Text('Hits', size=26, weight=ft.FontWeight.BOLD)],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
    ], width=400, height=2000,)

    layout = ft.SafeArea(ft.Row([
        ft.Column([
            ft.Text("Lyricl", size=30),
            lyrics_box
        ], width=500, height=2000),
        guess_column
    ], width=1000, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    page.add(layout)
    page.window.height = 800
    page.window.width = 1200
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.update()


if __name__ == '__main__':
    ft.app(main)

