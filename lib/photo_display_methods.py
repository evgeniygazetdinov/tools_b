from collections import OrderedDict
from time import time
import aiohttp
import asynci
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


def  remove_from_list(viewed_photo):
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(remove_messages(links))
    duration = time.time() - start_time



def delete_viewed_photos(photos):
    pass


