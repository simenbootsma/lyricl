import flet as ft
from backend import *


def main(page: ft.Page):
    lyrics = ''
    lyrics_box = ft.Container(ft.Column([]))

    layout = ft.SafeArea(ft.Column([
        ft.Text("Lyricl", size=30),

    ]))

    page.add(layout)
    page.update()


if __name__ == '__main__':
    ft.app(main)

