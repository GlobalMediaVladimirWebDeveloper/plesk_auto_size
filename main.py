
import os
import sys
from time import sleep
import re 
from datetime import datetime


from WorkingWithFiles.converting_tables import convertTableToDictionary
from WorkingWithFiles.write_to_spreadsheet import WriteToSpredSheet
from WorkingWithBrowser.browser import Browser

########################### Constants ###########################
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
SOURCES_PATH = f"{ROOT_PATH}/Sources"
SYSTEM32_FILES = f"{SOURCES_PATH}/system32"
ACCESS_FILE_PATH = f"{SOURCES_PATH}/Access"
OUTPUT_PATH = f"{SOURCES_PATH}/output"
LIST_OF_ACCESS_INIT = convertTableToDictionary(ACCESS_FILE_PATH, "auto_size.xlsx")

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

WRITE_TO_SPREAD_SHEET = WriteToSpredSheet(OUTPUT_PATH, f"plesk_hosting_statistics_{current_time}.xlsx")

ROW = 2

COL = 1

LIST_OF_ACCESS = LIST_OF_ACCESS_INIT.get_list_of_accesses()

FIREFOX_BINARY = f"{SYSTEM32_FILES}/firefox/firefox"
GECKODRIVER_BINNARY = f"{SYSTEM32_FILES}/geckodriver-src/geckodriver"
PAGE_LOADING_DELAY = 20
SLEEP_DELAY = 5

PART_OF_PANEL_LINK_FOR_ALL_SITES = "smb/web/view/"
PART_OF_PANEL_LINK_FOR_STATISTICS = "smb/statistics/details/"

SEARCHABLE_FILE_FOR_DATABASE_NAME = "config"



global FALSE_BACKUP_DICT
FALSE_BACKUP_DICT = {}

global ERROR_COUNTER
ERROR_COUNTER = 0

COUNT_OF_ALL_SITES = len(LIST_OF_ACCESS.items())

########################### Constants ###########################


print(LIST_OF_ACCESS)


########################### Inits ###########################

try:
	browser = Browser(FIREFOX_BINARY, GECKODRIVER_BINNARY,PAGE_LOADING_DELAY,SLEEP_DELAY)
except Exception as e:
	os.system("pkill firefox-bin")
	os.system("pkill geckodriver")
	browser = Browser(FIREFOX_BINARY, GECKODRIVER_BINNARY,PAGE_LOADING_DELAY,SLEEP_DELAY)


########################### Inits ###########################


def login_into_hosting_panel(browser: 'Browser with Selenium instances', path: 'link to login page', login: 'username for sing in', password: 'password for sign in'):
	print('\n\tLog in to hosting panel')

	browser.go_to_and_wait_until(path, 'id', 'loginSection')
	login_input = browser.find_element('id','login_name')
	if not login_input:
		return False
	password_input = browser.find_element('id','passwd')
	submit_btn = browser.find_element('class_name', 'pul-button.pul-button--lg.pul-button--primary.pul-button--fill')
	browser.type_to_element(login_input, login)
	browser.type_to_element(password_input, password)
	browser.click_on_element(submit_btn)
	is_loggin = browser.find_element_and_wait_until(15,'id', 'buttonAddDomain', None)
	if is_loggin: return True

	return False



def get_full_statistics(browser: 'Browser with Selenium instances', path: str, part_link_for_statistics: 'part link to default path for viewin all sites', site_url) -> 'Returning list of database names':
	print('\n\tGetting all statistics')

	browser.go_to_and_wait_until(f"{path}{part_link_for_statistics}", 'id', 'main')
	sleep(4)
	try:
		taskbar = browser.find_element('id', 'asyncProgressBar')
		if taskbar:
			delbtns = browser.find_elements_from(taskbar,'class_name','pul-button.pul-button--ghost.pul-button--empty.pul-button--on-dark.pul-toast__close')
			[browser.click_on_element(deltask) for deltask in delbtns]
			sleep(2)
	except Exception:
		pass
	
	full_statistics = list()
	full_statistics.append(site_url)
	try:
		################################# DISK SPACE SIZE #################################

		drive_size_statistics_root = browser.find_element('class_name', 'line-chart-data-table')
		get_block_of_drive_size_statistics = browser.find_elements_from(drive_size_statistics_root, 'tag_name', 'tr')

		list_of_all_drive_size_statistics = [drive_size_statistics_block.text.strip() for drive_size_statistics_block  in get_block_of_drive_size_statistics]
		disk_space_size = list_of_all_drive_size_statistics[0]
		disk_free_space_size = list_of_all_drive_size_statistics[-1].split(')')[-1]
		disk_space_used_size = list_of_all_drive_size_statistics[-1].split(')')[0] + ')	'
		[full_statistics.append(statistic) for statistic in [disk_space_size, disk_free_space_size,disk_space_used_size]]

		################################# DISK SPACE SIZE #################################

		############################# DISK DETAIL STATISTICS ##############################

		detail_drive_statistics_root = browser.find_element('class_name', 'chart-legend')
		all_details_drive_statistics = browser.find_elements_from(detail_drive_statistics_root, 'tag_name', 'li')
		[full_statistics.append(detail_statistic.text.strip().replace('\n','|').replace('\t', '')) for detail_statistic  in all_details_drive_statistics]

		############################# DISK DETAIL STATISTICS ##############################

		return full_statistics
	except Exception:
		print(f"cannot get site statistics {path}")

	return False

def write_data(site_url: str, data: dict):

	pass

def logout(browser, path):
	print('\n\tlogout \n\n\n')

	try:
		browser.go_to(f"{path}logout.php")
	except Exception as e:
		print('CANNOT LOG OUT\n\t', e)
	return True



def log_error_on_function_output(error_str, site_url):
	global FALSE_BACKUP_DICT
	global ERROR_COUNTER
	FALSE_BACKUP_DICT[site_url] = error_str
	ERROR_COUNTER += 1
	
	return FALSE_BACKUP_DICT

def write_statistic(data: list, ROW: int, COL: int):
	WRITE_TO_SPREAD_SHEET.write_to_spredsheet(data, ROW,COL)
	ROW += 1
	return ROW

for num,site in enumerate(LIST_OF_ACCESS.items(),1):
	try:
		login_path = site[1]['login_path']

		login_username = site[1]['login_name']
		login_password = site[1]['login_password']
		site_url = site[0]
		INTERMIDIATE_PATH_TO_SITE_FOLDER = ""
		print("ENROLED NOW ==> \n\t",login_path,login_username,login_password,site_url)
		print(f"\n\tSite number #{num} <==> from {COUNT_OF_ALL_SITES}")
		print(f"\n\tError counter is = {ERROR_COUNTER}")
		logout(browser,login_path)
		sleep(2)
		try:
			with open('error.txt', "w") as file:
				file.write(str(FALSE_BACKUP_DICT))
		except Exception as e:
			print("WRTIE\t",e)

		is_signed_in = login_into_hosting_panel(browser, login_path, login_username, login_password)
		if not is_signed_in:
			write_statistic([site_url, "не удалось войти","не удалось войти","не удалось войти","не удалось войти","не удалось войти"], ROW, COL)
			ROW += 1
			log_error_on_function_output(f"Cannot to login into {site_url}",site_url)
			continue
		all_statistics = get_full_statistics(browser, login_path, PART_OF_PANEL_LINK_FOR_STATISTICS,site_url)
		if not all_statistics:
			log_error_on_function_output("Cannot get full statistics", site_url)
			continue

		write_statistic(all_statistics, ROW, COL)
		ROW += 1

	except Exception as e:
		print(e)
		continue
	
print(FALSE_BACKUP_DICT)

os.system("pkill firefox-bin")
os.system("pkill geckodriver")


