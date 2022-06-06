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
#---------------------------------------
# Firebase Module Block
#---------------------------------------
import pyrebase
import os

from verifID.settings import HOME_DIR
#Firebase Connection
def FirebaseConnection():
    firebaseConfigdefault = {
                        'apiKey': "AIzaSyCsTnnNo2xWxC4eUGXo_mz6tAZrppEmwjc",
                        'authDomain': "verifid-3868b.firebaseapp.com",
                        'projectId': "verifid-3868b",
                        'databaseURL': "https://verifid-3868b-default-rtdb.firebaseio.com",
                        'storageBucket': "verifid-3868b.appspot.com",
                        'messagingSenderId': "689321406534",
                        'appId': "1:689321406534:web:5f557e74e0a683c47d5a47",
                        'measurementId': "G-E8631GH36G"
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
def get_routineDownloaded(teacherName):
    try:
        os.mkdir("c:\\verifidDownloads")
    except:
        pass
    os.chdir("c:\\verifidDownloads")
    downPath = teacherName+"/routine.jpg"
    fireStoreObject = fireStore()
    fireStoreObject.child(downPath).download(filename="download.jpg",path="")
#--------------------------------
# End
#--------------------------------
# MongoDB Atlas Module Block
#--------------------------------
import pymongo
from pymongo import MongoClient
def mongoAttendanceDB(timeStamp,subjectCode,attendanceList):
    # For Successful Insertion
    insertFlag = True
    # setup Connection with cluster
    myCluster = MongoClient("mongodb+srv://teacher_mckvie:Kookaburra06@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)
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
    if request.method == "GET":
        get_routineDownloaded(fname+lname)
    img_url = get_routine(fname+lname)
    context = {
        'url' :img_url
    }
    os.chdir(HOME_DIR)
    return render(request,'teachers/routine.html',context)

def announcement(request):
    if request.method == "POST":
        announcementText = request.POST['announcement']
        timeStamp = dt.now().strftime('%d/%m%y')
        teacherName = request.user.get_full_name()
        data = {
            'date':timeStamp,
            'teacher':teacherName,
            'text':announcementText,
            'seen':False,
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
        for i in range(1,73):
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
    try:
        os.mkdir("c:\\verifidDownloads")
    except:
        pass
    os.chdir("c:\\verifidDownloads")
    template.save("idCard.png")
    #reset dir
    os.chdir(HOME_DIR)
    return render(request,'teachers/dash.html')

def uploadAssignment(request):
    if request.method == "POST":
        fileName = dt.now().strftime("%d%m%Y%H%M%S") + "assignment.jpeg"
        fireStoreObject = fireStore()
        path = request.user.first_name + request.user.last_name + '/upload/' + fileName
        print(path)
        fireStoreObject.child(path).put(request.FILES['asgimg'])
    return render(request,'teachers/uploadAssignment.html')