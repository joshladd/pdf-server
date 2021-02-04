import json
import os
from datetime import datetime
import flask
from pdfjinja import PdfJinja
from flask import request, jsonify, Flask, make_response
from PyPDF2 import PdfFileReader, PdfFileMerger
import urllib
import re
import pypdftk
import base64
import shutil
from flask import make_response
from flask import send_file, current_app as app

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

# set up an elif where if it iss a string return the value or display text 
# if it is int or decimal, grab num value, then round the decimal to the number of places specifed in places in each obj
# for money prepend $ and for percentage suffix wit $ 
# return all data as strings 

# field_name = get_tooltip(field["name"])
# pdf_data[field_name] = get_display_text(field)


def get_display_text(field_object):  

    display_text = field_object["numValue"]
    # return str(field_object["numValue"])  
    # for field in data:
    if field_object["valueType"] == 0:
        display_text = field_object["value"]
        return display_text 
    elif field_object["valueType"] == 1:
        display_text = str(int(display_text))
        # display_text = str(round(display_text,field_object["places"]))
        return display_text
    elif field_object["valueType"] == 2:
        round(display_text,field_object["places"])
        display_text = str(round(display_text,field_object["places"]))
        return display_text
    elif field_object["valueType"] == 3:
        round(4,field_object["places"])
        display_text = '$' + str(round(display_text,field_object["places"]))
        return display_text
    elif field_object["valueType"] == 4:
        # print("found it")
        round(5,field_object["places"])
        display_text = str(round(display_text,field_object["places"])) + '%'
        return display_text


def generate_pdf_data(data):
    # return str(x)

    pdf_data = {}

    for field in data:
        field_name = get_tooltip(field["name"])
        field_value = get_display_text(field)

        pdf_data[field_name] = field_value
        print(field_name,field_value)
        # if field["valueType"] == 0:
        #     if not field["value"]:
        #         val = "filler"
        #     else:
        #         val = field["value"]

        #     pdf_data[get_tooltip(field["name"])] = val
        # else:
        #     pdf_data[get_tooltip(field["name"])] = round(field["numValue"], 2)

    return pdf_data


def debug(string):
    print(string)

@app.route("/ops", methods=["POST"])
def generate_ops():
    print("hit")
    print(dir(request))
    # print(request.data)
    form = json.loads(request.data)

    
    data = form["OPSData"]

    # with open("./test.txt","w") as f:
    #     for key in data:
    #         f.write(str(key) + "\n")

    output_objects = []
    template = PdfJinja("./fillable_ops.pdf")


    for key in data:
        
            #set DSUID to "
        
        pdf_data = generate_pdf_data(data[key])

        if key == "Summary":
            pdf_data["DSUID"] = ""

        deal_source = pdf_data.get("DealSource")
        seller = pdf_data.get("Seller")
        status = pdf_data.get("Status")
        date = pdf_data.get("Date")


        if deal_source == None:
            pdf_data["DealSource"] = "No Data Provided"
        if seller == None:
            pdf_data["Seller"] = "No Data Provided"
        if date == None:
            pdf_data["Date"] = "N/A"
        if status == None: 
            pdf_data["Status"] = "No Data Provided"
   
        
        
  
        #if DealSource not in pdf_data, then add it with "No Data Provided" as the value
        

        output_objects.append(pdf_data)
        rendered = template(pdf_data)
        pdf_name = "output" + key + ".pdf"
        output_file = "./output/" + pdf_name

        # append output_file to a list
        rendered.write(open(output_file, "wb"))

    # use pypdftk.concat() on the resulting list
    output_objects = []
    for filename in os.listdir("./output"):
        path_name = "./output/" + filename
        output_objects.append(path_name)

    output_objects.sort(reverse=True)\


    output = PdfFileMerger()

    for pdf in output_objects:
        pdf_file = PdfFileReader(pdf)
        output.append(pdf_file)

    # pdf_file1 = PdfFileReader("./output/outputSummary.pdf")
    # pdf_file2 = PdfFileReader("./output/output151097_29303132-1.pdf")
    # pdf_file3 = PdfFileReader("./output/output151097_17181920-1.pdf")
    # output.append(pdf_file1)
    # output.append(pdf_file2)
    # output.append(pdf_file3)
    output.write("outputMerged.pdf")

    # generated_pdf = pypdftk.fill_form('./output/', pdf_data)
    # output_file = pypdftk.concat(['./outputSummary/', generated_pdf])


    # given_value = OPSData.value


 

    # form = request.form
    # data = json.loads(form["OPSData"])
    # pdf_data = generate_pdf_data(data['151097_2635-1'])

    # # print(template)

    with open("./output.txt","w") as f:
        json.dump(output_objects,f,indent=2)

    return flask.jsonify({"message":"hi"})

# @app.route('/OPM') #the url you'll send the user to when he wants the pdf
# def pdfviewer():
#     return flask.send_file("./output/outputMerged.pdf", attachment_filename="outputMerged.pdf")

@app.route('/Show/')
def show_static_pdf():
    # with open('./outputMerged.pdf', 'rb') as static_file:
    return send_file("./outputMerged.pdf", attachment_filename='outputMerged.pdf')


        # return flask.jsonify({"message":"hi"})




    # print(form)
    # with open("./output/output.pdf", "rb") as f:
    #     encoded_string = base64.b64encode(f.read())

    # return flask.send_file("./output/output.pdf", mimetype="application/pdf", attachment_filename="ops.pdf", as_attachment=True)

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
    # return jsonify(data)
    # return jsonify(request.form)


@app.route("/")
def home():
    if "output.pdf" not in os.listdir("./output"):
        return "no file to send"
    else:
        return flask.send_file("./output/output.pdf", attachment_filename="output.pdf")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
