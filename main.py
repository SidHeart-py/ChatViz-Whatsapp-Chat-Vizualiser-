import PySimpleGUI as sg
import pandas as pd
import re
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
import logging
import time
from functools import wraps
from wordcloud import WordCloud, STOPWORDS


def logger(a_function):
    @wraps(a_function)
    def wrapper(*args, **kwargs):
        logging.basicConfig(filename='chat_viz.log', level=logging.INFO)
        t1 = time.time()
        x = a_function(*args, **kwargs)
        t1 = time.time() - t1
        logging.info(f'{a_function.__name__,} takes {t1} to execute')
        return x

    return wrapper


@logger
def create_dataset():
    """
    Create a pandas dataset with the help of given chats.
    The dataset will be a global variable.

    :return:
        True or False, says weather the database created successfully or not.
    """
    global message_df
    file = open(values['-File Name-'], 'r', encoding='utf').read()

    # Matching Patterns of Whatsapp chats
    first_date = r'\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s\w\w'
    number_lookahead = r'(?::)|(?:\sjoined)|(?:Messages)|(?:\screated)|(?:\schanged)|(?:\sadded)|(?:\sremoved)|(?:\sleft)|(?:Your)'
    pattern = f'({first_date})\s-\s(.*?(?={number_lookahead})):?\s?(.*?)(?=(?:\n{first_date})|(?:$))'
    match = re.findall(pattern, file, re.DOTALL)

    if match:
        # Making Data Frames
        message_df = pd.DataFrame(match, columns=['date_time', 'contact', 'message'])

        # Cleaning data
        message_df.drop(message_df[message_df.contact == ''].index, axis=0, inplace=True)
        message_df.drop(message_df[message_df.contact == 'You'].index, axis=0, inplace=True)
        message_df['date_time'] = pd.to_datetime(message_df.date_time, format=r'%d/%m/%y, %I:%M %p')
        # print('Shape of the dataset is', message_df.shape)
        # print(message_df.dtypes)
        # print(message_df.head(10))
        return True
    else:
        return False


@logger
def month_viz():
    """
    Creates a bar graph of month and no of chats.
    Shows results on interactive matplotlib window.
    """
    sns.countplot(x=message_df.date_time.dt.month_name())
    plt.xticks(rotation=90)
    plt.title('Message in Months')
    plt.xlabel('Month')
    plt.ylabel('message count')
    plt.show()


@logger
def day_viz():
    """
    Creates a bar graph of days(Sun, Mon .....) and no of chats on those days.
    Shows results on interactive matplotlib window.
    """
    sns.countplot(x=message_df.date_time.dt.weekday)
    plt.xticks(ticks=np.arange(7), labels=['Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'])
    plt.title('Message count every Day')
    plt.xlabel('Day of Weeks')
    plt.ylabel('Message count')
    plt.show()


@logger
def year_viz():
    """
    Creates a bar graph of year and no of chats.
    Shows results on interactive matplotlib window.
    """
    sns.countplot(x=message_df['date_time'].dt.year)
    plt.title('Message count per Year')
    plt.xlabel('Year')
    plt.ylabel('Message count')
    plt.show()


@logger
def hour_viz():
    """
    Creates a bar graph of hour(24 hours) and no of chats.
    Shows results on interactive matplotlib window.
    """
    sns.countplot(x=message_df.date_time.dt.hour)
    plt.title('Message count every Hour in a day')
    plt.xlabel('Hours')
    plt.ylabel('Message count')
    plt.show()


@logger
def timeline():
    """
    Plot a line graph to your whole timeline of chats.
    Shows results on interactive matplotlib window.
    """

    # Making relevant dataset
    message_timeline = pd.DataFrame({'date': message_df.date_time.dt.date, 'contact': message_df.contact})
    message_timeline = message_timeline.groupby(['date'])

    # Plotting
    sns.lineplot(x=message_timeline.count().index, y=message_timeline.count().contact)
    plt.xticks(rotation=90)
    plt.title('Your full chat timeline')
    plt.xlabel('Date')
    plt.ylabel('Message Count')
    plt.show()


@logger
def word_cloud():
    """
    Plot a wordcloud of your frequent words directly proportional to size.
    Shows results on interactive matplotlib window.
    """

    stopwords = STOPWORDS.union({'Media', 'omitted'})

    # instantiate a word cloud object
    message_wc = WordCloud(
        background_color='white',
        max_words=2000,
        stopwords=stopwords
    )

    # generate the word cloud
    message_wc.generate(' '.join(message_df['message']))

    # display the word cloud
    plt.imshow(message_wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()


@logger
def total_message_by_person():
    """
    Make a window with list of all members of chat and their number of messages.
    """
    message_count = pd.crosstab(index=message_df['contact'], columns='No of messages') \
        .sort_values('No of messages', ascending=False)
    sg.Print(message_count, no_titlebar=True)


@logger
def avg_reply_time():
    """
    Return the average reply time of a person.
    This function is only woks in individual chats, not in group chats.

    :warning:-
        Formula for this operation is not based on some standards, it's just for fun purpose.
    """
    no_of_peoples = len(message_df['contact'].unique())
    if no_of_peoples == 2:
        time_calc = list(zip(message_df['date_time'], message_df['contact']))
        reply_time = {i: [] for i in message_df['contact'].unique()}
        for i in range(1, len(time_calc)):
            if time_calc[i][1] != time_calc[i - 1][1]:
                reply_time[time_calc[i][1]].append(time_calc[i][0] - time_calc[i - 1][0])
        sg.Print('\nWARNING: This is just a rough estimate for fun.', no_titlebar=True)
        sg.Print('Don\'t make any decision based on it.\n\n')
        for i in reply_time:
            sg.Print(f'Avg reply time of {i} is {stats.trim_mean(reply_time[i], 0.1)}')
    else:
        sg.popup_error("Can't use when number of people not equal to two")


# Some essential default variables
valid_file = False
message_df = None
sg.theme('LightGreen3')
pd.set_option('display.max_rows', None)

options = [
    [
        sg.Frame('Message per Year', [[sg.Button('Year', key='-Year Viz-')]]),
        sg.Frame('Message per Month', [[sg.Button('Month', key='-Month Viz-')]])
    ],
    [
        sg.Frame('Message per Day', [[sg.Button('Day', key='-Day Viz-')]]),
        sg.Frame('Message per Hour', [[sg.Button('Hour', key='-Hour Viz-')]])
    ]
]

browse_file = [
    [
        sg.In(),
        sg.FileBrowse(key='-File Name-')
    ],
    [
        sg.OK(),
        sg.Cancel()
    ]
]

misc_layout = [
    [
        sg.Button('Full timeline', key='-Timeline-'),
        sg.Button('Word Cloud', key='-WORD CLOUD-')
    ]
]

basic_statistics = [
    [
        sg.Button('Avg. Reply Time', key='-AVG REPLY TIME-'),
        sg.Button('Total Message by Person', key='-TOTAL MESSAGE BY PERSON-')
    ]
]

layout = [
    [sg.Text('Welcome to Chat Viz', font=('Franklin Gothic Book', 14, 'bold'))],
    [
        sg.HSeparator()
    ],
    [
        sg.Frame('Browse file Here', browse_file, key='-FILE BROWSE-')
    ],
    [
        sg.Frame('Visualize on basis of Time', options, element_justification='center',
                 visible=False, key='-TIME SECTION-')
    ],
    [
        sg.Frame('Basic Stats', basic_statistics, element_justification='center',
                 visible=False, key='-BASIC STATS-')
    ],
    [
        sg.Frame('Some Misc', layout=misc_layout,
                 element_justification='center', visible=False, key='-TIMELINE SECTION-')
    ]
]

window = sg.Window('Chat Viz', layout, grab_anywhere=True, element_justification='c')

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'OK':
        if values['-File Name-']:
            valid_file = create_dataset()
            if valid_file:
                window['-TIME SECTION-'].update(visible=True)
                window['-TIMELINE SECTION-'].update(visible=True)
                window['-BASIC STATS-'].update(visible=True)
            else:
                sg.popup_error('Invalid whatsapp file')
        else:
            sg.popup_error('Choose a file', no_titlebar=True)

    if event == '-Month Viz-':
        if valid_file:
            month_viz()
        else:
            sg.popup_error('file read error')

    if event == '-Day Viz-':
        if valid_file:
            day_viz()
        else:
            sg.popup_error('file read error')

    if event == '-Year Viz-':
        if valid_file:
            year_viz()
        else:
            sg.popup_error('file read error')

    if event == '-Hour Viz-':
        if valid_file:
            hour_viz()
        else:
            sg.popup_error('file read error')

    if event == '-Timeline-':
        if valid_file:
            timeline()
        else:
            sg.popup_error('file read error')

    if event == '-WORD CLOUD-':
        if valid_file:
            word_cloud()
        else:
            sg.popup_error('file read error')

    if event == '-TOTAL MESSAGE BY PERSON-':
        if valid_file:
            total_message_by_person()
        else:
            sg.popup_error('file read error')
    if event == '-AVG REPLY TIME-':
        if valid_file:
            avg_reply_time()
        else:
            sg.popup_error('file read error')

window.close()
