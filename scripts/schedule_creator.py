"""
Create a schedule on a dizqueTV channel.
Complete the SCHEDULE below with time slot entries.
All programs used in schedule must already be added to your channel.

Entry example:
'2130': {
    'type': 'movie',
    'title': ['The Grinch', 'Halloween'],
    'order': 'shuffle'
}

Time is HH:MM in 24-hour time

Each entry must have a 'type' of either 'movie' or 'show'

'title' can be empty, a single show/movie title or a list of show/movie titles.
If no title is provided, a random show/movie will be selected to fill that time slot
If multiple titles are provided, one of the listed titles will be selected randomly to fill that time slot

'order' can be 'shuffle', 'next' or missing. 'shuffle' used by default behind-the-scenes
"""
from typing import List, Union
import argparse

from dizqueTV import API, make_time_slot_from_dizque_program
from dizqueTV.channels import Channel
import dizqueTV.helpers as helpers


# COMPLETE THESE SETTINGS
DIZQUETV_URL = "http://localhost:8000"
CHANNEL_NUMBER = 1

SCHEDULE = {  # use 24-hour time
    "00:00": {
        'type': 'show',
        'title': ['The Simpsons', 'Family Guy'],
        'order': 'shuffle'
    },
    "00:30": {
        'type': 'movie',
        'title': ['The Grinch', 'Halloween']
    },
    "03:30": {
        'type': 'movie',
    }
}


# DO NOT TOUCH BELOW

def get_items_of_type(item_type: str, program_list):
    return [item for item in program_list if
            (helpers._object_has_attribute(object=item, attribute_name='type') and item.type == item_type)]


def get_non(item_type: str, program_list):
    return [item for item in program_list if
            (helpers._object_has_attribute(object=item, attribute_name='type') and item.type != item_type)]


def get_random_item_of_type(media_type: str, program_list):
    filtered_program_list = get_items_of_type(item_type=media_type, program_list=program_list)
    if not filtered_program_list:
        return None
    return helpers.random_choice(items=filtered_program_list)


def get_show_episodes(show_title: str, program_list):
    episodes = []
    for program in program_list:
        if program.showTitle == show_title:
            episodes.append(program)
    return episodes


def get_program(program_name, program_list):
    for program in program_list:
        if program.showTitle == program_name:
            return program
    return None


def create_time_slots(channel: Channel):
    channel_programs = channel.programs
    time_slots = []
    for start_time, data in SCHEDULE.items():
        program = None
        if not data.get('type'):
            raise Exception("Must include 'type' in each schedule entry.")
        if data['type'] == 'show':
            if data.get('title'):
                titles = data['title']
                if not type(data['title']) == List:
                    titles = [titles]
                shows = []
                for show_title in titles:
                    episodes = get_show_episodes(show_title=show_title, program_list=channel_programs)
                    if episodes:
                        shows.append(episodes)
                if not shows:
                    print(f"Could not get any episodes to select for {start_time}.")
                else:
                    selected_show_episodes = helpers.random_choice(items=shows)
                    print(f"Getting random episode of {selected_show_episodes[0].showTitle}...")
                    program = helpers.random_choice(items=selected_show_episodes)
            else:
                print("Getting random episode of a random show...")
                program = get_random_item_of_type(media_type='episode', program_list=channel_programs)
        elif data['type'] == 'movie':
            if data.get('title'):
                program = get_program(program_name=data['title'], program_list=channel_programs)
            else:
                print("Getting random movie...")
                program = get_random_item_of_type(media_type='movie', program_list=channel_programs)
        else:
            raise Exception("Type is not 'show' or 'movie'.")
        if not program:
            print(f"Could not get a program to schedule for {start_time}.")
        else:
            print(f"Scheduling {program.showTitle} for {start_time}...")
            time_slots.append(
                make_time_slot_from_dizque_program(program=program,
                                                   time=start_time,
                                                   order=data.get('order', 'shuffle')))
    return time_slots


dtv = API(url=DIZQUETV_URL)
channel = dtv.get_channel(channel_number=CHANNEL_NUMBER)
if not channel:
    raise Exception(f"Could not find channel #{CHANNEL_NUMBER}")

if channel.schedule:
    channel.delete_schedule()
time_slots = create_time_slots(channel=channel)
if channel.add_schedule(time_slots=time_slots):
    print(f"Created schedule for {channel.name}.")
else:
    print(f"Could not create schedule for {channel.name}.")
