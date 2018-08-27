from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from forms import SelectPlatformForm, SelectFunctionForm
from werkzeug.utils import secure_filename
import options
import platform_manager as pm
import urllib3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1ac33ec538de1e200d5f537e717ae6b'
app.config["UPLOAD_FOLDER"] = "upload"

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

# when file gets dropped into the dropzone, or "Query" function is selected, run this
@app.route("/process", methods=['POST'])
def process():
    # get fields
    platform = request.form['platform']
    function = request.form['function']
    save_path = None

    if function != "Query":
        # Get downloaded file
        fileob = request.files["file"]
        filename = secure_filename(fileob.filename)
        save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
        fileob.save(save_path)

    output = pm.callAPI(platform, function, save_path)
    output_message = output["message"]
    output_file = output["file"]
    return output_message
    

if __name__ == "__main__":
    app.run()

# Test function
# @app.route("/function", methods=['GET','POST'])
# def function():
#     platform_selected = {'name':request.args['platform']}
#     print("Platform Selected: " + platform_selected['name'])

#     form = SelectFunctionForm()
#     return render_template('function.html', title="Select Function", platform=platform_selected)
