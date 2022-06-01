from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd

#from PIL import Image
import numpy as np
import random
from random import choices
import xlsxwriter

import mimetypes

import os
from project290.settings import BASE_DIR

from chardet import detect

# Create your views here.
def ransol(fieldsList):
    n=10
    l=[]
    for i in range(n):
        s=[]
        for a,b in fieldsList:
            c=random.randint(0,(len(b)-1))
            s.append(b[c])
        l.append(s)
    return l
'''
def fitness(individual):
    reqDone=RequirementG.copy()
    for i in range(len(individual)):
        area=fieldsListG[i][0]
        cropY=cropYieldG[individual[i]]
        totalWeight=area*cropY
        reqDone[individual[i]]-=totalWeight
    neg=True
    fit=0
    fitall=0
    for a,b in reqDone.items():
        if b>0:
            fit+=b
            neg=False
        fitall+=b
    for i in reqDone:
        if reqDone[i]>0:
            fit+=(2*BigNumG)
            fitall+=(2*BigNumG)
    if not neg:
        return (BigNumG-fit)
    else :
        return (BigNumG-fitall)'''

def fitness(individual):
    reqDone=RequirementG.copy()
    for i in range(len(individual)):
        area=fieldsListG[i][0]
        cropY=cropYieldG[individual[i]]
        totalWeight=area*cropY
        reqDone[individual[i]]-=totalWeight
    neg=True
    crp=cropRateG
    #fit=0
    fitall=0
    for a,b in reqDone.items():
        #fitall+=b
        fitall+=b*crp[a]*cropYieldG[a]
    for i in reqDone:
        if reqDone[i]>0:
            fitall+=(2*BigNumG)
    return (BigNumG-fitall)

def pick_parent_candidates(population):
    popu=population.copy()
    fitnesses = [fitness(j) for j in popu]
    p1=choices(popu, weights=fitnesses, k=1)[0]
    ii=popu.index(p1)
    popu.pop(ii)
    fitnesses.pop(ii)
    p2=choices(popu, weights=fitnesses, k=1)[0]
    return [list(p1)]+[list(p2)]

def crossover(par1,par2):
    cp=len(par1)
    co=random.randint(0,cp-1)

    o1=[]
    o2=[]
    cc=0.6
    for i in range(0,cp):
        getrand=random.random()
        if getrand>cc:
            o1.append(par1[i])
            o2.append(par2[i])
            continue
        o1.append(par2[i])
        o2.append(par1[i])

    return [o1,o2]

def getrndcrop(n):
    c=fieldsListG[n][1]
    g=random.randint(0,len(c)-1)
    return c[g]

def mutation2(off):
    canmut=0.3
    tbr=[]
    for i in range(len(off)):
        getrand=random.random()
        if getrand>canmut:
            tbr.append(off[i])
            continue
        tbr.append(getrndcrop(i))
    return tbr

def deviation(solgen):
    soldict=RequirementG.copy()
    messages=[]
    for i in range(len(solgen)):
        soldict[solgen[i]]-=(fieldsListG[i][0])*cropYieldG[solgen[i]]
    for j in soldict:
        if soldict[j]>0:
            print("Solution lags in",j,"by",soldict[j])
            messages.append("Solution lags in "+j+" by "+str(soldict[j]))
        else:
            print("Conditions for",j,"are met")
            messages.append("Conditions for "+j+" are met, the surplus = "+ str(-1*soldict[j])+" & Profit = "+str(-1*soldict[j]*cropRateG[j]))
    return (soldict,messages)

def geneticAlgo(ip):
    ta=ip.copy()
    generations=400
    for i in range(generations+1):
        a,b=pick_parent_candidates(ta)
        oa,ob=crossover(a,b)
        oa=mutation2(oa)
        ob=mutation2(ob)
        ta.append(oa)
        ta.append(ob)
        ta.sort(key=fitness,reverse=True)
        ta.pop()
        ta.pop()
    print(ta[0],len(ta[0]))
    return ta[0]

def findSolution(fieldsList,cropYield,cropRate,Requirement):

    initialPop=ransol(fieldsList)
    print(initialPop)

    global fieldsListG
    fieldsListG=fieldsList
    global cropYieldG
    cropYieldG=cropYield
    global cropRateG
    cropRateG=cropRate
    global RequirementG
    RequirementG=Requirement
    global BigNumG

    BigNumG=10000000007
    '''for i in Requirement:
        BigNumG+=Requirement[i]'''

    result=geneticAlgo(initialPop)

    #result=maximize_profit(result)

    deviation(result)

    return result

def first(request):
    return render(request,'firstpage.html')

def fieldForm(request):
    n=request.POST['fieldNum']
    n=int(n)
    ns=n*"1"
    return render(request,'fieldsForm.html',{"fields":ns})

def fieldsSubmit(request):
    allFields=[]
    for i in request.POST:
        if 'field' in i:
            allFields.append(request.POST.getlist(i))


    for i in range(len(allFields)):
        allFields[i]=(float(allFields[i][1]),allFields[i][2].split(","))

    print(allFields)

    cy={}
    for i in cropDatOn:
        cy[i]=float(cropDatOn[i][0])


    cr={}
    for i in cropDatOn:
        cr[i]=float(cropDatOn[i][1])

    sltn=findSolution(allFields,cy,cr,gcrdat)

    fieldSolution=[]
    for i in range(len(sltn)):
        infs=[]
        infs.append(i+1)
        infs.append(allFields[i][0])
        infs.append(",".join(allFields[i][1]))
        infs.append(sltn[i])
        fieldSolution.append(infs)

    print(fieldSolution)

    message=(deviation(sltn))[1]

    global FinalSolution
    FinalSolution = [["Field ID","area","available","recommended"]]+fieldSolution

    FinalSolution=tuple(FinalSolution)

    print("This right here ______________ ",FinalSolution)

    return render(request,'ViewFields.html',{"ThisTable":fieldSolution,'Messages':message})

def excelpage(request):
    return render(request,'xcelupload.html')

def Decodexl(request):
    cropData=request.FILES['excelfile1']
    vilReq=request.FILES['excelfile2']
    fieldsDat=request.FILES['excelfile3']

    cropData=pd.read_excel(cropData)
    vilReq=pd.read_excel(vilReq)
    fieldsDat=pd.read_excel(fieldsDat)

    cropDataDict=cropData.set_index('Name').T.to_dict('list')
    print(cropDataDict)

    cropYield={}
    for i in cropDataDict:
        cropYield[i]=cropDataDict[i][0]

    cropRate={}
    for i in cropDataDict:
        cropRate[i]=cropDataDict[i][1]

    vilReqDict=vilReq.set_index('Crop').T.to_dict('list')
    for i in vilReqDict:
        vilReqDict[i]=vilReqDict[i][0]
    print(vilReqDict)


    fieldsDatDict=fieldsDat.set_index('ID').T.to_dict('list')
    print(fieldsDatDict)

    fieldsData=[]

    for i in fieldsDatDict:
        area=float(fieldsDatDict[i][0])
        crops1=fieldsDatDict[i][1].split(",")
        fieldsData.append((area,crops1))

    print(fieldsData)



    solution=findSolution(fieldsData,cropYield,cropRate,vilReqDict)

    fieldSolution=[]
    for i in range(len(solution)):
        infs=[]
        infs.append(i+1)
        infs.append(fieldsData[i][0])
        infs.append(",".join(fieldsData[i][1]))
        infs.append(solution[i])
        fieldSolution.append(infs)

    print(fieldSolution)

    global FinalSolution
    FinalSolution = [["Field ID","area","available","recommended"]]+fieldSolution

    FinalSolution=tuple(FinalSolution)

    print("This right here ______________ ",FinalSolution)

    message=(deviation(solution))[1]

    return render(request,'ViewFields.html',{'ThisTable':fieldSolution,'Messages':message})


def onDatPage(request):
    return render(request,'Nums.html')

def cropEntryPage(request):
    cropNum=int(request.POST['CropVar'])
    fieldNum=int(request.POST['TotFields'])

    global fieldNumsOn
    fieldNumsOn=fieldNum

    print(cropNum)
    print(fieldNum)

    loopCount="1"*int(cropNum)
    return render(request,'cropEntry.html',{'cropVar':loopCount})

def ReqPage(request):
    global cropDatOn
    global cropNamesOn

    cropDatOn={}

    cropNamesOn=[]

    for i in request.POST:
        if 'crop' in i:
            cropNamesOn.append((request.POST.getlist(i))[0])
            cropDatOn[(request.POST.getlist(i))[0]]=[request.POST.getlist(i)[1:3]][0]

    print(cropDatOn)
    print(cropNamesOn)

    return render(request,'reqPage.html',{'cropnames':cropNamesOn})


def fieldsEntryPage(request):
    rr=request.POST.getlist('RequirementsOn')

    global gcrdat
    gcrdat={}

    for i in range(len(cropNamesOn)):
        gcrdat[cropNamesOn[i]]=float(rr[i])

    print(gcrdat)

    fielNum=fieldNumsOn*"1"

    return render(request,'fieldsForm.html',{'fields':fielNum})

def landpage(request):
    return render(request,'LandingPage.html')

def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

def dloadxl(request):

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('Expenses01.xlsx')
    worksheet = workbook.add_worksheet()

    # Some data we want to write to the worksheet.
    expenses = FinalSolution

    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0

    # Iterate over the data and write it out row by row.
    for Field,area,available,recommended in expenses:
        worksheet.write(row, col,     Field)
        worksheet.write(row, col + 1, area)
        worksheet.write(row, col + 2, available)
        worksheet.write(row, col + 3, recommended)
        row += 1

    # Write a total using a formula.
    #worksheet.write(row, 0, 'Total')
    #worksheet.write(row, 1, '=SUM(B1:B4)')

    workbook.close()

    # fill these variables with real values
    fl_path = os.path.join(BASE_DIR, '')
    filename = 'Expenses01.xlsx'

    print(get_encoding_type(fl_path+filename))

    fl = open(fl_path+filename, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response
