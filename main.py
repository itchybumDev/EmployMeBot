import configparser
import logging
import random
import sys

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext.dispatcher import run_async
from telegram.utils import helpers

import admin as ad
from const import *
from logging_handler import logInline
from model.Job import Job
from model.Seeker import Seeker
from model.User import User

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

FIRST, POSTING, REGISTERING_JOB, ADD_SEEKER, SUBMIT_JOB_INTEREST, CHOOSING_SEEKER, ADD_JOB, CHOOSING_EDIT_CLOSE_JOB, UPDATE_JOB, \
UPDATE_STAGE, REJECTION_REASON, NOTIFY_DECISION = range(12)


#TuitionBotSg
channel = [-1001215957440]


class authorize:
    def __init__(self, f):
        self._f = f

    def __call__(self, *args):
        if str(args[0].effective_chat.id) in ad.dev_team:
            return self._f(*args)
        else:
            raise Exception('Alpaca does not want to you use this command.')


@run_async
def unknown(update, context):
    send_plain_text(update, context, "Sorry, I didn't understand that command.\nRun /start to see available options")


@logInline
@run_async
def start(update, context):
    payload = context.args
    if len(payload) != 0:
        return startFromChannel(update, context, payload)

    currUser = User(update.effective_user.first_name,
                    update.effective_user.full_name,
                    update.effective_user.id,
                    update.effective_user.is_bot,
                    update.effective_user.last_name,
                    update.effective_user.name)
    ad.addUser(currUser)

    keyboard = [
        [InlineKeyboardButton("Job Poster", callback_data=str('poster'))],
        [InlineKeyboardButton("Tutor", callback_data=str('tutor'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        START_TEXT.format(currUser.full_name),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


@logInline
def startFromChannel(update, context, payload):
    jobId = payload[0].replace('from-channel-', '')

    if not ad.isJobAvailableForTaking(jobId):
        context.bot.send_message(update.effective_chat.id,
                                 text=JOB_NO_LONGER_THERE,
                                 parse_mode=telegram.ParseMode.MARKDOWN)
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton('Proceed', callback_data=str(jobId))],
                [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id,
                             text=START_FROM_CHANNEL_TEXT.format(update.effective_user.full_name, ad.getJob(jobId).toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    return REGISTERING_JOB


@logInline
@run_async
@authorize
def start_admin(update, context):
    currUser = User(update.effective_user.first_name,
                    update.effective_user.full_name,
                    update.effective_user.id,
                    update.effective_user.is_bot,
                    update.effective_user.last_name,
                    update.effective_user.name)
    ad.addUser(currUser)

    send_plain_text(update, context, 'Hello Admin!')

    pendingList = []
    publishList = []
    rejectedList = []
    closedList = []

    for value in ad.getJobDict().values():
        if value.stage == Job.stages[0]:
            pendingList.append(value.id)
        elif value.stage == Job.stages[1]:
            publishList.append(value.id)
        elif value.stage == Job.stages[2]:
            rejectedList.append(value.id)
        elif value.stage == Job.stages[3]:
            closedList.append(value.id)

    if len(pendingList) != 0 or len(publishList) != 0:
        keyboard = []
        for i in pendingList:
            keyboard.append([InlineKeyboardButton('Pending - ' + i, callback_data=str(i))])
        for i in publishList:
            keyboard.append([InlineKeyboardButton('Published - ' + i, callback_data=str(i))])
        keyboard.append([InlineKeyboardButton("Quit", callback_data=str('quit'))])
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(update.effective_chat.id, text=JOB_POSTED_TEXT.format(
            ','.join(pendingList),
            ','.join(publishList),
            ','.join(rejectedList),
            ','.join(closedList), parse_mode=telegram.ParseMode.MARKDOWN), reply_markup=reply_markup)
        return CHOOSING_EDIT_CLOSE_JOB
    else:
        context.bot.send_message(update.effective_chat.id, text=JOB_POSTED_TEXT.format(
            ','.join(pendingList),
            ','.join(publishList),
            ','.join(rejectedList),
            ','.join(closedList),
        ))
        send_plain_text(update, context, JOB_POSTED_EMPTY_TEXT)
        return ConversationHandler.END


@logInline
@run_async
def postingJob(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("New Job", callback_data=str('newjob'))],
        [InlineKeyboardButton("Job Posted", callback_data=str('jobposted'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(POSTING_JOB_TEXT, reply_markup=reply_markup)
    return POSTING


@logInline
@run_async
def newJob(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query, text=NEW_JOB_TEXT)
    send_plain_text(update, context, NEW_JOB_TEXT_SAMPLE)
    keyboard = [[InlineKeyboardButton('Quit', callback_data=str('quit'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id,
                             text='Waiting for your input',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    return ADD_JOB


@logInline
@run_async
def chosingEditOrClose(update, context):
    query = update.callback_query
    selection = query.data
    query.answer()

    if selection not in ad.getJobDict():
        send_edit_text(query,
                       text=JOB_NO_LONGER_THERE)
        return ConversationHandler.END

    curr_job = ad.getJobDict().get(selection)

    if not ad.isAdmin(update.effective_chat.id):
        send_edit_text(query, text=EDIT_JOB_TEXT_1)
        send_plain_text(update, context, curr_job.toPostingString())
    else:
        send_edit_text(query, text=curr_job.toPostingString())

    # Use Case when the job is in Publish
    if curr_job.isPublish():
        keyboard = [[InlineKeyboardButton('Close Posting', callback_data=str('closeposting')),
                     InlineKeyboardButton("Quit", callback_data=str('quit'))]]
        if len(curr_job.interestedUser) != 0:
            keyboard.append([InlineKeyboardButton('View Interested Seekers', callback_data=str('interestedlist'))])
    # Use Case when job is in Pending
    elif curr_job.isPending():
        if ad.isAdmin(update.effective_chat.id):
            # Admin keyboard
            keyboard = [[InlineKeyboardButton('Publish Posting', callback_data=str('publishposting')),
                         InlineKeyboardButton('Reject Posting', callback_data=str('rejectposting'))],
                        [InlineKeyboardButton('Edit Posting', callback_data=str('editposting')),
                         InlineKeyboardButton('Close Posting', callback_data=str('closeposting'))],
                        [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
        else:
            keyboard = [[InlineKeyboardButton('Edit Posting', callback_data=str('editposting')),
                         InlineKeyboardButton('Close Posting', callback_data=str('closeposting'))],
                        [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
    # Job is in Rejected
    else:
        if ad.isAdmin(update.effective_chat.id):
            # Admin keyboard
            keyboard = [[InlineKeyboardButton('Publish Posting', callback_data=str('publishposting'))]
                        [InlineKeyboardButton('Edit Posting', callback_data=str('editposting')),
                         InlineKeyboardButton('Close Posting', callback_data=str('closeposting'))],
                        [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
        else:
            keyboard = [[InlineKeyboardButton('Edit Posting', callback_data=str('editposting')),
                         InlineKeyboardButton('Close Posting', callback_data=str('closeposting'))],
                        [InlineKeyboardButton("Quit", callback_data=str('quit'))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(update.effective_chat.id,
                             text='What do you want to do?',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    context.user_data['editJob'] = selection
    return UPDATE_STAGE


@logInline
@run_async
def interestedList(update, context):
    query = update.callback_query
    query.answer()
    selection = context.user_data['editJob']
    curr_job = ad.getJob(selection)

    keyboard = []

    for seeker in curr_job.interestedUser:
        keyboard.append([InlineKeyboardButton('{} - {} - {}'.format(seeker.name,
                                                                    seeker.gender,
                                                                    seeker.education_level).replace('\n', ''),
                                              callback_data=str(seeker.id))])
    keyboard.append([InlineKeyboardButton("Quit", callback_data=str('quit'))])

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(POSTING_JOB_TEXT, reply_markup=reply_markup)
    return CHOOSING_SEEKER


@logInline
@run_async
def choosingSeeker(update, context):
    query = update.callback_query
    query.answer()
    selection = query.data
    seeker = ad.getSeeker(selection)
    context.user_data['selectedSeeker'] = seeker

    keyboard = [[InlineKeyboardButton('Accept', callback_data=str('accept')),
                 InlineKeyboardButton('Reject', callback_data=str('reject'))],
                [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(CHOOSING_SEEKER_TEXT.format(seeker.toPostingString()),
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)
    return NOTIFY_DECISION


def accept(update, context):
    #context.user_data['editJob']
    query = update.callback_query
    query.answer()
    seeker = context.user_data['selectedSeeker']
    curr_job = ad.getJob(context.user_data['editJob'])

    curr_job.setAssignedUser(seeker)
    send_edit_text(query, ACCEPT_TEXT)
    context.bot.send_message(seeker.id,
                             text=ACCEPT_NOTIFICATION_TEXT.format(curr_job.toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


def reject(update, context):
    #context.user_data['editJob']
    query = update.callback_query
    query.answer()
    seeker = context.user_data['selectedSeeker']
    curr_job = ad.getJob(context.user_data['editJob'])

    curr_job.reject(seeker)
    send_edit_text(query, REJECT_TEXT)
    context.bot.send_message(seeker.id,
                             text=REJECT_NOTIFICATION_TEXT.format(curr_job.toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


@logInline
@run_async
def editPosting(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query,
                   text=EDIT_JOB_TEXT_2)
    return UPDATE_JOB


@logInline
def closePosting(update, context):
    query = update.callback_query
    query.answer()
    ad.getJobDict()[context.user_data['editJob']].closed()
    send_edit_text(query, text=CLOSE_JOB_TEXT.format(ad.getJobDict()[context.user_data['editJob']].toPostingString()))
    return ConversationHandler.END


@logInline
def publishPosting(update, context):
    query = update.callback_query
    query.answer()
    ad.getJobDict()[context.user_data['editJob']].publish()
    currJob = ad.getJobDict()[context.user_data['editJob']]
    send_edit_text(query, text=PUBLISH_JOB_TEXT.format(currJob.toPostingString()))
    context.bot.send_message(currJob.created_by,
                             text=PUBLISH_JOB_POSTER_TEXT.format(currJob.toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN)

    publishToChannel(currJob, context)
    return ConversationHandler.END


def publishToChannel(currJob : Job, context):
    jobId = currJob.id
    url = helpers.create_deep_linked_url(context.bot.get_me().username, ''+str(jobId))
    keyboard = [
        [InlineKeyboardButton("Register for job", url=url)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for c in channel:
        context.bot.send_message(c,
                             text=CHANNEL_NEW_JOB_POSTED_TEXT.format(currJob.toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)


@logInline
def rejectPosting(update, context):
    query = update.callback_query
    query.answer()
    currJob = ad.getJobDict()[context.user_data['editJob']]
    send_edit_text(query, text=REJECT_JOB_TEXT.format(currJob.toPostingString()))
    return REJECTION_REASON


@logInline
def rejectionReason(update, context):
    reason = update.message.text_markdown
    ad.getJobDict()[context.user_data['editJob']].rejected(reason)
    currJob = ad.getJobDict()[context.user_data['editJob']]

    send_plain_text(update, context, 'Thank you!\nJob Poster will be notified the reason')
    context.bot.send_message(currJob.created_by,
                             text=REJECT_JOB_POSTER_TEXT.format(currJob.toPostingString(), reason),
                             parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


@logInline
def updateJob(update, context):
    inputJob = update.message.text_markdown
    if not validateJob(inputJob):
        send_plain_text(update, context, "Your job posting missing certain information please try again")
        return UPDATE_JOB
    new_job = createJob(inputJob, update.effective_chat.id)
    print('UPDATE JOB - New job created \n' + new_job.toString())
    old_job = ad.getJobDict()[context.user_data['editJob']]
    new_job.updateNewJobInfo(old_job.id, old_job.created_on, old_job.created_by, old_job.assignedUser,
                             old_job.interestedUser)

    context.user_data['job'] = new_job

    keyboard = [
        [InlineKeyboardButton("Yes, updated this job", callback_data=str('doneupdatingjob'))],
        [InlineKeyboardButton("No, I want to re-submit a job", callback_data=str('reeditjob'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id,
                             text='*Updated Job Posting!*\n' + new_job.toPostingString() + '\nIs this posting correct?',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    return UPDATE_JOB


@logInline
def reSubmitEditJob(update, context):
    query = update.callback_query
    query.answer()
    if context.user_data['editJob'] in ad.getJobDict():
        send_edit_text(query,
                       text='Please re-submit the posting')
        return UPDATE_JOB
    else:
        send_edit_text(query,
                       text='The job is no longer there. Press /start to tsend_plain_textry again')
        return ConversationHandler.END


@logInline
def doneUpdatingJob(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='*EDITED JOB POSTING!*\n' + context.user_data['job'].toPostingString(),
        parse_mode=telegram.ParseMode.MARKDOWN)
    send_plain_text(update, context, DONE_UPDATING_JOB_TEXT)
    ad.updateJob(context.user_data['job'])
    notifyAdmin(text='*A JOB* has been *UPDATED*:\n' + context.user_data['job'].toString(), context=context)
    return ConversationHandler.END


@logInline
def addJob(update, context):
    inputJob = update.message.text_markdown
    if not validateJob(inputJob):
        send_plain_text(update, context, "Your job posting missing certain information please try again")
        return ADD_JOB
    new_job = createJob(inputJob, update.effective_chat.id)
    print('New job created \n' + new_job.toString())
    context.user_data['job'] = new_job

    keyboard = [
        [InlineKeyboardButton("Yes, post this job", callback_data=str('donepostingjob'))],
        [InlineKeyboardButton("No, I want to re-submit a job", callback_data=str('resubmitjob'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id,
                             text='*New Job Posting!*\n' + new_job.toPostingString() + '\nIs this posting correct?',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    return ADD_JOB


@logInline
def donePostingJob(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query, text='*New Job Posting!*\n' + context.user_data['job'].toPostingString())
    send_plain_text(update, context, DONE_POSTING_JOB_TEXT)

    ad.addNewJob(context.user_data['job'])
    notifyAdmin(text='*NEW JOB* has been added:\n' + context.user_data['job'].toString(), context=context)
    return ConversationHandler.END


def generateUniqueId():
    return ''.join(random.sample('0123456789', 6))


def createSeeker(info, chatId) -> Job:
    if Seeker.getTerms()[0] in info:
        terms = Seeker.getTerms()
    else:
        terms = Seeker.getBoldTerms()

    print('Create new job seeker {}'.format(info))

    result = []
    for index in range(0, len(terms) - 1):
        left = terms[index]
        right = terms[index + 1]
        result.append(info[info.index(left) + len(left):info.index(right)])
    # find note:
    result.append(info[info.index(terms[-1]) + len(terms[-1]):])
    user = ad.getUser(chatId)
    # (first_name, full_name, id, is_bot, last_name, name, gender, education_level, occupation, experience, note)
    if len(result) == 6:
        return Seeker(user.first_name, user.full_name, user.id, user.is_bot, user.last_name, result[0],
                      result[1], result[2], result[3], result[4], result[5])
    else:
        print('Something went wrong in added seeker')
        return None


def createJob(inputJob, created_by) -> Job:
    if Job.getTerms()[0] in inputJob:
        terms = Job.getTerms()
    else:
        terms = Job.getBoldTerms()
    id = generateUniqueId()
    print('Create new job id: {}'.format(id))
    #   __init__(self, id, subject, level, location, time, frequency, rate, additional_note):

    result = []
    for index in range(0, len(terms) - 1):
        left = terms[index]
        right = terms[index + 1]
        result.append(inputJob[inputJob.index(left) + len(left):inputJob.index(right)])
    # find note:
    result.append(inputJob[inputJob.index(terms[-1]) + len(terms[-1]):])
    return Job(id, result[0], result[1], result[2], result[3], result[4], result[5], result[6], created_by)


def validateSeeker(info):
    if Seeker.getTerms()[0] in info:
        terms = Seeker.getTerms()
    else:
        terms = Seeker.getBoldTerms()

    for t in terms:
        if t not in info:
            return False
    return True


def validateJob(inputJob):
    if Job.getTerms()[0] in inputJob:
        terms = Job.getTerms()
    else:
        terms = Job.getBoldTerms()

    for t in terms:
        if t not in inputJob:
            return False
    return True


@logInline
@run_async
def jobPosted(update, context):
    chatId = update.effective_chat.id
    query = update.callback_query
    query.answer()

    pendingList = []
    publishList = []
    rejectedList = []
    closedList = []

    for value in ad.getJobDict().values():
        if value.created_by == chatId or ad.isAdmin(chatId):
            if value.stage == Job.stages[0]:
                pendingList.append(value.id)
            elif value.stage == Job.stages[1]:
                publishList.append(value.id)
            elif value.stage == Job.stages[2]:
                rejectedList.append(value.id)
            elif value.stage == Job.stages[3]:
                closedList.append(value.id)

    if len(pendingList) != 0 or len(publishList) != 0 or len(rejectedList) != 0:
        keyboard = []
        for i in pendingList:
            keyboard.append([InlineKeyboardButton('Pending - ' + i, callback_data=str(i))])
        for i in publishList:
            keyboard.append([InlineKeyboardButton('Published - ' + i, callback_data=str(i))])
        for i in rejectedList:
            keyboard.append([InlineKeyboardButton('Rejected - ' + i, callback_data=str(i))])
        keyboard.append([InlineKeyboardButton("Quit", callback_data=str('quit'))])
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text=JOB_POSTED_TEXT.format(
            ','.join(pendingList),
            ','.join(publishList),
            ','.join(rejectedList),
            ','.join(closedList),
        ), reply_markup=reply_markup)
        #   Return Stage to Handle edit
        return CHOOSING_EDIT_CLOSE_JOB
    else:
        send_edit_text(query,
                       text=JOB_POSTED_TEXT.format(
                           ','.join(pendingList),
                           ','.join(publishList),
                           ','.join(rejectedList),
                           ','.join(closedList),
                       ))
        send_plain_text(update, context, JOB_POSTED_EMPTY_TEXT)
        return ConversationHandler.END


@logInline
def quit(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query, QUIT_TEXT)
    return ConversationHandler.END


@logInline
def tutor(update, context):
    query = update.callback_query
    query.answer()
    publishList = []

    for value in ad.getJobDict().values():
        if value.stage == Job.stages[1]:
            publishList.append(value.id)

    if len(publishList) != 0:
        keyboard = []
        for i in publishList:
            keyboard.append([InlineKeyboardButton(str(i), callback_data=str(i))])
        keyboard.append([InlineKeyboardButton("Quit", callback_data=str('quit'))])
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text=TUTOR_TEXT.format(update.effective_user.full_name),
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                reply_markup=reply_markup)
    else:
        send_plain_text(update, context, TUTOR_EMPTY_TEXT.format(update.effective_user.full_name))
        return ConversationHandler.END

    return REGISTERING_JOB


@logInline
def addSeeker(update, context):
    info = update.message.text_markdown
    if not validateSeeker(info):
        send_plain_text(update, context, "Your personal information is missing certain fields please try again")
        return ADD_SEEKER
    new_seeker = createSeeker(info, update.effective_chat.id)
    if new_seeker is None:
        send_plain_text(update, context, "Your personal information is missing certain fields please try again")
        notifyAdmin("Something went wrong in added new job seeker {}".format(info), context)
        return ADD_SEEKER

    context.user_data['jobSeekerInfo'] = new_seeker

    keyboard = [
        [InlineKeyboardButton("Yes, post this info", callback_data=str('donepostinginfo'))],
        [InlineKeyboardButton("No, I want to re-submit the information", callback_data=str('resubmitinfo'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(update.effective_chat.id,
                             text='*Your information*\n\n' + new_seeker.toPostingString() + '\n\nIs this posting correct?',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=reply_markup)
    return ADD_SEEKER


@logInline
def donePostingInfo(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query, DONE_SEEKER_INFO_TEXT)
    ad.addSeeker(context.user_data['jobSeekerInfo'])

    keyboard = [
        [InlineKeyboardButton("Tutor", callback_data=str('tutor'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        DONE_SEEKER_INFO_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    notifyAdmin(text='*New Job Seeker added*:\n' + context.user_data['jobSeekerInfo'].toPostingString(),
                context=context)
    return FIRST


@logInline
def resubmitInfo(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton('Quit', callback_data=str('quit'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    name = update.effective_user.full_name or\
           update.effective_user.name or\
           update.effective_user.first_name or\
           update.effective_user.last_name

    query.edit_message_text(text='Here is the sample\n\n' +
                                 NEW_SEEKER_INFO_TEXT_SAMPLE.format(name) +
                                 '\nPlease submit the information again',
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)
    return ADD_SEEKER


@logInline
def registeringJob(update, context):
    query = update.callback_query
    query.answer()
    selection = query.data
    context.user_data['seekerChoice'] = selection

    chatId = update.effective_user.id

    name = update.effective_user.full_name or \
           update.effective_user.name or \
           update.effective_user.first_name or \
           update.effective_user.last_name

    if not ad.isSeekerRegistered(chatId):
        send_plain_text(update, context, SEEKER_NOT_REGISTERED_TEXT.format(update.effective_user.full_name))
        keyboard = [[InlineKeyboardButton('Quit', callback_data=str('quit'))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(update.effective_chat.id,
                                 text=NEW_SEEKER_INFO_TEXT_SAMPLE.format(name),
                                 parse_mode=telegram.ParseMode.MARKDOWN,
                                 reply_markup=reply_markup)
        return ADD_SEEKER

    if selection not in ad.getJobDict():
        send_edit_text(query,
                       text=JOB_NO_LONGER_THERE)
        return ConversationHandler.END

    curr_job = ad.getJobDict().get(selection)

    if not curr_job.isPublish():
        send_edit_text(query,
                       text=JOB_NO_LONGER_THERE)
        return ConversationHandler.END

    # Check if seeker profile is already there

    seeker = ad.getSeeker(chatId)

    keyboard = [[InlineKeyboardButton('Yes, apply for this job', callback_data=str('submitjobinterest'))],
                [InlineKeyboardButton('No, let me edit my profile', callback_data=str('resubmitinfo'))],
                [InlineKeyboardButton('Quit', callback_data=str('quit'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(REGISTERING_JOB_TEXT.format(curr_job.toPostingString(), seeker.toPostingString()),
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)

    return SUBMIT_JOB_INTEREST


@logInline
@run_async
def submitJobInterest(update, context):
    query = update.callback_query
    query.answer()
    selection = context.user_data['seekerChoice']
    seeker = ad.getSeeker(update.effective_chat.id)
    if selection not in ad.getJobDict():
        send_edit_text(query,
                       text=JOB_NO_LONGER_THERE)
        return ConversationHandler.END

    curr_job = ad.getJob(selection)

    if not curr_job.isPublish():
        send_edit_text(query,
                       text=JOB_NO_LONGER_THERE)
        return ConversationHandler.END

    curr_job.setInterestedUser(seeker)
    # notify job poster
    send_edit_text(query, SEEKER_SUBMIT_INTEREST_TEXT.format(curr_job.toPostingString()))
    context.bot.send_message(curr_job.created_by,
                             text=SEEKER_SUBMIT_INTEREST_POSTER_NOTIFY_TEXT.format(seeker.toPostingString(),
                                                                                   curr_job.toPostingString()),
                             parse_mode=telegram.ParseMode.MARKDOWN)

    return ConversationHandler.END


@logInline
@run_async
def addDev(update, context):
    ad.dev_team.append(update.effective_chat.id)
    ad.saveDevTeam()


@authorize
@logInline
@run_async
def help_me(update, context):
    HELP_TEXT = """--<i>Here is a list of commands</i>--
/canIBeAdmin

/downloadAll

/addAdmin [id]

/help

"""
    context.bot.send_message(update.effective_chat.id, text=HELP_TEXT, parse_mode=telegram.ParseMode.HTML)


# logInlineEmoticon table: https://apps.timwhitlock.info/emoji/tables/unicode
# def keepSending(update, context, job):
#     print("{} :: Last sent - {} at {}".format(datetime.today(), job.groupName, job.lastSent))
#     if (isinstance(job.lastSent, int)
#         or (datetime.today() - job.lastSent).total_seconds() > job.frequency) \
#             and job.msg != '' \
#             and job.frequency != -1:
#         context.bot.send_message(job.chatId, text=job.msg, parse_mode=telegram.ParseMode.MARKDOWN)
#         notifyAdmin(("Just sent to *{}* \n\n" + u'\U0001F4EA' + " Message: \n{}").format(job.groupName, job.msg),
#                     context)
#         job.lastSent = datetime.today()

def notifyAdmin(text, context):
    for dev in ad.dev_team:
        try:
            context.bot.send_message(dev, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        except:
            logger.error('User admin is not found {}'.dev)


@logInline
def error_handler(update, context):
    send_plain_text(update, context, str("Something is missing! Please try again"))
    logger.error(" Error in Telegram Module has Occurred:", exc_info=True)


def send_edit_text(query, text):
    query.edit_message_text(text, parse_mode=telegram.ParseMode.MARKDOWN)


def send_plain_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def send_html_text(update, context, text):
    context.bot.send_message(update.effective_chat.id, text=text, parse_mode=telegram.ParseMode.HTML)


@authorize
@run_async
def download_all(update, context):
    with open("./db/jobData.csv", 'rb') as f:
        context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='jobData.csv')
    with open("./db/seekerData.csv", 'rb') as f:
        context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='seekerData.csv')
    with open("./db/userData.csv", 'rb') as f:
        context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='userData.csv')
    # with open("./db/userData.pickle", 'rb') as f:
    #     context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename='userData.pickle')

@authorize
@run_async
def canIBeAdmin(update, context):
    user = ad.getUser(update.effective_user.id)
    notifyAdmin(user.toString() + " want to admin", context)

@authorize
@run_async
def addAdmin(update, context):
    newAdminId = context.args[0]
    ad.addDevTeam(newAdminId)
    send_plain_text(update, context,"Added Dev: {}".format(ad.getUser(newAdminId)))


@run_async
def hi(update, context):
    print("new channel added bot {}".format(update.effective_chat.id))
    notifyAdmin("Channel {} added bot".format(update.effective_chat.id), context)


def main():
    # ad.startAdmin()
    updater = Updater(config['telegram']['token_dev'], use_context=True)
    dp = updater.dispatcher

    ad.loadDataOnStartup()

    # Second State is New Job, Posted Job,

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_args=True),
                      CommandHandler('start_admin', start_admin)],
        states={
            FIRST: [CallbackQueryHandler(postingJob, pattern='^poster$'),
                    CallbackQueryHandler(quit, pattern='^quit$'),
                    CallbackQueryHandler(tutor, pattern='^tutor$')],
            POSTING: [CallbackQueryHandler(newJob, pattern='^newjob$'),
                      CallbackQueryHandler(quit, pattern='^quit$'),
                      CallbackQueryHandler(jobPosted, pattern='^jobposted$')],
            ADD_JOB: [MessageHandler(Filters.text, addJob),
                      CallbackQueryHandler(newJob, pattern='^resubmitjob$'),
                      CallbackQueryHandler(quit, pattern='^quit$'),
                      CallbackQueryHandler(donePostingJob, pattern='^donepostingjob$')],
            CHOOSING_EDIT_CLOSE_JOB: [CallbackQueryHandler(chosingEditOrClose),
                                      CallbackQueryHandler(quit, pattern='^quit$')],
            UPDATE_STAGE: [CallbackQueryHandler(editPosting, pattern='^editposting$'),
                           CallbackQueryHandler(publishPosting, pattern='^publishposting$'),
                           CallbackQueryHandler(rejectPosting, pattern='^rejectposting$'),
                           CallbackQueryHandler(quit, pattern='^quit$'),
                           CallbackQueryHandler(interestedList, pattern='^interestedlist$'),
                           CallbackQueryHandler(closePosting, pattern='^closeposting$')],
            UPDATE_JOB: [MessageHandler(Filters.text, updateJob),
                         CallbackQueryHandler(reSubmitEditJob, pattern='^reeditjob$'),
                         CallbackQueryHandler(quit, pattern='^quit$'),
                         CallbackQueryHandler(doneUpdatingJob, pattern='^doneupdatingjob$')],
            REJECTION_REASON: [MessageHandler(Filters.text, rejectionReason)],
            REGISTERING_JOB: [CallbackQueryHandler(registeringJob)],
            CHOOSING_SEEKER: [CallbackQueryHandler(choosingSeeker),
                              CallbackQueryHandler(quit, pattern='^quit$')],
            ADD_SEEKER: [MessageHandler(Filters.text, addSeeker),
                         CallbackQueryHandler(resubmitInfo, pattern='^resubmitinfo$'),
                         CallbackQueryHandler(donePostingInfo, pattern='^donepostinginfo$'),
                         CallbackQueryHandler(quit, pattern='^quit$')],
            SUBMIT_JOB_INTEREST: [CallbackQueryHandler(submitJobInterest, pattern='^submitjobinterest$'),
                                  CallbackQueryHandler(resubmitInfo, pattern='^resubmitinfo'),
                                  CallbackQueryHandler(quit, pattern='^quit$')],
            NOTIFY_DECISION: [CallbackQueryHandler(accept, pattern='^accept$'),
                              CallbackQueryHandler(reject, pattern='^reject$'),
                              CallbackQueryHandler(quit, pattern='^quit$')]
            #        CallbackQueryHandler(abandon, pattern='ABANDON*')],
            # END: [CallbackQueryHandler(end)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    admin_commands = [
        ['canIBeAdmin', canIBeAdmin],
        ['downloadAll', download_all],
        ['addAdmin', addAdmin],
        ["help", help_me],
        ["hi", hi],
    ]
    #
    for command, function in admin_commands:
        updater.dispatcher.add_handler(CommandHandler(command, function))

    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, unknown))

    dp.add_error_handler(error_handler)
    updater.start_polling(poll_interval=1.0, timeout=20)
    updater.idle()


if __name__ == '__main__':
    logger.info("Starting Bot")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Terminated using Ctrl + C")
    ad.saveDataOnShutDown()
    logger.info("Exiting Bot")
    sys.exit()
