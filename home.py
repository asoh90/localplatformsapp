from flask import Flask, render_template, url_for, flash, redirect, request
from forms import SelectPlatformForm, SelectFunctionForm
from werkzeug.utils import secure_filename
import options
import platform_manager as pm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1ac33ec538de1e200d5f537e717ae6b'
app.config["DOWNLOAD_FOLDER"] = "download"

platform_functions = options.platform_functions

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = SelectPlatformForm()
    # if form.validate_on_submit():
    #     return redirect(url_for("function", platform=form.platform.data))
    return render_template('home.html', form=form, platform_functions=platform_functions)


# Test page
@app.route("/testhome", methods=['GET','POST'])
def testhome():
    return render_template('testhome.html')

@app.route("/download", methods=['POST'])
def download():
    # Get downloaded file
    fileob = request.files["file"]
    filename = secure_filename(fileob.filename)
    save_path = "{}/{}".format(app.config["DOWNLOAD_FOLDER"], filename)
    fileob.save(save_path)

    # get fields
    platform = request.form['platform']
    function = request.form['function']

    return pm.callAPI(platform, function)

if __name__ == "__main__":
    app.run()

# Test function
# @app.route("/function", methods=['GET','POST'])
# def function():
#     platform_selected = {'name':request.args['platform']}
#     print("Platform Selected: " + platform_selected['name'])

#     form = SelectFunctionForm()
#     return render_template('function.html', title="Select Function", platform=platform_selected)
