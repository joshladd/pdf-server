from pdfrw import PdfReader
import sys
import os
# os.environ["PDFTK_PATH"] = os.path.abspath(os.path.join(sys._MEIPASS,"pdftk.exe"))
# print(os.listdir(sys._MEIPASS))
import pdfrw
import pypdftk
import fitz
from PIL import Image
import argparse
import tempfile
import json
from tkinter import Tk, filedialog
from PyPDF2 import PdfFileMerger, PdfFileReader
import shutil
from time import sleep
import subprocess



# def gen_xfdf(datas,out_dir):
# 	''' Generates a temp XFDF file suited for fill_form function, based on dict input data '''
# 	fields = []
# 	for key, value in datas.items():
# 		fields.append("""        <field name="%s"><value>%s</value></field>""" % (key, value))
# 	tpl = """<?xml version="1.0" encoding="UTF-8"?>
# <xfdf xmlns="http://ns.adobe.com/xfdf/" xml:space="preserve">
# 	<fields>
# %s
# 	</fields>
# </xfdf>""" % "\n".join(fields)
# 	handle, out_file = tempfile.mkstemp()
# 	with open(out_dir,"wb") as f:
# 		f.write((tpl.encode('UTF-8')))
# 	return out_file


def check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output

def run_command(command, shell=False):
    ''' run a system command and yield output '''
    p = check_output(command, shell=shell)
    return p.decode("utf-8").splitlines()





def gen_xfdf(datas={}):
	''' Generates a temp XFDF file suited for fill_form function, based on dict input data '''
	fields = []
	for key, value in datas.items():
		fields.append("""        <field name="%s"><value>%s</value></field>""" % (key, value))
	tpl = """<?xml version="1.0" encoding="UTF-8"?>
<xfdf xmlns="http://ns.adobe.com/xfdf/" xml:space="preserve">
	<fields>
%s
	</fields>
</xfdf>""" % "\n".join(fields)
	handle, out_file = tempfile.mkstemp()
	f = os.fdopen(handle, 'wb')
	f.write((tpl.encode('UTF-8')))
	f.close()
	return out_file


def fill_form(pdf_path, datas={}, out_file=None, flatten=True):
	'''
		Fills a PDF form with given dict input data.
		Return temp file if no out_file provided.
	'''
	cleanOnFail = False
	tmp_fdf = gen_xfdf(datas)
	handle = None
	if not out_file:
		cleanOnFail = True
		handle, out_file = tempfile.mkstemp()

	cmd = "%s %s fill_form %s output %s" % (".\\pdftk.exe", pdf_path, tmp_fdf, out_file)
	if flatten:
		cmd += ' flatten'
	try:
		run_command(cmd, True)
	except:
		if cleanOnFail:
			os.remove(tmp_fdf)
		raise
	finally:
		if handle:
			os.close(handle)
	os.remove(tmp_fdf)
	return out_file

	
def get_output_directory():
	root = Tk()
	root.withdraw()
	folder_selected = filedialog.askdirectory()
	# print(folder_selected)
	if not folder_selected:
		print("no output directory selected, using C:/SirosExports by default")
		folder_selected = "C:/SirosExports"

	return folder_selected

def load_data(dsu_dir):
	data = {}
	for i in os.listdir(os.path.join(dsu_dir,"Data")):
		with open(os.path.join(dsu_dir,"Data",i),"r") as f:
			fields = json.load(f)

	for field in fields["fieldObjs"]:

		if field["name"] == "Operator" and len(field["displayText"]) > 10:
			data[field["name"]] = field["displayText"][:10] + "..."
		else:
			data[field["name"]] = field["displayText"]

	return data


def write_single_image(image_dir,pdf_dir,out_dir):
	x1 = 115
	x2 = 505
	y1 = 105
	y2 = 240

	image_rectangle = fitz.Rect(x1,y1,x2,y2)

	file_handle = fitz.open(pdf_dir)
	target_page = file_handle[0]

	target_page.insertImage(image_rectangle,filename=image_dir)
	file_handle.save(out_dir)

	
def write_double_image(left,right,pdf_dir,out_dir):
	x1 = 90
	x2 = 305
	y1 = 70
	y2 = 275
	offset = 220

	print(left)
	print(right)
	image_rectangle = fitz.Rect(x1,y1,x2,y2)

	file_handle = fitz.open(pdf_dir)
	target_page = file_handle[0]

	target_page.insertImage(image_rectangle,filename=left)


	image_rectangle = fitz.Rect(x1+offset,y1,x2+offset,y2)
	target_page.insertImage(image_rectangle,filename=right)

	file_handle.save(out_dir)

def get_images(image_dir):
	images = {}


	for filename in os.listdir(os.path.join(image_dir,"Images")):
		if "Isometric" in filename:
			images["right"] = os.path.abspath(os.path.join(image_dir,"Images",filename))
		else:
			images["left"] = os.path.abspath(os.path.join(image_dir,"Images",filename))

	return images

def process_pdf(data,images,pagename,input_dir,out_dir):

	if getattr(sys,"frozen",False):
		fill = os.path.join(sys._MEIPASS,"files/fillable_ops.pdf")
		exe = os.path.join(sys._MEIPASS,"pdftk.exe")
	else:
		fill = "files/fillable_ops.pdf"

	pypdftk.fill_form(fill,datas=data,out_file=os.path.join(input_dir,"%s_temp.pdf"%pagename),flatten=True)

	# gen_xfdf(data,os.path.join(out_dir,pagename+".fdf"))
	# subprocess.call([exe,fill,"fill_form",os.path.join("out_dir",pagename+".fdf"),"output",os.path.join(input_dir,"%s_temp.pdf"%pagename),"flatten"])

	if pagename == "Summary":
		write_single_image(images["left"],os.path.join(input_dir,"%s_temp.pdf"%pagename),os.path.join(out_dir,"%s.pdf"%pagename))
	else:
		write_double_image(images["left"],images["right"],os.path.join(input_dir,"%s_temp.pdf"%pagename),os.path.join(out_dir,"%s.pdf"%pagename))

def nukedir(dir):
	if dir[-1] == os.sep: dir = dir[:-1]
	files = os.listdir(dir)
	for file in files:
		if file == '.' or file == '..': continue
		path = dir + os.sep + file
		if os.path.isdir(path):
			nukedir(path)
		else:
			os.unlink(path)
	os.rmdir(dir)


def cleanup(input_dir,temp_dir):

	for folder in os.listdir(input_dir):
		path = os.path.join(input_dir,folder)
		if os.path.isdir(path):
			shutil.rmtree(path)
		else:
			os.remove(path)
	
	nukedir(temp_dir)



def merge(pages,temp_dir,out_dir):
	merger = PdfFileMerger()

	openfiles = []
	for filename in pages:
		openfile = open(os.path.join(temp_dir,filename[0]),"rb")
		merger.append(openfile)
		openfiles.append(openfile)

	merger.write(os.path.join(output_dir,"%s.pdf"%args.filename))
	merger.close()

	for f in openfiles:
		f.close()


if __name__ == "__main__":

	parser = argparse.ArgumentParser(
		prog="PDF Exporter", description="Convert SIROS reports into a PDF document")
	parser.add_argument(
		"--input_dir", help="Absolute path for input files", required=True)
	parser.add_argument(
		"--filename", help="filename for resulting PDF", required=True)
	args = parser.parse_args()

	output_dir = get_output_directory()
	print(output_dir)
	temp_dir = os.path.join(output_dir,"SIROSTEMP")
	if os.path.exists(temp_dir):
		shutil.rmtree(temp_dir)
	os.mkdir(temp_dir)

	pages = []
	for i in os.listdir(os.path.join(args.input_dir,"OnePageSummary")):
		if "OPS" not in i:
			continue
		path = os.path.join(args.input_dir,"OnePageSummary")
		pagename = os.path.splitext(i.split(" ")[1])[0]
		data = load_data(os.path.abspath(os.path.join(path,i)))
		images = get_images(os.path.abspath(os.path.join(path,i)))

		if pagename == "Summary":
			data["DSUID"] = "Summary"

		data["Exit Date"] = "01/01/2024"

		page = (pagename+ ".pdf",int(data["Page Numbers"].split(" ")[0]))
		pages.append(page)

		process_pdf(data,images,pagename,temp_dir,temp_dir)


	pages.sort(key=lambda x: x[1])


	
	merge(pages,temp_dir,output_dir)

	


	cleanup(args.input_dir,temp_dir)



		# path = os.path.join("OnePageSummary",i,"Data")
		# # print(path)
		# for k in os.listdir(path):
		# 	filename = os.path.join(path,k)
		# 	with open(filename,"r") as f:
		# 		data = json.load(f)

		# 	with open(filename,"w") as f:
		# 		json.dump(data,f,indent=2)


#need to add dialog for save location
# class FillPDF: 

# 	def __init__(self,template,datadir,datamap,outfile):

# 		self.template = template
# 		self.data = datadir
# 		self.fields = self.getFields()
# 		self.datamap = datamap
# 		self.outfile = outfile

# 	def getFields(self):

# 		self.fields = pypdftk.dump_data_fields(self.template)


# 	def add_dsu_images(self):
# 		pass

# 	def add_summary_image(self):
# 		pass

# 	def formatField(self,field,fieldType):

# 		if fieldType == "Money":
# 			pass
# 		elif fieldType == "Decimal":
# 			pass
# 		elif fieldType == "Int":
# 			pass
# 		elif fieldType == "Percent":
# 			pass
# 		elif fieldType == "Rate":
# 			pass
# 		else:
# 			pass

# 		return field


# 	def fillFields(self):
# 		updatedFields = {}

# 		for field in self.fields:
# 			dataField = self.datamap[field["FieldName"]]
# 			updatedFields[field["FieldName"].strip()] = self.formatField(self.data[dataField])

# 		pypdftk.fill_form(self.template,datas=updatedFields,out_file=self.outfile,flatten=True)
		


# fields = pypdftk.dump_data_fields("./fillable_ops.pdf")

# update = {}
# for field in fields:
# 	print(field["FieldName"])
# 	if field["FieldName"].strip() in ["image1","image2"]:
# 		# with open("./irr.png","r") as f:
# 		# 	update[field["FieldName"].strip()] = f.read()
# 		continue
# 	else:
# 		update[field["FieldName"].strip()] = "123"


# pypdftk.fill_form("./fillable_ops.pdf",datas=update,out_file="./output.pdf",flatten=True)



# input_file = "./output.pdf"
# output_file = "./image_output.pdf"


# image_file = 'C:\\Users\\ladd6\\Desktop\\OnePageSummary\\OPS 150093_03040910-1\\Images\\OPS 150093_03040910-1 Birds Eye.png'
# x1 = 90
# x2 = 305
# y1 = 70
# y2 = 275
# offset = 220

# aspect = 2
# size = 5
 
# # x1 = 115
# # x2 = 505
# # y1 = 105
# # y2 = 240
# # offset = 220

# # aspect = 2
# # size = 5

# image_rectangle = fitz.Rect(x1,y1,x2,y2)

# file_handle = fitz.open(input_file)
# target_page = file_handle[0]

# target_page.insertImage(image_rectangle,filename=image_file)


# image_rectangle = fitz.Rect(x1+offset,y1,x2+offset,y2)
# target_page.insertImage(image_rectangle,filename=image_file)


# # image_rectangle = fitz.Rect(x1,y1,x2,y2)

# # file_handle = fitz.open(input_file)
# # target_page = file_handle[0]

# # target_page.insertImage(image_rectangle,filename=image_file)

# file_handle.save(output_file)


# pdf = PdfReader("./OPS_Fillable.pdf")
# fields = pdf.Root.AcroForm.Fields

# update = {}
# for f in fields:
# 	print(f.T)
# 	update[f.T[1:-1]] = "update"
# 	# f.update(pdfrw.PdfDict(V='{}'.format("update")))

# # pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

# # pdfrw.PdfWriter().write("./output.pdf", pdf)
# print(dir(pdf))
