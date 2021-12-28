# import Libraries
import requests
import os
import smtplib
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

youtube_trending_url = 'https://www.youtube.com/feed/trending' #'https://www.youtube.com/feed/trending'

def request_web(url):
  response = requests.get(url)
  
  with open('trending1.html','w') as f:
    f.write(response.text)
  print('Html Page Saved successfully')
  return response


def get_driver():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=chrome_options)
  return driver

def get_videos(driver):
  print('Fetching the Page...')
  driver.get(youtube_trending_url)
  driver.implicitly_wait(10) # seconds

  print('Returning the Page info...')
  print(driver.title)
 
  for i in range(33):
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
    driver.implicitly_wait(10) # seconds

  ytd_videos = driver.find_elements(by= By.TAG_NAME,value='ytd-video-renderer')
 
  print(f'Found {len(ytd_videos)} videos')

  return ytd_videos

def scrape_data(video):
  title = video.find_element(By.TAG_NAME ,'h3').text
  # print(title)
  url = video.find_element(By.TAG_NAME ,'h3').find_element(By.TAG_NAME, 'a').get_attribute('href')
 
  # attrs=[]
  thumbnail = video.find_element(By.ID, 'thumbnail')
  # for attr in thumbnail.get_property('attributes'):
  #   attrs.append([attr['name'], attr['value']])
  # print(attrs)
  thumbnail_url = thumbnail.find_element(By.ID ,'img').get_attribute('src')
  # print(thumbnail_url)

  video_time = thumbnail.find_element(By.ID, 'text').text

  channel_name = video.find_element(By.ID ,'text-container').text
  # print(channel_name)

  metadata = video.find_element(By.ID ,'metadata-line').find_elements(By.TAG_NAME,'span')
  # print(metadata[0].text)
  # print(metadata[1].text)

  desc = video.find_element(By.ID ,'description-text').text
  # print(desc)
  return {
    'title': title, 
    'url_link': url,
    'thumbnail': thumbnail_url, 
    'Play_Time' : video_time,
    'Channel' : channel_name, 
    'Views' : metadata[0].text, 
    'Upload': metadata[1].text, 
    'Desc': desc
  }



def send_mail(text):
  sender = os.environ['gmail_username']
  reciever = [os.environ['gmail_username']]
  
  gmail_password = os.environ['gmail_password']
  
  try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    print('Logging In to Email...')
    server.login(sender, gmail_password)
    print('Successfully logged In') 

    sent_from = sender
    to = reciever
    subject = 'Report From Youtube Trend'
    body = f"Hey, what's up?\nThis is a report about the daily trending videos on youtube.\n\n{text}"

    email_text = """
    From: %s
    To: %s
    Subject: %s

    %s""" %(sent_from, "; ".join(to), subject, body)
    print('Sending Email...')
    server.sendmail(sent_from, to, email_text)
    server.close()
    print('Email Sent Successfully')
  except Exception as err:
    print('Something went wrong...' , err)
  




def table_data():
  print('Creating Driver...')
  driver = get_driver()
  videos = get_videos(driver)
  video_list = []
  #title, url, thumbnail_url, channel, views, uploaded, description
  for video in videos:
    video_list.append(scrape_data(video))
    # print(scrape_data(video))
  video_df = pd.DataFrame(video_list)
  print(video_df.head())
  print()
  print('Saving to CSV...')
  video_df.to_csv('trending_video.csv',index=False)
  text = json.dumps(video_list, indent=4)

  return text




if __name__ == '__main__':
  # request_web(youtube_trending_url)
  body = table_data()
  send_mail(body)
  
  
    
  