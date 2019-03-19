import requests
import time
import json
import numpy
import datetime
import math
from random import randint
from dateutil import rrule

### IMPORTANT VARIABLES AND CONSTANTS ###
group_id = '34883130'
access_token = '7bC53ZymUUULq74uIlnYHJ3WExGkGJMevOXGitY3'
bot_id = '66937b801033770130013711b2'
#bot_id = '08a9497a271a70057028cd3b55'
todays_people = None
current_week = None
choreMapping = numpy.zeros((3,7), int)
member_array = [30437530, 30693108, 32706950, 30107026, 31580930, 31628754, 28709877, 19049601]
member_dict = {30437530: 'Alec Maier', 30693108: 'Ben Janesch', 32706950: 'Benjamin Janish', 30107026: 'Stephen Gant', 31580930: 'Wenjing Deng', 31628754: 'Derek Potts', 28709877: 'Mhomas 👵', 19049601: 'Justin Clark'}
request_params = {'token': access_token}
intro_string = '!!! Daily Whore Reminder !!!\n'
dishwasher_string = '\nDishwasher: @'
countertop_string = '\nClean Countertops: @'
stovetop_string = '\nClean Stovetop: @'
ending_string = '\n\nThis has been your daily whore reminder.'

request_url = 'https://api.groupme.com/v3/groups/' + group_id
homies_group_info = requests.get(request_url, params = request_params).json()
response = int(homies_group_info['meta']['code'])
# sets nicknames to most recent set
if(response < 400):
    the_homies = homies_group_info['response']['members']
    for homie in the_homies:
        member_dict[int(homie['user_id'])] = homie['nickname']

# request for bot test group, remove once migrated
#group = requests.get('https://api.groupme.com/v3/groups/48409659', params = request_params).json()
    
# reads the current Week from the JSON file and maps it to the numpy array
def createWeekMapping():
    whole_week = current_week.read().split("\n")
    for i in range(len(whole_week)):
        whole_week[i] = whole_week[i].split()
        for j in range(len(whole_week[i])):
            choreMapping[i][j] = int(whole_week[i][j])

def chooseClosingLine():
    chore_lines = open('chore_lines.txt', 'r+')
    all_lines = chore_lines.read().split('\n')
    line = all_lines[22]
    chore_lines.close()
    return '\n\n\"' + line + '\"'

# starts a new chore week by shifting everybody to the left
def shiftWeek():
    firstWeekStart = datetime.date(2019, 2, 18)
    today = datetime.date.today()
    weekDiff = int(math.floor((today - firstWeekStart).days / 7))
    for _ in range(weekDiff):
        for j in range(choreMapping.shape[0]):
            for k in range(choreMapping.shape[1]):
                id = choreMapping[j][k]
                mem_index = member_array.index(id)
                if mem_index < 7:
                    choreMapping[j][k] = member_array[mem_index + 1]
                else:
                    choreMapping[j][k] = member_array[0]

# accesses nicknames from todays people and returns the message for the bot to post. Chore strings are defined at the top of the file
def constructChoreMessage(todays_people, member_dict):
    return intro_string + dishwasher_string + member_dict.get(todays_people[0]) + countertop_string \
     + member_dict.get(todays_people[1]) + stovetop_string + member_dict.get(todays_people[2]) + ending_string

# calculates the correct loci based on the length of todays nicknames and the length of the chore strings
def constructMentionsObject(todays_people):
    mention_index1 = len(intro_string) + len(dishwasher_string)
    mention_index2 = mention_index1 + len(member_dict.get(todays_people[0])) + len(countertop_string)
    mention_index3 = mention_index2 + len(member_dict.get(todays_people[1])) + len(stovetop_string)
    firstLoci = [mention_index1 - 1, len(member_dict.get(todays_people[0])) + 1]
    secondLoci = [mention_index2 - 1, len(member_dict.get(todays_people[1])) + 1]
    thirdLoci = [mention_index3 - 1, len(member_dict.get(todays_people[2])) + 1]
    return {'loci': [firstLoci, secondLoci, thirdLoci], 'type': 'mentions', 'user_ids': [str(todays_people[0]), \
     str(todays_people[1]), str(todays_people[2])]}

# open the current week information
current_week = open('current_week.txt', 'r+')

# map it to the numpy array
createWeekMapping()

day_of_week = datetime.datetime.today().weekday() # get the current weekday

# shift the chore mapping based on the number of weeks elapsed
shiftWeek()

# close file stream
current_week.close()

# get the chore people for today
todays_people = choreMapping[:,day_of_week]

# pick a random quote for the end of the message
ending_string = chooseClosingLine()

# construct message
chore_message = constructChoreMessage(todays_people, member_dict)

# get mentions attachment object for request
mentions = constructMentionsObject(todays_people)

# construct request
post_params = { "bot_id" : bot_id, "text": chore_message, "attachments": [mentions] }

# make the request
request = requests.post('https://api.groupme.com/v3/bots/post', data=json.dumps(post_params))