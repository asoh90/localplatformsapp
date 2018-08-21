from flask import Flask, render_template
app = Flask(__name__)

PLATFORMS = [
    {
        'display_name':'AppNexus',
        'value':'appnexus'
    },
    {
        'display_name':'The Trade Desk',
        'value':'ttd'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=PLATFORMS)

@app.route("/about")
def about():
    return render_template('about.html', title="About")

if __name__ == "__main__":
    app.run()