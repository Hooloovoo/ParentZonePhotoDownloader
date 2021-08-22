#!/usr/bin/env python3
import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import requests

import click


@click.command()
@click.option('--email', help='Email address used to log in to ParentZone',
              prompt='Email address used to log in to ParentZone')
@click.option('--password', help='Password used to log in to ParentZone',
              prompt='Password used to log in to ParentZone')
@click.option('--output_folder', help='Output folder',
              default='./output')
def get_parentzone_photos(email, password, output_folder):
    """Downloads all photos from a ParentZone account"""
    driver = webdriver.Chrome()

    driver.get("https://www.parentzone.me/")
    driver.implicitly_wait(10)

    # Fill in email and password
    email_field = driver.find_element_by_xpath('//*[@id="email"]')
    email_field.clear()
    email_field.send_keys(email)

    passwd_field = driver.find_element_by_xpath('//*[@id="password"]')
    passwd_field.clear()
    passwd_field.send_keys(password)
    time.sleep(2)
    # passwd_field.send_keys(Keys.RETURN)  # This isn't working for me, so click manually for now
    login_button = driver.find_element_by_xpath("//button[@data-test-id='login_btn']")
    login_button.click()
    
    # Go to timeline
    driver.get('https://www.parentzone.me/#/timeline')

    # Open the filter dropdown
    filter_button = driver.find_element_by_xpath("//button[@data-test-id='toggle_filter_button_wrapper']")
    filter_button.click()

    # Choose "Observation" and "Moment", which are the two that have pictures
    observation_filter_button = driver.find_element_by_xpath("//div[@data-test-id='tag_Observation']")
    observation_filter_button.click()
    moment_filter_button = driver.find_element_by_xpath("//div[@data-test-id='tag_Moment']")
    moment_filter_button.click()

    # Close filter pane
    filter_button.click()

    # The page has infinite scrolling, and scrolling by the JS scroll function
    # doesn't seem to work
    # So instead, set up a loop to scroll infinitely, and stop when we
    # stop getting any more photos displaying
    html = driver.find_element_by_tag_name('html')
    old_n_photos = 0
    while True:
        # Scroll
        html.send_keys(Keys.END)
        time.sleep(3)
        # Get all photos
        media_elements = driver.find_elements_by_class_name('img-responsive')
        n_photos = len(media_elements)

        if n_photos > old_n_photos:
            old_n_photos = n_photos
        else:
            break

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # For each image that we've found
    for element in media_elements:
        image_url = element.get_attribute('src')
        image_id = image_url.split("&d=")[-1]

        # Deal with file extension based on tag used to display the media
        if element.tag_name == 'img':
            extension = 'jpg'
        elif element.tag_name == 'video':
            extension = 'mp4'
        image_output_path = os.path.join(output_folder,
                                         f'{image_id}.{extension}')

        # Only download and save the file if it doesn't already exist
        if not os.path.exists(image_output_path):
            r = requests.get(image_url, allow_redirects=True)
            open(image_output_path, 'wb').write(r.content)


if __name__ == '__main__':
    get_parentzone_photos()
