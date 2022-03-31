
import csv
with open('AVAXBUSD-5m-2022-Ene-Feb-Mar.csv', newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:
         p0 = float(row[1])
         p1 = float(row[2])
         p2 = float(row[3])
         p3 = float(row[4])
         ave_p = (p0+p1+p2+p3)/4.0
         print(row[0]+','+str(ave_p))