import csv
import pickle

from model.Job import Job
from model.User import User

user_dict = {}
dev_team = []
job_dict = {}

def loadDataOnStartup():
    loadUserDict()
    loadDevTeam()
    loadJobDict()


def getJobDict():
    return job_dict


def addNewJob(job : Job):
    print("Attempt to add new job")
    if job.id in job_dict:
        print('Job is already in the database')
        return job_dict.get(job.id)
    else:
        print('New Job added')
        job_dict.setdefault(job.id, job)
        saveJobDict()
        return job


def updateJob(job: Job):
    print('Updating job')
    job_dict[job.id] = job
    saveJobDict()
    return job


def saveJobDict():
    global job_dict
    with open("./db/jobData.pickle", 'wb') as handle:
        pickle.dump(job_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("./db/jobData.csv", 'w', newline='') as file:
        fieldnames = Job.getFields_name()
        writer = csv.DictWriter(file, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for v in job_dict.values():
            writer.writerow(v.toExcelRow())
    return True


def loadJobDict():
    global job_dict
    try:
        with open('./db/jobData.pickle', 'rb') as handle:
            job_dict = pickle.load(handle)
            print(job_dict)
    except IOError:
        print("Job Dict data is not found, initialize to empty")


def getJobDict():
    return job_dict

def getUserDict():
    return user_dict


def addUser(user : User):
    print("Attempt to add new user")
    if user.id in user_dict:
        print('User is already in the database')
        return user_dict.get(user.id)
    else:
        print('New User added')
        user_dict.setdefault(user.id, user)
        saveUserDict()
        return user


def saveUserDict():
    global user_dict
    with open("./db/userData.pickle", 'wb') as handle:
        pickle.dump(user_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("./db/userData.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in user_dict.values():
            writer.writerow(v.toExcelRow())
    return True


def loadUserDict():
    global user_dict
    try:
        with open('./db/userData.pickle', 'rb') as handle:
            user_dict = pickle.load(handle)
    except IOError:
        print("User Dict data is not found, initialize to empty")


def loadDevTeam():
    with open("./db/dev_team.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            dev_team.append(str(row[0]))


def saveDevTeam():
    with open("./db/dev_team.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for v in dev_team:
            writer.writerow([v])
    return True
