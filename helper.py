from flask import render_template

def apology(message, status):
    return render_template("apology.html", error=message, number=status)
    