import json
import os
from datetime import datetime
import flask
from pdfjinja import PdfJinja
from flask import request, jsonify, Flask, make_response
import urllib
import re
import base64
import shutil

app = Flask(__name__)


def get_tooltip(name):
    out = name.replace(" ", "")
    out = out.replace("%", "")
    out = out.replace("$", "")
    out = out.replace("&", "")
    out = out.replace("/", "")
    out = out.replace("(", "")
    out = out.replace(")", "")
    out = out.replace(".", "")
    return out


def generate_pdf_data(data):

    pdf_data = {}

    for field in data:
        print(get_tooltip(field["name"]))
        if field["valueType"] == 0:
            if not field["value"]:
                val = "filler"
            else:
                val = field["value"]

            pdf_data[get_tooltip(field["name"])] = val
        else:
            pdf_data[get_tooltip(field["name"])] = round(field["numValue"], 2)

    return pdf_data


@app.route("/ops", methods=["POST"])
def generate_ops():
    print("hit")
    print(dir(request))
    # print(request.data)
    form = json.loads(request.data)
    data = form["OPSData"]
    pdf_data = generate_pdf_data(data["151097_2635-1"])

    # form = request.form
    # data = json.loads(form["OPSData"])
    # pdf_data = generate_pdf_data(data['151097_2635-1'])

    template = PdfJinja("./fillable_ops.pdf")
    print(template)

    rendered = template(pdf_data)
    output_file = "./output/output.pdf"
    rendered.write(open(output_file, "wb"))

    print(form)
    with open("./output/output.pdf", "rb") as f:
        encoded_string = base64.b64encode(f.read())

    return flask.send_file("./output/output.pdf", mimetype="application/pdf", attachment_filename="ops.pdf", as_attachment=True)

    # pypdftk.fill_form("./fillable_ops.pdf",datas=data,out_file="./output/output.pdf",flatten=True)

    # yo = json.loads(jstr.decode("ascii"))
    # print(yo['151097_2635-1'][:5])
    # keys = []
    # for key in data:
    #     keys.append(key)

    # if "Summary" in keys:
    #     pass
    # else:
    #     print(data)
    # pdf_data = generate_pdf_data(keys[0])
    return jsonify(data)
    # return jsonify(request.form)


@app.route("/")
def home():
    if "output.pdf" not in os.listdir("./output"):
        return "no file to send"
    else:
        return flask.send_file("./output/output.pdf", attachment_filename="output.pdf")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
