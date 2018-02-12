import numpy
#
searchString=input('Enter vendor to search: ')

vendorArray = numpy.loadtxt('vendors.csv',delimiter=',',dtype=str,skiprows=1)

for i in vendorArray:
    if searchString.upper() in i[0].upper():
        vendorName = str(i[0])
        vendorCertificationlevel = i[1]
        vendorContactname = i[2]
        vendorContactemail = i[3]
        vendorContactphone = i[4]
        cdwPartnermanagername = i[5]
        cdwPartnermanageremail = i[6]
        cdwPartnermanagerphone = i[7]
        cdwVendorstatus = i[8]
        vendorList = i
        print('Vendor Name: %s') % vendorName
        print(vendorContactname)
        print(vendorContactemail)
        #print('Vendor: %s Certfication Level: %s Contact: %s E-Mail: %s Phone: %s') % (vendorName,vendorCertificationlevel,vendorContactname,vendorContactemail,vendorContactphone)
    else:
        print('No matching vendor found')
        



        

