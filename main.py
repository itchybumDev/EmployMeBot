import configparser
import logging
import random
import sys
from datetime import datetime

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext.dispatcher import run_async

import admin as ad
from const import *
from model.Job import Job
from model.User import User
from logging_handler import logInline


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

FIRST, POSTING, THREE, FOUR, FIVE, END, ADD_JOB, CHOOSING_EDIT_CLOSE_JOB, UPDATE_JOB, UPDATE_CLOSE_JOB= range(10)


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
    send_plain_text(update, context, "Sorry, I didn't understand that command.\nRun /help to see available options")


@logInline
@run_async
def start(update, context):
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
@run_async
def postingJob(update, context):
    print('Posting Job')
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("New Job", callback_data=str('newjob'))],
        [InlineKeyboardButton("Job Posted", callback_data=str('jobposted'))],
        [InlineKeyboardButton("Quit", callback_data=str('quit'))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(POSTING_JOB_TEXT,reply_markup=reply_markup)
    return POSTING


@logInline
@run_async
def newJob(update, context):
    print('newJob')
    query = update.callback_query
    query.answer()
    send_edit_text(query,text=NEW_JOB_TEXT)
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
    print('editJob')
    query = update.callback_query
    selection = query.data
    query.answer()
    if selection in ad.getJobDict():
        send_edit_text(query,
            text=EDIT_JOB_TEXT_1)
        send_plain_text(update, context, ad.getJobDict().get(selection).toPostingString())
        # send_plain_text(update,context, EDIT_JOB_TEXT_2)
        keyboard = [[InlineKeyboardButton('Edit Posting', callback_data=str('editposting')),
                     InlineKeyboardButton('Close Posting', callback_data=str('closeposting'))],
                    [InlineKeyboardButton("Quit", callback_data=str('quit'))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(update.effective_chat.id,
                                 text='What do you want to do?',
                                 parse_mode=telegram.ParseMode.MARKDOWN,
                                 reply_markup=reply_markup)
        context.user_data['editJob'] = selection
        return UPDATE_CLOSE_JOB
    else:
        send_edit_text(query,
            text='The job is no longer there. Press /start to try again')
        return ConversationHandler.END

@logInline
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
    send_edit_text(query,text=CLOSE_JOB_TEXT.format(ad.getJobDict()[context.user_data['editJob']].toPostingString()))
    return ConversationHandler.END


@logInline
def updateJob(update, context):
    print('updateJob')
    inputJob = update.message.text_markdown
    if not validateJob(inputJob):
        send_plain_text(update, context, "Your job posting missing certain information please try again")
        return UPDATE_JOB
    new_job = createJob(inputJob, update.effective_chat.id)
    print('UPDATE JOB - New job created \n' + new_job.toString())
    old_job = ad.getJobDict()[context.user_data['editJob']]
    new_job.setId(old_job.id, old_job.created_on)

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
    print('reSubmitEditJob')
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
    print('doneUpdatingJob')
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='*EDITED JOB POSTING!*\n' + context.user_data['job'].toPostingString(),
        parse_mode=telegram.ParseMode.MARKDOWN)
    send_plain_text(update, context, DONE_UPDATING_JOB_TEXT)
    ad.updateJob(context.user_data['job'])
    return ConversationHandler.END

@logInline
def addJob(update, context):
    print('addJob')
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
    print('donePostingJob')
    query = update.callback_query
    query.answer()
    send_edit_text(query, text='*New Job Posting!*\n' + context.user_data['job'].toPostingString())
    send_plain_text(update, context, DONE_POSTING_JOB_TEXT)

    ad.addNewJob(context.user_data['job'])
    return ConversationHandler.END

def generateUniqueId():
    return ''.join(random.sample('0123456789', 6))

def createJob(inputJob, created_by) -> Job:
    terms = ['Subject :', 'Level :', 'Location :', 'Time :', 'Frequency :', 'Rate :', 'Additional Note :']
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

def validateJob(inputJob):
    terms = ['Subject :', 'Level :', 'Location :', 'Time :', 'Frequency :', 'Rate :', 'Additional Note :']
    for t in terms:
        if t not in inputJob:
            return False
    return True


@logInline
@run_async
def jobPosted(update, context):
    print('jobPosted')
    chatId = update.effective_chat.id
    query = update.callback_query
    query.answer()

    pendingList = []
    publishList = []
    rejectedList = []
    closedList = []

    for value in ad.getJobDict().values():
        if value.created_by == chatId:
            if value.stage == Job.stages[0]:
                pendingList.append(value.id)
            elif value.stage == Job.stages[1]:
                publishList.append(value.id)
            elif value.stage == Job.stages[2]:
                rejectedList.append(value.id)
            elif value.stage == Job.stages[3]:
                closedList.append(value.id)

    if len(pendingList) != 0:
        keyboard = []
        for i in pendingList:
            keyboard.append([InlineKeyboardButton('Pending - ' + i, callback_data=str(i))])
        for i in publishList:
            keyboard.append([InlineKeyboardButton('Published - ' + i, callback_data=str(i))])
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
        return ConversationHandler.END

@logInline
def quit(update, context):
    query = update.callback_query
    query.answer()
    send_edit_text(query, QUIT_TEXT)
    return ConversationHandler.END

@logInline
def tutor(update, context):
    print('Tutor')
    query = update.callback_query
    query.answer()
    send_edit_text(query,text='Tutor')
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

/hi
Register the group after added bot to group

/activate
Start sending after the bot reset

/show
Show all Groups that the bot is active

/update [chatId] [frequency in seconds] [message]
Update the message sending to the group
*b -- *bBold*b
*i -- *iItalic*i
*n -- newline

/delete [chatId]
Delete the group from the bot

/iamadmin
Add admin
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
        context.bot.send_message(dev, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

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


def main():
    # ad.startAdmin()
    updater = Updater(config['telegram']['token_dev'], use_context=True)
    dp = updater.dispatcher

    ad.loadDataOnStartup()

    # Second State is New Job, Posted Job,
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(postingJob, pattern='^' + str('poster') + '$'),
                    CallbackQueryHandler(quit, pattern='^' + str('quit') + '$'),
                    CallbackQueryHandler(tutor, pattern='^' + str('tutor') + '$')],
            POSTING: [CallbackQueryHandler(newJob, pattern='^' + str('newjob') + '$'),
                      CallbackQueryHandler(quit, pattern='^' + str('quit') + '$'),
                     CallbackQueryHandler(jobPosted, pattern='^' + str('jobposted') + '$')],
            ADD_JOB: [MessageHandler(Filters.text, addJob),
                      CallbackQueryHandler(newJob, pattern='^resubmitjob$'),
                      CallbackQueryHandler(quit, pattern='^' + str('quit') + '$'),
                      CallbackQueryHandler(donePostingJob, pattern='^donepostingjob$')],
            CHOOSING_EDIT_CLOSE_JOB: [CallbackQueryHandler(chosingEditOrClose),
                                      CallbackQueryHandler(quit, pattern='^' + str('quit') + '$')],
            UPDATE_CLOSE_JOB: [CallbackQueryHandler(editPosting, pattern='^editposting$'),
                               CallbackQueryHandler(quit, pattern='^' + str('quit') + '$'),
                               CallbackQueryHandler(closePosting, pattern='^closeposting$')],
            UPDATE_JOB: [MessageHandler(Filters.text, updateJob),
                         CallbackQueryHandler(reSubmitEditJob, pattern='^reeditjob$'),
                         CallbackQueryHandler(quit, pattern='^' + str('quit') + '$'),
                         CallbackQueryHandler(doneUpdatingJob, pattern='^doneupdatingjob$')]
            # FOUR: [CallbackQueryHandler(choose_one_job)],
            # FIVE: [CallbackQueryHandler(done, pattern='DONE*'),
            #        CallbackQueryHandler(abandon, pattern='ABANDON*')],
            # END: [CallbackQueryHandler(end)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    admin_commands = [
        ["help", help_me],
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
    logger.info("Exiting Bot")
    sys.exit()
