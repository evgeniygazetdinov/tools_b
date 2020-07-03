from collections import OrderedDict
import time
import datetime
import pytz
import requests
from lib.backend_methods import remove_uploadlist




def find_empty_uploadlist(content):
    null_lists = []
    lists = content['upload_list']
    for lis in lists:
        if len(lis['photos']) == 0:
            null_lists.append(lis['date_upload'])
    return null_lists


def clean_empty_uploadlists(username,password,content):
    null_uploadlists = find_empty_uploadlist(content)
    if len(null_uploadlists) != 0 :
        for null_list in null_uploadlists:
            remove_uploadlist(username,password,null_list)



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



def remove_photos(urls,username,password):
    print('this my urls')
    print(urls)
    
    for url in urls:
        response=requests.get(url, auth=(username, password))
        print(response.content) if response.status_code == 201 or response.status_code == 200 else print(response.status_code)

def remove_from_list(login,password,viewed_photo):
    start_time = time.time()
    remove_photos(viewed_photo,login,password)
    duration = time.time() - start_time
    print(viewed_photo)
    print(f"REMOVE {len(viewed_photo)} messages in {duration} seconds")


    








def find_viewed_photos(content):
    res = {}
    lists = content['upload_list']
    without_lists = content['photos_without_upload_list']
    for li in lists:
        for photo in li['photos']:
            if len(photo['views']) !=0:
                res[photo['unique_short_link']] = {'views':photo['views'],'delete_link':photo['delete_by_unique_link']}
    for lis in without_lists:
        if len(lis['views']) != 0:
           res[lis['unique_short_link']] = {'views':lis['views'],'delete_link':lis['delete_by_unique_link']}

    return res

def extract_delete_links(links):
    delete_links = []
    print(links)
    for key,value in links.items():
        delete_links.append(value['delete_link'])
    return delete_links

def delete_viewed_photos(login, password, content):
    links = find_viewed_photos(content)
    for_delete = extract_delete_links(links)
    remove_from_list(login, password, for_delete)
    return links

