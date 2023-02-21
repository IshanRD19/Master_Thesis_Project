import os
import engine
import pandas as pd
from io import StringIO
from tabulate import tabulate
from datetime import datetime

DIVIDER_LENGTH = 80


def welcome(submissions_path):
    print('-' * DIVIDER_LENGTH)
    print('  >>>>> Welcome to Command Line Interface (CLI) for Plagiarism Detection <<<<<  ')
    print('-' * DIVIDER_LENGTH)
    print('Select an option to proceed:')
    print(f'1) Select directory from {submissions_path}')
    print('2) Provide custom path of directory')
    print('0) Exit')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = input()
        
        if user_choice in ['0', '1', '2']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, or 2 given above.')

    return user_choice


def get_filenames_from_path(path):
    filenames = os.listdir(path)
    return filenames
    

def select_submission_directory(submissions_path):
    filenames = get_filenames_from_path(submissions_path)
    file_count = len(filenames)
    
    print('-' * DIVIDER_LENGTH)
    print(f'Found {file_count} directories in the chosen path {submissions_path}')
    print('Select a submission directory for plagiarism detection:')
    print('0) Go back')
    for i in range(file_count):
        print(f'{i+1}) {filenames[i]}')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = int(input())
        
        if not user_choice: return user_choice
        elif 0 < user_choice <= file_count: break
        else: print('Incorrect choice!\nKindly select from the options 0, to {filecount} given above.')

    return filenames[user_choice - 1], submissions_path + filenames[user_choice - 1] + '\\'


def take_custom_path():
    print('-' * DIVIDER_LENGTH)
    print('Enter 0 to go back')
    print('Enter custom path of directory:', end=' ')
    custom_path = input()
    print(f'Custom Path: {custom_path}')
    return


## find only folders/files as filenames


def exit():
    print('-' * DIVIDER_LENGTH)
    print('Thank you for using our Plagiarism Detection Interface!')
    print('Share your valuable feedback on ishaniit23@gmail.com')
    print('-' * DIVIDER_LENGTH)
    return


def select_specific_file(submission_directory_path):
    filenames = get_filenames_from_path(submission_directory_path)
    file_count = len(filenames)
    
    print('-' * DIVIDER_LENGTH)
    print(f'Found {file_count} files in the selected path {submission_directory_path}')
    print('Select a file for plagiarism detection:')
    print('0) Go back')
    for i in range(file_count):
        print(f'{i+1}) {filenames[i]}')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = int(input())
        
        if not user_choice: return user_choice
        elif 0 < user_choice <= file_count: break
        else: print('Incorrect choice!\nKindly select from the options 0, to {filecount} given above.')

    return filenames[user_choice - 1]


def select_initial_action(submission_directory_path):
    filenames = get_filenames_from_path(submission_directory_path)
    file_count = len(filenames)

    print('-' * DIVIDER_LENGTH)
    print('>>>>> Select your desired task <<<<<')
    print('-' * DIVIDER_LENGTH)
    print(f'{file_count} files are present in {submission_directory_path}')
    print('Select an option to proceed:')
    print('0) Go back')
    print('1) Generate plagiarism report for all files')
    print('2) Generate plagiarism report for a specific file')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = input()

        if user_choice in ['0', '1', '2']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, or 2 given above.')

    return user_choice


def display_insights(insights, is_file_specific=False):
    print('Here are some insights on Plagiarism for an overview:')
    print(f"Maximum Plagiarism: {insights['max']}%")
    print(f"Minimum Plagiarism: {insights['min']}%")
    print(f"Mean: {insights['mean']}%")
    print(f"Standard Deviation: {insights['std']}")
    
    if is_file_specific:
        print(f"Originality Score: {insights['originality_score']}")

    return


def display_group_insights(group_insights):
    print('-' * DIVIDER_LENGTH)
    print('A few insights about the groups of plagiarised submissions:')
    print(f"Total Groups: {group_insights['total']}")
    print(f"Average Submissions per Group: {group_insights['avg']}")
    print(f"Groups with 2 or more Submissions: {group_insights['ge_2']}")
    print(f"Groups with 5 or more Submissions: {group_insights['ge_5']}")
    print(f"Groups with 10 or more Submissions: {group_insights['ge_10']}")
    print(f"Maximum Group Size: {group_insights['max']}")
    return


def select_ensuing_action(submission_directory_path):
    print('-' * DIVIDER_LENGTH)
    print('>>>>> Select a follow-up task <<<<<')
    print('-' * DIVIDER_LENGTH)
    print('Select an option to proceed:')
    print('0) Go back')
    print('1) Export the above plagiarism report')
    print('2) Export a comprehensive list of logs')
    print('3) Identify groups of plagiarised submissions')

    while True:
        print('Enter your choice:', end=' ') 
        user_choice = input()

        if user_choice in ['0', '1', '2', '3']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, 2, or 3 given above.')

    return user_choice


def select_group_action():
    print('-' * DIVIDER_LENGTH)
    print('>>>>> Select a follow-up task <<<<<')
    print('-' * DIVIDER_LENGTH)
    print('Select an option to proceed:')
    print('0) Go back')
    print('1) Export the above plagiarism report having grouped submissions')
    print('2) Extract group-level information')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = input()

        if user_choice in ['0', '1', '2']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, or 2 given above.')

    return user_choice


def export_report(results_path, report, filename):
    '''
    To export the data requested by the User
    '''
    # Ensure the desired directory exists
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    new_filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    report.to_csv(f'{results_path}\\{new_filename}', index=False)
    print(f'Successfully exported the file {new_filename} to {results_path}')

    return


def display_report(report):
    df = pd.read_table(StringIO(report.to_string(index=False)), sep="\s+", header=0)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    return


def select_file_follow_up():
    print('-' * DIVIDER_LENGTH)
    print('>>>>> Select a concluding task <<<<<')
    print('-' * DIVIDER_LENGTH)
    print('Select an option to proceed:')
    print('0) Go back')
    print('1) Export the above file report')
    print('2) Go to Home Page')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = input()

        if user_choice in ['0', '1', '2']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, or 2 given above.')

    return user_choice


def select_final_action():
    print('-' * DIVIDER_LENGTH)
    print('>>>>> Select a concluding task <<<<<')
    print('-' * DIVIDER_LENGTH)
    print('Select an option to proceed:')
    print('0) Go back')
    print('1) Export the above group information')
    print('2) Go to Home Page')

    while True:
        print('Enter your choice:', end=' ')
        user_choice = input()

        if user_choice in ['0', '1', '2']: break
        else: print('Incorrect choice!\nKindly select from the options 0, 1, or 2 given above.')

    return user_choice


def user_commands():
    flow = 'welcome'
    current_path = os.getcwd()
    submissions_path = current_path + '\\submissions\\'

    while flow:

        # Home Screen
        if flow == 'welcome':
            welcome_choice = welcome(submissions_path)
            if welcome_choice == '1': flow = 'select_directory'
            elif welcome_choice == '2': flow = 2.2
            elif welcome_choice == '0': break

        # Select a submission directory from default path
        elif flow == 'select_directory':
            chosen_directory, submission_directory_path = select_submission_directory(submissions_path)
            results_path = current_path + '\\results\\' + chosen_directory
            if submission_directory_path == 0: flow = 'welcome'
            else: flow = 'select_initial_action'

        # Select an action to proceed submission directory from default path
        elif flow == 'select_initial_action':
            initial_action_choice = select_initial_action(submission_directory_path)
            if initial_action_choice == '0': flow = 'select_directory'
            elif initial_action_choice == '1': flow = 'generate_batch_report'
            elif initial_action_choice == '2': flow = 'select_file'

        elif flow == 'generate_batch_report':
            print('-' * DIVIDER_LENGTH)
            plagiarism_logs, batch_report, insights = engine.trigger_moss(submission_directory_path)
            display_report(batch_report)
            display_insights(insights) 
            flow = 'select_ensuing_action'

        elif flow == 'select_file':
            specific_file_path = select_specific_file(submission_directory_path)
            if specific_file_path == 0: flow = 'select_directory'
            else: flow = 'generate_file_report'

        elif flow == 'generate_file_report':
            plagiarism_logs, file_report, insights = engine.trigger_moss(submission_directory_path, specific_file=specific_file_path)
            display_report(file_report)
            display_insights(insights, True)
            flow = 'file_report_follow_up'

        elif flow == 'select_ensuing_action':
            ensuing_action_choice = select_ensuing_action(submission_directory_path)
            if ensuing_action_choice == '0': flow = 'select_directory'
            elif ensuing_action_choice == '1': flow = 'export_plag_report'
            elif ensuing_action_choice == '2': flow = 'export_plag_logs'
            elif ensuing_action_choice == '3': flow = 'identify_groups'

        elif flow == 'export_plag_report':
            export_report(results_path, batch_report, 'batch_report')
            flow = 'select_ensuing_action'

        elif flow == 'export_plag_logs':
            export_report(results_path, plagiarism_logs, 'exhaustive_logs')
            flow = 'select_ensuing_action'

        # Receive a custom path
        elif flow == 'identify_groups':
            group_logs, group_insights = engine.diagnose_clusters(batch_report)
            display_report(group_logs)
            display_group_insights(group_insights)
            flow = 'group_follow_up'

        elif flow == 'group_follow_up':
            group_action_choice = select_group_action()
            if group_action_choice == '0': flow = 'select_directory'
            elif group_action_choice == '1': flow = 'export_group_logs'
            elif group_action_choice == '2': flow = 'generate_group_report'

        elif flow == 'export_group_logs':
            export_report(results_path, group_logs, 'group_logs')
            flow = 'group_follow_up'

        elif flow == 'generate_group_report':
            group_report = engine.generate_group_report(group_logs)
            display_report(group_report)
            flow = 'final_follow_up'

        elif flow == 'final_follow_up':
            final_choice = select_final_action()
            if final_choice == '0': flow = 'group_follow_up'
            elif final_choice == '1': flow = 'export_group_report'
            elif final_choice == '2': flow = 'welcome'

        elif flow == 'export_group_report':
            export_report(results_path, group_report, 'group_report')
            flow = 'final_follow_up'

        elif flow == 'batch_report_follow_up':
            flow = 'welcome'

        elif flow == 'file_report_follow_up':
            flow = 'welcome'

    exit()

    return
