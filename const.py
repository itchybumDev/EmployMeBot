START_TEXT = """
*Hello {}*, 
Welcome to your personal Job Assitant Bot!

I am Emily and I am here to assist you.

Before we start, please join our Telegram channel @sgTuitions if you are not yet a member!

Important Notice: If you do not have a Telegram Username and have disabled forwarded messages to contain your Telegram contact in your Privacy Settings, Job Posters or Tutors will not be able to contact you on Telegram. We advise you to create a Telegram username before proceeding further steps!

"""

POSTING_JOB_TEXT = """
Posting job is fast and simple!

Please do not share private information / specific location for your assignment as they will be posted on the public channel.

Press 'New Job' below to begin posting a new assignment!
"""

NEW_JOB_TEXT = """
Please send me your posting in the format below, by insert in those places

Subject : [Insert subject]
Level : [Insert level]
Location : [Insert location]
Time : [Insert time]
Frequency : [Insert frequency]
Rate : [Insert rate]
Additional Note : [Insert note]

For Example:
"""

NEW_JOB_TEXT_SAMPLE = """
*Subject* : [H2 Chemistry]
*Level* : [JC2]
*Location* : [Bukit Timah Hill]
*Time* : [Monday, Tuesday, Friday]
*Frequency* : [Twice a week]
*Rate* : [$100]
*Additional Note* : [N/A]
"""

DONE_UPDATING_JOB_TEXT = """
*WOOHOO! Your job posting has been UPDATED successfully!*

What will happen next:

Once approved by the Administrators, your job request will be published on @sgTuitions.

Sit tight and be patient! Once any tutor applies for your job, his/her profile will be sent to you by me (the bot) directly.

Shortlisting of Tutors: By default, you can only shortlist a total of 5 tutors to access their Telegram contacts. We recommend that you should only shortlist tutors whom you are keen to discuss further details with them directly.

If you wish to start a new assignment posting for another subject, press /start anytime!

Thank you for using our platform to broadcast your assignment! :)
"""

DONE_POSTING_JOB_TEXT = """
*WOOHOO! Your job posting has been recorded successfully!*

What will happen next:

Once approved by the Administrators, your job request will be published on @sgTuitions.

Sit tight and be patient! Once any tutor applies for your job, his/her profile will be sent to you by me (the bot) directly.

Shortlisting of Tutors: By default, you can only shortlist a total of 5 tutors to access their Telegram contacts. We recommend that you should only shortlist tutors whom you are keen to discuss further details with them directly.

If you wish to start a new assignment posting for another subject, press /start anytime!

Thank you for using our platform to broadcast your assignment! :)
"""

JOB_POSTED_TEXT = """
Assignments Dashboard

Pending Approval
{}

Published Assignments
{}

Rejected Assignments
{}

Closed Assignments
{}

Select each assignment below to view more details, edit assignment fields, shortlist your tutors, or close the job!

Assignments will automatically expire and close after 3 days to prevent flooding of jobs on the channel and tutors' application panel.
"""

EDIT_JOB_TEXT_1 = """
You posted the job:
"""

EDIT_JOB_TEXT_2 = """
Please re-submit the job with edited values.
"""

UPDATE_JOB_TEXT ="""
Congratulations! Here is your new posting:
{}

Please wait for admin to review the changes
"""

CLOSE_JOB_TEXT = """
You have *closed* the job:
{}

If you wish to start a new assignment posting for another subject, press /start anytime!
"""

PUBLISH_JOB_TEXT = """
You have *PUBLISHED* the job:
{}

If you wish to start a new assignment posting for another subject, press /start anytime!
"""


PUBLISH_JOB_POSTER_TEXT = """
*Congratuations*, your job posting:
{}

Have been *APPROVED* by admin, you will now see the posting in channel

If you wish to start a new assignment posting for another subject, press /start anytime!
"""

REJECT_JOB_TEXT = """
You have *REJECTED* the job:
{}

Please type in the reason and job poster will be notified to make changes.
"""

REJECT_JOB_POSTER_TEXT = """
{}

has been *REJECTED* by the admin. Here is the reason:

_{}_

Please edit the post again for approval, press /start again!
"""


QUIT_TEXT = """
Thanks for using me

If you wish to start a new assignment posting for another subject, press /start anytime!
"""

JOB_POSTED_EMPTY_TEXT = """
All jobs are ready, you do not have pending"""

TUTOR_TEXT = """
*Hey {}*!

I am Emily and I will help you find a job!

Please do not share any private information 
specific location with me as your profile will be sent directly to the job posters (parents, students, agents).

At the current moment, here are the list of tuition jobs that are still OPENED.
Please select the Assignment Code you want to apply to:
"""

TUTOR_EMPTY_TEXT = """
*Hey {}*!

I am Emily and I will help you find a job!

There is currently no job at the moment.

Please try /start again later.
"""

SEEKER_NOT_REGISTERED_TEXT = """
*Hey {}*!

Seems like you have no profile yet. Let make you one!

Please send me your information by replacing those insert places:
*Name* : [Insert name]
*Gender* : [Insert Male/Female]
*Education Level* : [Insert High School/ Bachelor/ Master/ PhD]
*Occupation* : [Insert Engineer/ Doctor/ etc]
*Experience* : [Insert graduate/ 2 yrs/ etc]
*Additional Note* : [Insert N/A]

For example, something like this:

"""

NEW_SEEKER_INFO_TEXT_SAMPLE = """
*Name* : [Emily]
*Gender* : [Female]
*Education Level* : [AI Bot]
*Occupation* : [Personal Assistant]
*Experience* : [2 yrs]
*Additional Note* : [I am not really a real person]
"""

DONE_SEEKER_INFO_TEXT = """
Congratulations! You got a profile!
Now you can feel free to browse jobs
"""

REGISTERING_JOB_TEXT = """
You have chosen job:

{}

Would you like to apply with your current profile?

{} 
"""

SEEKER_SUBMIT_INTEREST_TEXT = """
*Well done*!

You have submitted your interest in the job
{}

Please wait for the owner to contact you

"""

SEEKER_SUBMIT_INTEREST_POSTER_NOTIFY_TEXT = """
{}

has expressed interest in your posting:

{}

Please view your posted jobs to give the hiring decision
"""

CHOOSING_SEEKER_TEXT = """
Application from 

{}

What do you want to do?
"""

ACCEPT_TEXT = """
Congratulations on finding the person for the job.
Your posting is now moved to Closed and will not be able to modify further
We will notify him/her
Please proceed to contact him/her to arrange for a call as well
"""
ACCEPT_NOTIFICATION_TEXT = """
You application for

{}

has been *ACCEPTED*'.

Please wait for the job poster to contact you
"""

REJECT_TEXT = """
We will notify him/her about your decision

Dont give up!
Lets keep looking.
"""

REJECT_NOTIFICATION_TEXT = """
You application for

{}

has been *REJECTED*
Dont give up!
Lets keep looking.
"""