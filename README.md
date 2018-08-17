This is a web based python3 system to convert SPSS .sav files to .csv files and clean up labels
After selecting the file, it downloads the variable names and current labels
The user goes through and can select or edit from several options or create their own.
You can exit at any time by clicking the "write" button, any unmodified label will default to the label 
(not the variable)
Both the codefile (updated with modifications) and the data file can be downloaded. They are .csv files
The restart button will remove all uploaded user files from the server.


This runs in a flask web server. By default it runs on port 5000
It uses R to read the SPSS file
It also use NLTK to remove stopwords

Installation:

clone the git repository to your server

pip3 install Flask

pip3 install rpy2 (R will need to be installed on your system first "apt-get install r-base")

pip3 install nltk

after installation, start python. in python type:

  import nltk
  
  from nltk.corpus import stopwords
  
  nltk.download('stopwords')
  
  stopwords = stopwords.words('english')

This only needs to be run one time

afterwords run the shell script ./startflask.sh

This set location parameters, which you may or may not need or
type

export FLASK_APP=sav2csv.py

flask run --host=0.0.0.0

(If you get complaints bout 

The goto the web page.



