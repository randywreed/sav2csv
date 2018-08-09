from rpy2.robjects.packages import importr
from rpy2 import robjects
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.utils import secure_filename
from nltk.corpus import stopwords
import csv
#print (rpy2.__version__)
foreign=importr("foreign")
en_stops=set(stopwords.words('english'))
#update stopwords
en_stops.remove('not')
newstopwords=['what','why','who','when','where']
en_stops.update(newstopwords)


app=Flask(__name__)

APP_ROOT=os.path.dirname(os.path.abspath(__file__))
@app.route("/")
def index():
  return render_template("upload.html")

@app.route("/upload", methods=['GET','POST'])
def upload():
  target=os.path.join(APP_ROOT,'files/')
  print(target)
  print('request=',request)
  if not os.path.isdir(target):
    os.mkdir(target)
  file=request.files['file']
  
  print('file from request=',file)
  if file.filename=="":
    flash('No selected files')
    return redirect(request.url)
  
  filename=secure_filename(file.filename)
  print(filename)
  destination=os.path.join(target, filename)
  print("saving to ", destination)
  file.save(destination)
  global outfile
  outfile=os.path.splitext(destination)[0]+".csv"
  print ("outfile=",outfile)
  #create dataframe of save file
  robjects.r.assign('dest',destination)
  robjects.r.assign('outfile',outfile)
  robjects.r('dataset1<-read.spss(dest,to.data.frame=TRUE)')
  robjects.r('write.csv(dataset1, file=outfile, row.names=FALSE)')
  dataset1=robjects.r('dataset1')
  #print(robjects.r('head(dataset1)'))
  print(robjects.r('names(dataset1)'))
  #print(robjects.r('attr(dataset1,"variable.labels")'))
  #robjects.r('dataset.label<-data.frame(seq.int(names(dataset1)),names(dataset1),attr(dataset1,"variable.labels"), row.names=seq.int(names(dataset1)))')
  #robjects.r('names(dataset.label)<-c("ID","fieldname","variable")')
  robjects.r('lst_seq=seq.int(names(dataset1))')
  robjects.r('lst_names=names(dataset1)')
  robjects.r('lst_variables=attr(dataset1,"variable.labels")')
  #newdataset=robjects.r('dataset.label')
  global a,b,c,t
  a=robjects.r('lst_seq')
  b=robjects.r('lst_names')
  c=robjects.r('lst_variables')
  c_strip=""
  c_stripns=""
  
  t=5
#   c_split=c[t].split(" ")
#   for word in c_split:
#     if word not in en_stops:
#       c_strip=c_strip+word+" "
#       c_stripns=c_stripns+word+"_"
#   c_stripns=c_stripns.rstrip('_')
  ret=strip_it(c[t])
  print(len(ret))
  c_strip=ret[0]
  c_stripns=ret[1]
  print(a[t],b[t],c[t],c_strip,c_stripns)
  return render_template("uploaded_file.html", name=filename, field=b[t], variable=c[t], stripvariable=c_strip, stripnsv=c_stripns)

@app.route("/next", methods=['GET','POST'])
def next():
  print('form=',request.form)
  #print('action=', request.form['action'])
  #print('userAnswer=', request.form['userAnswer'])
  #print('Answer=',request.form['Answer'])
  action=request.form['action']
  if request.form['Answer']!='None':
    newvar=request.form['Answer']
  else:
    newvar=request.form['userAnswer']
    
  print(action,newvar)
  #rewrite c with new userAnswer
  global t
  c[t]=newvar
  print (action, newvar)
  if action=="Next":
    t=t+1
  else:
    t=t-1
  if t<0:
    t=1
  if t>len(c):
    t=len(c)
  if action=="Write":
    #write code file to csv
    global codefile
    head, tail=os.path.split(outfile)
    codefile=head+"codefile_"+tail
    rows=zip(a,b,c)
    with open(codefile,"w") as d:
      writer=csv.writer(d)
      for row in rows:
        writer.writerow(row)
    #write data file with new column names
    tmpfile=os.path.split(outfile)[0]
    tmpfile=tmpfile+".tmp"
    with open(outfile, 'r', newline='') as f, open(tmpfile, 'w', newline='') as data:
      #next(f)  # Skip over header in input file.
      writer = csv.writer(data, quoting=csv.QUOTE_ALL)
      writer.writerow(c)      
      writer.writerows(line.split() for line in f)
    os.rename(outfile, os.path.split(outfile)[0]+".old")
    os.rename(tmpfile,os.path.split(tmpfile)[0]+".sav")
    return (render_template("download.html"))
  
  print (a[t],b[t],c[t],t)
  ret=strip_it(c[t])
  print('words after strip',len(ret), ret)
  c_strip=ret[0]
  c_stripns=ret[1]
  return render_template("edvar.html", cur=t, tot=len(c), field=b[t], variable=c[t], stripvariable=c_strip, stripnsv=c_stripns)

@app.route('/return-datafile/')
def return_files_dat():
  global outfile
  head, tail = os.path.split(outfile)
  try:
    return send_file(outfile, attachment_filename=tail)
  except Exception as e:
    return str(e)
  
@app.route('/return-codefile/')
def return_files_code():
  global codefile
  head, tail = os.path.split(codefile)
  try:
    return send_file(codefile, attachment_filename=tail)
  except Exception as e:
    return str(e)
  
  
def strip_it(initialsent):
  c_split=initialsent.split(" ")
  c_strip=""
  c_stripns=""
  for word in c_split:
    if word not in en_stops:
      c_strip=c_strip+word+" "
      c_stripns=c_stripns+word+"_"
  c_stripns=c_stripns.rstrip('_')
  return (c_stripns,c_strip)
#install.packages("foreign")
#library(foreign)
#dataset1=read.spss('PRRI_workingclass.sav',to.data.frame=TRUE)
#head(dataset1)
#attr(dataset1,"variable.labels")
#names(dataset1)
#dataset.labels<-data.frame(attr(dataset1,"variable.labels"))
#dataset.labels<-data.frame(attr(dataset1,"variable.labels"),names(dataset1))
#names(dataset.labels)<-c("label","variable")
#dataset.labels$outlabels<-dataset.labels$variable'''