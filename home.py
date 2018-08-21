from flask import Flask, render_template, flash, redirect
from forms import SelectPlatformForm, SelectFunctionForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1ac33ec538de1e200d5f537e717ae6b'

PLATFORMS = [
    {
        'display_name':'AppNexus',
    },
    {
        'display_name':'The Trade Desk',
    }
]

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = SelectPlatformForm()
    if form.validate_on_submit():
        flash(f'Platform selected: {form.platform.data}','success')
        return redirect(url_for('function'))
    return render_template('home.html', form=form, posts=PLATFORMS)

@app.route("/function", methods=['GET','POST'])
def function():
    form = SelectFunctionForm()
    return render_template('function.html', title="Select Function")

if __name__ == "__main__":
    app.run()