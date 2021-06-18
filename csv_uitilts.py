import csv
import re
from pathlib import Path
cwd = Path.cwd()
import os
def dataset_formatter(text):
     #the 8 is indexc of dataset/
     dot_index=text.find(".")
     return(text[8:dot_index])
# reading file.cv
def read_cv():
  names=[]
  with open(os.path.join(str(cwd),'HAND.csv')) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0

    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            names.append(row[0])

            line_count += 1
  return names
# appending the data
def append_cv(filename,features):
   modfied_filename="dataset/"+filename+"."# to adhere to the standared
   print(modfied_filename)
   featuresOut = [str(f) for f in features]
   with open('HAND.csv','a') as output:
      output.write("%s,%s\n" % (modfied_filename, ",".join(featuresOut)))



