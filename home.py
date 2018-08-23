from flask import Flask, render_template, url_for, flash, redirect, request
from forms import SelectPlatformForm, SelectFunctionForm
import options
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1ac33ec538de1e200d5f537e717ae6b'

platform_functions = options.platform_functions

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = SelectPlatformForm()
    if form.validate_on_submit():
        return redirect(url_for("function", platform=form.platform.data))
    return render_template('home.html', form=form, platform_functions=platform_functions)

@app.route("/function", methods=['GET','POST'])
def function():
    platform_selected = {'name':request.args['platform']}
    print("Platform Selected: " + platform_selected['name'])

    form = SelectFunctionForm()
    return render_template('function.html', title="Select Function", platform=platform_selected)

if __name__ == "__main__":
    app.run()