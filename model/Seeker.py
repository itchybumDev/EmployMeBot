# State [Done, Unassigned, Assigned]
from datetime import datetime


class Seeker:

    bold_terms = ['*Name* :', '*Gender* :', '*Education Level* :', '*Occupation* :', '*Experience* :',
                  '*Additional Note* :']
    terms = ['Name :', 'Gender :', 'Education Level :', 'Occupation :', 'Experience :', 'Additional Note :']
    fields_name = ['first_name', 'full_name', 'id', 'is_bot', 'last_name', 'name', 'gender', 'education_level',
                   'occupation', 'experience','note', 'created_on', 'modifiedOn']

    @staticmethod
    def getFields_name():
        return Seeker.fields_name

    @staticmethod
    def getTerms():
        return Seeker.terms

    @staticmethod
    def getBoldTerms():
        return Seeker.bold_terms

    def __init__(self, first_name, full_name, id, is_bot, last_name, name, gender, education_level, occupation, experience, note):
        self.first_name = first_name
        self.full_name = full_name
        self.id = id
        self.is_bot = is_bot
        self.last_name = last_name
        self.name = name
        self.gender = gender
        self.education_level = education_level
        self.occupation = occupation
        self.experience = experience
        self.note = note
        self.created_on = datetime.today()
        self.modifiedOn = datetime.today()

    def toPostingString(self):
        return '*Name* : {}' \
               '*Gender* : {}' \
               '*Education Level* : {}' \
               '*Occupation* : {}' \
               '*Experience* : {}' \
               '*Additional Note* : {}'.format(self.name, self.gender, self.education_level, self.occupation,
                                               self.experience, self.note)

    def toString(self):
        return 'Seeker {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}'.format(self.first_name,
                                                                     self.full_name,
                                                                     self.id,
                                                                     self.is_bot,
                                                                     self.last_name,
                                                                     self.name,
                                                                     self.gender,
                                                                     self.education_level,
                                                                     self.occupation,
                                                                     self.note,
                                                                     self.experience)

    def toExcelRow(self):
        return {'first_name': self.first_name,
                'full_name': self.full_name.replace('\n', ''),
                'id': self.id,
                'is_bot': self.is_bot.replace('\n', ''),
                'last_name': self.last_name.replace('\n', ''),
                'name': self.name.replace('\n', ''),
                'gender': self.gender.replace('\n', ''),
                'education_level': self.education_level.replace('\n', ''),
                'occupation': self.occupationreplace('\n',''),
                'experience': self.experiencereplace('\n',''),
                'note': self.notereplace('\n',''),
                'created_on': self.created_on,
                'modifiedOn': self.modifiedOn}