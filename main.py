from flask import Flask, render_template, request
from backend import *

app = Flask(__name__)
guesses = []


@app.route('/', methods=['GET', 'POST'])
def root():
    global guesses
    filepath = 'static/data/songs/song2.txt'
    if request.method == 'POST':
        word = request.form['word']
        if word.lower() not in guesses:
            guesses.append(word.lower())
    lyrics = process_song(filepath, guesses)
    guessed_words = [(i+1, w, number_of_occurences(filepath, w)) for i, w in enumerate(guesses)][::-1]
    kwargs = {"lyrics": lyrics[1:], "song_title": lyrics[0], "guessed_words": guessed_words}
    return render_template('index_flex.html', **kwargs)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8000, debug=True)


