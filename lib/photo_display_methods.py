from collections import OrderedDict
from time import time
import datetime
import pytz
import aiohttp
import asyncio
from lib.history import remove_messages

def extract_lists_from_response(lists):
    res = OrderedDict()
    for lis in lists:
        for key,value in lis.items():
            res[lis['date_upload']] = [photo['unique_short_link'] for photo in lis['photos']]
    return res
    
def make_fake_list_based_on_photos(photos_without_list):
    res = OrderedDict()
    for photo in photos_without_list:
        res[photo['created_date']]=photo['unique_short_link']
    return res




def get_uploaded_photos_from_response(response):
    uploads=OrderedDict()
    if response['photos_without_upload_list']:
       fake_lists = make_fake_list_based_on_photos(response['photos_without_upload_list'])
       uploads.update(fake_lists)
    if response['upload_list']:
        true_list = extract_lists_from_response(response['upload_list'])
        uploads.update(true_list)
    return uploads

def from_string_to_datetimes(uploads_lists):
    times_list = []
    for times in uploads_lists.keys():
        times_list.append(datetime.datetime.strptime(times,"%Y-%m-%d %H:%M"))
    return times_list



def find_most_new_list(uploads_lists):
    now = datetime.datetime.now()
    youngest = max(dt for dt in uploads_lists if dt < now)
    return youngest.strftime("%Y-%m-%d %H:%M")
   

        
def get_newest_upload_list(response):
    uploads_lists = get_uploaded_photos_from_response(response)
    datetimes_list = from_string_to_datetimes(uploads_lists)
    newest_date = find_most_new_list(datetimes_list)
    if newest_date in uploads_lists:
        return {newest_date:uploads_lists[newest_date]}
    else :
        return None


def remove_from_list(viewed_photo):
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(remove_messages(viewed_photo))
    duration = time.time() - start_time


def find_viewed_photos(content):
    res = []
    lists = content['upload_list']
    without_lists = content['photos_without_upload_list']
    for li in lists:
        for photo in li['photos']:
            if len(photo['views']) !=0:
                res.append(photo['delete_by_unique_link'])
    for lis in without_lists:
        if len(lis['views']) != 0:
            res.append(photo['delete_by_unique_link'])
    return res


def delete_viewed_photos(content):
    links = find_viewed_photos(content)
    #remove_from_list(links)
    print(links)


