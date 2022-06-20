from asyncore import write
from urllib import response
from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.contrib.auth import logout
from home import views
from datetime import datetime as dt
from django.contrib.auth.decorators import login_required
import uuid , re
import qrcode
from PIL import Image , ImageDraw , ImageFont
from .models import TeacherData
import csv
import xlwt
#---------------------------------------
# Firebase Module Block
#---------------------------------------
import pyrebase
import os

from verifID.settings import HOME_DIR
from . import credentials
#Firebase Connection
def FirebaseConnection():
    firebaseConfigdefault = {
                        'apiKey': credentials.FIREBASE_API_KEY,
                        'authDomain': credentials.FIREBASE_AUTH_DOMAIN,
                        'projectId': credentials.FIREBASE_PROJECT_ID,
                        'databaseURL': credentials.FIREBASE_DATABASE_URL,
                        'storageBucket': credentials.FIREBASE_STORAGE_BUCKET,
                        'messagingSenderId': credentials.FIREBASE_SENDER_ID,
                        'appId': credentials.FIREBASE_APP_ID,
                        'measurementId': credentials.FIREBASE_MEASUREMENT_ID,
    }
    firebase = pyrebase.initialize_app(firebaseConfigdefault)
    return firebase
#Firebase Storage Initialize
def fireStore():
    myFireStore = FirebaseConnection().storage()
    return myFireStore
# Firebase Real Time Database Initialize
def fireData():
    myFireDB = FirebaseConnection().database()
    return myFireDB
#Individual Routine Access
def get_routine(teacherName):
    destinationPath = teacherName+"/routine.jpg"
    fireStoreObject = fireStore()
    imgurl =  fireStoreObject.child(destinationPath).get_url(None)
    return imgurl
#Download Routine 
import requests
def get_routineDownloaded(request):
    fname = request.user.first_name
    lname = request.user.last_name
    teacherName = fname + lname
    downPath = teacherName+"/routine.jpg"
    fireStoreObject = fireStore()
    downloadURL = fireStoreObject.child(downPath).get_url(None)
    response = HttpResponse(content_type = "image/png")
    response['Content-Disposition'] = "attachment;filename=image.png"
    response.write(requests.get(downloadURL).content)
    return response
#Download ID
def get_idDownloaded(request):
    fname = request.user.first_name
    lname = request.user.last_name
    teacherName = fname + lname
    downPath = teacherName+"/idCard.png"
    fireStoreObject = fireStore()
    downloadURL = fireStoreObject.child(downPath).get_url(None)
    response = HttpResponse(content_type = "image/png")
    response['Content-Disposition'] = "attachment;filename=idCard.png"
    response.write(requests.get(downloadURL).content)
    return response
#--------------------------------
# End
#--------------------------------
# MongoDB Atlas Module Block
#--------------------------------
import pymongo
from pymongo import MongoClient
from . import credentials
def mongoAttendanceDB(timeStamp,subjectCode,attendanceList):
    # For Successful Insertion
    insertFlag = True
    # cluster URL
    clusterURL = "mongodb+srv://"+credentials.MONGODB_USERNAME+":"+credentials.MONGODB_PASSWORD+"@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority"
    # setup Connection with cluster
    myCluster = MongoClient(clusterURL,tls=True,tlsAllowInvalidCertificates=True)
    # setup connection with database
    myDB = myCluster["attendanceMCKVIE"]
    # setup connnection with collection
    myCollection = myDB[subjectCode]
    myData = {
        'timeStamp':timeStamp,
        'hasData':True,
        'AttendanceList':attendanceList,
    }
    checkDuplicate = myCollection.find_one({'timeStamp':timeStamp})
    if checkDuplicate is not None:
        checkDuplicateObject = checkDuplicate['hasData']
    else:
        checkDuplicateObject = False
    if checkDuplicateObject is True:
        insertFlag = False
        pass
    else:
        myCollection.insert_one(myData)
    return insertFlag

def archive(request):
    if request.method == "POST":
        subject_code = request.POST['subjectcode']
        response = HttpResponse(content_type = "application/ms-excel")
        response['Content-Disposition'] = "attachment;filename=attendance"+ subject_code +".xls"
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(subject_code)
        # cluster URL
        clusterURL = "mongodb+srv://"+credentials.MONGODB_USERNAME+":"+credentials.MONGODB_PASSWORD+"@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority"
        # setup connection with cluster
        myCluster = MongoClient(clusterURL,tls=True,tlsAllowInvalidCertificates=True)
        # setup connection with database
        myDB = myCluster["attendanceMCKVIE"]
        myClassDB = myCluster["studentData"]
        # setup connnection with collection
        myCollection = myDB[subject_code]
        myClassCollection = myClassDB["CSE"]
        collectionsCount = myCollection.count_documents({})
        collectionsData = myCollection.find({})
        columns = list()
        columns.append("Roll")
        columns.append("Name")
        for i in range(collectionsCount):
            columns.append(collectionsData[i]['timeStamp'])
        for colNum in range(len(columns)):
            ws.write(0,colNum,columns[colNum])
        batchInfoDoc = myClassCollection.find_one({'batch':'2019-23','currentSem':6})
        totalClassStrength = batchInfoDoc['totalStrength']
        rowData = list()
        for rowNum in range(1,totalClassStrength+1):
            rowData.append(rowNum)
            studentName = myClassCollection.find_one({'Roll':rowNum})
            rowData.append(studentName['Name'])
            for j in range(collectionsCount):
                rowData.append(collectionsData[j]['AttendanceList'][rowNum])
            for k in range(len(rowData)):
                ws.write(rowNum,k,rowData[k])
            rowData.clear()
        wb.save(response)
        return response
    return render(request,'teachers/archivedata.html')

def getClassStrength(stream):
    # cluster URL
    clusterURL = "mongodb+srv://"+credentials.MONGODB_USERNAME+":"+credentials.MONGODB_PASSWORD+"@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority"
    # setup connection with cluster
    myCluster = MongoClient(clusterURL,tls=True,tlsAllowInvalidCertificates=True)
    # setup connection with database
    myDB = myCluster["studentData"]
    # setup connnection with collection
    myCollection = myDB[stream]
    data = myCollection.find_one({'batch':'2019-23','currentSem':6})
    totalStrength = data['totalStrength']
    return totalStrength

def setAncLog(collectionName,filePath,subjectCode,about,dateOfSubmit):
    # cluster URL
    clusterURL = "mongodb+srv://"+credentials.MONGODB_USERNAME+":"+credentials.MONGODB_PASSWORD+"@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority"
    # setup connection with cluster
    myCluster = MongoClient(clusterURL,tls=True,tlsAllowInvalidCertificates=True)
    # setup connection with database
    myDB = myCluster["announcementData"]
    # setup connnection with collection
    myCollection = myDB[collectionName]
    timeStamp = dt.now().strftime('%d-%m-%y')
    data = {
        'subjectCode':subjectCode,
        'about':about,
        'datePosted': timeStamp,
        'dateOfSubmit':dateOfSubmit,
        'filePath':filePath,
    }
    myCollection.insert_one(data)
#---------------------------------
# End
#---------------------------------


# My views here.
@login_required(login_url='home')
def dashboard(request):
    return render(request,'teachers/dash.html')    

def routineTeacher(request):
    fname = request.user.first_name
    lname = request.user.last_name
    if request.method == "POST":
        return redirect('downloadRoutine')
    img_url = get_routine(fname+lname)
    context = {
        'url' :img_url
    }
    #os.chdir(HOME_DIR)
    return render(request,'teachers/routine.html',context)

def announcement(request):
    if request.method == "POST":
        announcementText = request.POST['announcement']
        subjectCode = request.POST['subjectcodeanc']
        timeStamp = dt.now().strftime('%d/%m/%y')
        teacherName = request.user.get_full_name()
        data = {
            'date':timeStamp,
            'teacher':teacherName,
            'text':announcementText,
            'seen':False,
            'subjectCode':subjectCode,
        }
        myFireDBObject = fireData()
        myFireDBObject.push(data)
    return render(request,'teachers/postAnn.html')

def attendance(request):
    if request.method == "POST":
        subjectCode = request.POST["subjectCode"]
        attendanceList = request.POST["attendanceList"]
        try:
            attendanceList = list(map(int,attendanceList.split(',')))
        except:
            attendanceList = list(map(int,attendanceList.split(' ')))
        logBook = list()
        logBook.append('null')
        for i in range(1,getClassStrength("CSE")+1):
            if i in attendanceList:
                logBook.append('P')
            else:
                logBook.append('A')
        timeStamp = dt.now().strftime('%d/%m/%y')
        returnValue = mongoAttendanceDB(timeStamp,subjectCode,logBook)
        if returnValue is False:
            return HttpResponse("Data Record present")
    return render(request,'teachers/attendance.html')

def myid(request):
    teacherDataObject = TeacherData.objects.all().get(email = request.user.email)
    # get device id
    macAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    # uniqueid
    uniqueId = teacherDataObject.deviceid
    if macAddress != uniqueId:
        return HttpResponse("Device not Registered")
    # make qr
    qr_img = qrcode.make(teacherDataObject.collegeid) 
    os.chdir(os.path.join(HOME_DIR+"\\etc"))
    qr_img.save("qr.jpg")
    # make idcard
    template = Image.open("template.png")
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("Ubuntu-Regular.ttf",size=26)
    draw.text((366,245),dt.now().strftime('%d/%m/%Y'),fill = "black",font=font)
    nameOfUser = teacherDataObject.firstname + " " + teacherDataObject.lastname
    draw.text((376,115),nameOfUser,fill = "black",font=font)
    draw.text((473,160),teacherDataObject.designation,fill = "black",font=font)
    draw.text((371,210),teacherDataObject.department,fill = "black",font=ImageFont.truetype("Ubuntu-Regular.ttf",size=20))
    pic = Image.open('qr.jpg').resize((196,218),Image.ANTIALIAS)
    template.paste(pic,(61,116,257,334))
    template.save("idCard.png")
    fireStoreObject = fireStore()
    path = request.user.first_name + request.user.last_name + "/idCard.png"
    fireStoreObject.child(path).put("idCard.png")
    return redirect('downloadid')

def uploadAssignment(request):
    if request.method == "POST":
        fileName = dt.now().strftime("%d%m%Y%H%M%S") + "assignment.jpeg"
        fireStoreObject = fireStore()
        path = request.user.first_name + request.user.last_name + '/upload/' + fileName
        fireStoreObject.child(path).put(request.FILES['asgimg'])
        filePath = fireStoreObject.child(path).get_url(None)
        description = request.POST['aboutannc']
        subjectCode = request.POST['subjectcode']
        dateOfSubmit = request.POST['dos']
        setAncLog("collection01",filePath,subjectCode,description,dateOfSubmit)
    return render(request,'teachers/uploadAssignment.html')