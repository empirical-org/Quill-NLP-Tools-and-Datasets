# -*- coding: utf-8 -*-
from flask import request, \
     render_template, flash, Flask
print('Loading qfragment models...')
from qfragment import check
app = Flask(__name__)
app.secret_key = 'dddxasdasd' # needed for message flashing

@app.route('/', methods=['GET', 'POST'])
def check_sentence():
    """Sole porcupine endpoint"""
    text = ''
    if request.method == 'POST':
        text = request.form['text']
        if not request.form['text']:
            error = 'No input'
            flash_message = error
        else:
            feedback = check(request.form['text']).human_readable
            # TODO: remove the hack below
            if feedback == "This looks like a strong sentence.":
                feedback = "No errors were found."
            flash_message = feedback

        flash(flash_message)
    return render_template('check_sentence.html', text=text)

if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
