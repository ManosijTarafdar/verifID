from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teachers import views as teacherAuthViews
from teachers import credentials as cred
from pymongo import MongoClient
import pyrebase

# Create your views here.
@login_required(login_url='home')
def home(request):
    return render(request,'students/studentHome.html')

@login_required(login_url='studentHome')
def announcements(request):
    myFireRDB = teacherAuthViews.fireData()
    dataList = myFireRDB.get()
    subDataList = list()
    dataListObject = list()
    for i in dataList:
        dataListObject.append(i.val()['subjectCode'])
        dataListObject.append(i.val()['date'])
        dataListObject.append(i.val()['teacher'])
        dataListObject.append(i.key())
        subDataList.append(dataListObject.copy())
        dataListObject.clear()
    context = {
        'dataList':subDataList[::-1],
    }
    return render(request,'students/announcement.html',context)

def view_announcement(request,id):
    myFireRDB = teacherAuthViews.fireData()
    dataList = myFireRDB.child(id).get()
    about = dataList.val()['text']
    return HttpResponse(about)

def assignments(request):
    # cluster URL
    clusterURL = "mongodb+srv://"+cred.MONGODB_USERNAME+":"+cred.MONGODB_PASSWORD+"@attendanccedb.vkkyk.mongodb.net/?retryWrites=true&w=majority"
    # setup connection with cluster
    myCluster = MongoClient(clusterURL,tls=True,tlsAllowInvalidCertificates=True)
    # setup connection with database
    myDB = myCluster["announcementData"]
    # setup connnection with collection
    collectionName = "collection01"
    myCollection = myDB[collectionName]
    dataList = myCollection.find({})
    subDataList = list()
    subDataListObject = list()
    for data in dataList:
        subDataListObject.append(data['subjectCode'])
        subDataListObject.append(data['about'])
        subDataListObject.append(data['datePosted'])
        subDataListObject.append(data['dateOfSubmit'])
        subDataListObject.append(data['filePath'])
        subDataList.append(subDataListObject.copy())
        subDataListObject.clear()
    context = {
        'dataList':subDataList,
    }
    return render(request,'students/assignments.html',context)