import csv
import sys
import os

vendorList = []
#search = input("Enter vendor: ")
search = 'Cisco'
with open('vendors.csv', mode='r',encoding='utf-8') as vendorCSV:
    reader = csv.DictReader(vendorCSV)
    for line in reader:
        vendorList.append(line)
def vendorSearch(searchText):
    for vendor in vendorList:
        if searchText in vendor['Partner']:
            print ('Partner Account Manager: ' + vendor['Partner Account Manager'])
print (vendorSearch(search))


