# State [Done, Unassigned, Assigned]
from datetime import datetime
import admin as ad

class Job:
    stages = ['Pending', 'Published', 'Rejected', 'Closed']
    fields_name = ['id', 'subject', 'level', 'location', 'time', 'frequency', 'rate', 'additional_note', 'stage',
                   'created_by', 'created_on', 'modified_on']

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

    @staticmethod
    def getFields_name():
        return Job.fields_name

    def publish(self):
        self.stage = self.stages[1]
        self.modifiedOn = datetime.today()
        ad.saveJobDict()

    def rejected(self):
        self.stage = self.stages[2]
        self.modifiedOn = datetime.today()
        ad.saveJobDict()

    def closed(self):
        self.stage = self.stages[3]
        self.modifiedOn = datetime.today()
        ad.saveJobDict()

    def setId(self, id, created_on):
        self.id = id
        self.modifiedOn = datetime.today()
        self.created_on = created_on

    def toPostingString(self):
        return 'Subject : {}' \
               'Level : {}' \
               'Location : {}' \
               'Time : {}' \
               'Frequency : {}' \
               'Rate : {}' \
               'Additional Note : {}'.format(self.subject, self.level, self.location, self.time, self.frequency,
                                             self.rate, self.additional_note)

    def toString(self):
        return 'Subject : {}' \
               'Level : {}' \
               'Location : {}' \
               'Time : {}' \
               'Frequency : {}' \
               'Rate : {}' \
               'Additional Note : {}' \
               '\nStage: {}'.format(self.subject, self.level, self.location, self.time, self.frequency,
                                    self.rate, self.additional_note, self.stage)

    def toExcelRow(self):
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
                'modified_on': self.modifiedOn}
