# State [Done, Unassigned, Assigned]
from datetime import datetime
import admin as ad
from model.Seeker import Seeker
from model.User import User


class Job:
    stages = ['Pending', 'Published', 'Rejected', 'Closed']
    fields_name = ['id', 'subject', 'level', 'location', 'time', 'frequency', 'rate', 'additional_note', 'stage', 'rejected_reason',
                   'created_by', 'created_on', 'modified_on', 'assignedUser', 'interestedUser']
    bold_terms = ['*Subject* :', '*Level* :', '*Location* :', '*Time* :', '*Frequency* :', '*Rate* :', '*Additional Note* :']
    terms = ['Subject :', 'Level :', 'Location :', 'Time :', 'Frequency :', 'Rate :', 'Additional Note :']

    def __init__(self, id, subject, level, location, time, frequency, rate, additional_note, created_by):
        self.id = id
        self.subject = subject
        self.level = level
        self.location = location
        self.time = time
        self.frequency = frequency
        self.rate = rate
        self.additional_note = additional_note
        self.created_on = datetime.today()
        self.modifiedOn = datetime.today()
        self.stage = self.stages[0]
        self.created_by = created_by
        self.rejected_reason = None
        self.assignedUser = None
        self.interestedUser = []

    @staticmethod
    def getFields_name():
        return Job.fields_name

    @staticmethod
    def getTerms():
        return Job.terms

    @staticmethod
    def getBoldTerms():
        return Job.bold_terms

    def setRejectedReason(self, reason):
        self.rejected_reason = reason
        ad.saveJobDict()

    def setAssignedUser(self, seeker: Seeker):
        if self.stage == self.stages[1] and self.created_by != seeker.id:
            self.assignedUser = seeker
            self.stage = self.stages[3]
            self.modifiedOn = datetime.today()
            ad.saveJobDict()

    def setInterestedUser(self, seeker: Seeker):
        if self.stage == self.stages[1] and self.notYetAdded(seeker) and self.created_by != seeker.id:
            self.interestedUser.append(seeker)
            ad.saveJobDict()

    def reject(self, seeker: Seeker):
        newList = []
        if self.stage == self.stages[1]:
            for u in self.interestedUser:
                if u.id == seeker.id:
                    continue
                else:
                    newList.append(u)
        self.interestedUser = newList
        return True

    def notYetAdded(self, seeker):
        for u in self.interestedUser:
            if seeker.id == u.id:
                return False
        return True

    def publish(self):
        self.stage = self.stages[1]
        self.modifiedOn = datetime.today()
        ad.saveJobDict()

    def isPublish(self):
        return self.stage == self.stages[1]

    def isPending(self):
        return self.stage == self.stages[0]

    def rejected(self, reason):
        self.stage = self.stages[2]
        self.modifiedOn = datetime.today()
        self.rejected_reason = reason
        ad.saveJobDict()

    def closed(self):
        self.stage = self.stages[3]
        self.modifiedOn = datetime.today()
        ad.saveJobDict()

    def updateNewJobInfo(self, id, created_on, created_by, assignedUser, interestedUser):
        self.id = id
        self.modifiedOn = datetime.today()
        self.created_on = created_on
        self.created_by = created_by
        self.assignedUser = assignedUser
        self.interestedUser = interestedUser

    def toPostingString(self):
        return '*Subject* : {}' \
               '*Level* : {}' \
               '*Location* : {}' \
               '*Time* : {}' \
               '*Frequency* : {}' \
               '*Rate* : {}' \
               '*Additional Note* : {}'.format(self.subject, self.level, self.location, self.time, self.frequency,
                                             self.rate, self.additional_note)

    def toString(self):
        return '*Subject* : {}' \
               '*Level* : {}' \
               '*Location* : {}' \
               '*Time* : {}' \
               '*Frequency* : {}' \
               '*Rate* : {}' \
               '*Additional Note* : {}' \
               '\n*Stage*: {}'.format(self.subject, self.level, self.location, self.time, self.frequency,
                                    self.rate, self.additional_note, self.stage)

    def toExcelRow(self):
        interestedUserString = ''
        for u in self.interestedUser:
            interestedUserString += u.toString()
        interestedUserString.replace('\n', '')
        return {'id': self.id,
                'subject': self.subject.replace('\n', ''),
                'level': self.level.replace('\n', ''),
                'location': self.location.replace('\n', ''),
                'time': self.time.replace('\n', ''),
                'frequency': self.frequency.replace('\n', ''),
                'rate': self.rate.replace('\n', ''),
                'additional_note': self.additional_note.replace('\n', ''),
                'stage': self.stage,
                'created_by': self.created_by,
                'created_on': self.created_on,
                'modified_on': self.modifiedOn,
                'rejected_reason': self.rejected_reason if self.rejected_reason != None else 'None',
                'assignedUser': self.assignedUser.toString() if self.assignedUser != None else 'None',
                'interestedUser': interestedUserString}
g