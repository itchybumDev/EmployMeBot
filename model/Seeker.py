# State [Done, Unassigned, Assigned]
from datetime import datetime


class Seeker:
    bold_terms = ['*Name* :', '*Gender* :', '*Education Level* :', '*Occupation* :', '*Experience* :',
                  '*Contact Number* :',
                  '*Additional Note* :']
    terms = ['Name :', 'Gender :', 'Education Level :', 'Occupation :', 'Experience :', 'Contact Number :',
             'Additional Note :']
    fields_name = ['first_name', 'full_name', 'id', 'is_bot', 'last_name', 'name', 'gender', 'education_level',
                   'occupation', 'experience', 'contact_number', 'note', 'created_on', 'modifiedOn']

    @staticmethod
    def getFields_name():
        return Seeker.fields_name

    @staticmethod
    def getTerms():
        return Seeker.terms

    @staticmethod
    def getBoldTerms():
        return Seeker.bold_terms

    def __init__(self, first_name, full_name, id, is_bot, last_name, name, gender, education_level, occupation
                 , experience, contact_number, note):
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
        self.contact_number = contact_number
        self.note = note
        self.created_on = datetime.today()
        self.modifiedOn = datetime.today()

    def toPostingString(self):
        return '*Name* : {}' \
               '*Gender* : {}' \
               '*Education Level* : {}' \
               '*Occupation* : {}' \
               '*Experience* : {}' \
               '*Contact Number* : {}' \
               '*Additional Note* : {}'.format(self.name, self.gender, self.education_level, self.occupation,
                                               self.experience, self.contact_number, self.note)

    def toString(self):
        return 'Seeker {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}'.format(self.first_name,
                                                                                       self.full_name,
                                                                                       self.id,
                                                                                       self.is_bot,
                                                                                       self.last_name,
                                                                                       self.name,
                                                                                       self.gender,
                                                                                       self.education_level,
                                                                                       self.occupation,
                                                                                       self.note,
                                                                                       self.experience,
                                                                                       self.contact_number)

    def toExcelRow(self):
        return {'first_name': self.first_name,
                'full_name': self.full_name.replace('\n', '') if self.full_name != None else 'None',
                'id': self.id,
                'is_bot': self.is_bot,
                'last_name': self.last_name.replace('\n', '') if self.last_name != None else 'None',
                'name': self.name.replace('\n', '') if self.name != None else 'None',
                'gender': self.gender.replace('\n', '') if self.gender != None else 'None',
                'education_level': self.education_level.replace('\n', '') if self.education_level != None else 'None',
                'occupation': self.occupation.replace('\n', '') if self.occupation != None else 'None',
                'experience': self.experience.replace('\n', '') if self.experience != None else 'None',
                'contact_number': self.contact_number.replace('\n', '') if self.contact_number != None else 'None',
                'note': self.note.replace('\n', '') if self.note != None else 'None',
                'created_on': self.created_on,
                'modifiedOn': self.modifiedOn}
