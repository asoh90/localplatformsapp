from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from forms import SelectPlatformForm, SelectFunctionForm
from werkzeug.utils import secure_filename
import variables
import platform_manager as pm

app = Flask(__name__)

app.config['SECRET_KEY'] = variables.SECRET_KEY
app.config["UPLOAD_FOLDER"] = variables.UPLOAD_FOLDER
RETURN_FOLDER = variables.RETURN_FOLDER

platform_functions = variables.platform_functions

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

    # try:
        # output_file = output["file"]
        # return send_file(RETURN_FOLDER + output_file, as_attachment=True, attachment_filename=output_file)
    # except:
    #     return output["message"]
    output_file = output["file"]
    return send_file(RETURN_FOLDER + output_file, as_attachment=True, attachment_filename=output_file)
    

@app.route("/test", methods=['GET','POST'])
def test():
    return send_file(RETURN_FOLDER + "The_Trade_Desk_2018-08-27_23;46;06.xlsx", as_attachment=True, attachment_filename="The_Trade_Desk_2018-08-27_23;46;06.xlsx")

if __name__ == "__main__":
    app.run()

# Test function
# @app.route("/function", methods=['GET','POST'])
# def function():
#     platform_selected = {'name':request.args['platform']}
#     print("Platform Selected: " + platform_selected['name'])

#     form = SelectFunctionForm()
#     return render_template('function.html', title="Select Function", platform=platform_selected)
