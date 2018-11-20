from base64 import b64encode
from os import makedirs
from os.path import join, basename
from sys import argv
import json
import requests
import os
from PIL import Image
import PIL.ImageGrab
import re
import io, os, urllib.request, urllib.parse, urllib.error, requests, re, webbrowser, json

from termcolor import colored
import termcolor
import colorama
colorama.init()

# import Bsoup
from bs4 import BeautifulSoup
class colors:
    blue = '\033[94m'
    red   = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'
CLOUD_VISION_ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'

from googleapiclient.discovery import build
import pprint

api_key = "Enter API KEY"  #Add your API Key

def google(q_list, num):

	"""
		given a list of queries, this function Google's them as a concatenated string.
		
	"""

	params = {"q":" ".join(q_list), "num":num}
	url_params = urllib.parse.urlencode(params)
	google_url = "https://www.google.com/search?" + url_params
	r = requests.get(google_url)

	soup = BeautifulSoup(r.text,"html.parser")
	spans = soup.find_all('span', {'class' : 'st'})

	text = " ".join([span.get_text() for span in spans]).lower().strip()

	return text
	
	
def rank_answers(question,answers):

	"""
		Ranks answers based on how many times they show up in google's top 50 results. 
		
		If the word " not " is in the question is reverses them. 
		If theres a tie breaker it google the questions with the answers

	"""


	print("rankings answers...")
	
	question = question
	ans_1 = answers[0]
	ans_2 = answers[1]
	ans_3 = answers[2]

	reverse = True

	if " not " in question.lower():
		print("reversing results...")
		reverse = False

	text = google([question], 50)

	results = []

	results.append({"ans": ans_1, "count": text.count(ans_1)})
	results.append({"ans": ans_2, "count": text.count(ans_2)})
	results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results = []

	sorted_results.append({"ans": ans_1, "count": text.count(ans_1)})
	sorted_results.append({"ans": ans_2, "count": text.count(ans_2)})
	sorted_results.append({"ans": ans_3, "count": text.count(ans_3)})

	sorted_results.sort(key=lambda x: x["count"], reverse=reverse)

	# if there's a tie redo with answers in q

	if (sorted_results[0]["count"] == sorted_results[1]["count"]):
		# build url, get html
		print("running tiebreaker...")

		text = google([question, ans_1, ans_2, ans_3], 50)

		results = []

		results.append({"ans": ans_1, "count": text.count(ans_1)})
		results.append({"ans": ans_2, "count": text.count(ans_2)})
		results.append({"ans": ans_3, "count": text.count(ans_3)})

	return results

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
            })
    return img_requests

def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()

def request_ocr(api_key, image_filenames):
    response = requests.post(CLOUD_VISION_ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def get_text_from_response(response):
    t = response['textAnnotations'][0]
    return (t['description'])

def take_screenshot():
	img_name = PIL.ImageGrab.grab(bbox=(27,297,288,545)) #Co-ordinates for the screenshot
	img_name.save("screen.png")

def split_screen_to_question_and_options():
    i = Image.open('screen.png')
    width, height = i.size
    frame = i.crop(((0,18,width,105))) # cropping the image for the question
    frame.save('question.png')
    frame = i.crop(((0,105,width,160))) # cropping the for the first option
    frame.save('1.png')
    frame = i.crop(((0,155,width,210))) # cropping the for the second option
    frame.save('2.png')
    frame = i.crop(((0,205,width,260))) # cropping the for the third option
    frame.save('3.png')
	
def print_question_block(question,question_block):

	""" 
		Prints the q to the terminal

	"""
	"Uncomment this if you want to open the webbrowser "	
	#webbrowser.open('http://google.com/search?q=' +question) 
	print("\n")

	if " not " in question.lower():
		print (colors.red +"Negative  Question"+ colors.end)
	if  " never " in question.lower():
		print (colors.red +"Negative  Question"+ colors.end)
	print("Q: ", colors.blue +question + colors.end)
	print("1: ", question_block[0])
	print("2: ", question_block[1])
	print("3: ", question_block[2])
	print("\n")

def print_results(results):

	""" 
		Prints the results

	"""

	print("\n")

	small = min(results, key= lambda x: x["count"])
	large = max(results, key= lambda x: x["count"])

	for (i,r) in enumerate(results):
		text = "%s - %s" % (r["ans"], r["count"])

		

		if r["ans"] == large["ans"]:
			print(colors.green + text + colors.end)
		elif r["ans"] == small["ans"]:
			print(colors.red + text + colors.end)
		else:
			print(text)

	print("\n")



if __name__ == '__main__':        
        take_screenshot()
        split_screen_to_question_and_options()
        image_filenames = ['question.png','1.png','2.png','3.png']
        response = request_ocr(api_key, image_filenames)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            responses = (response.json()['responses'])
            question = get_text_from_response(responses[0])
            question = question.replace('\n',' ')
            options = [get_text_from_response(responses[1]),get_text_from_response(responses[2]),get_text_from_response(responses[3])]
            for idx,option in enumerate(options):
                options[idx] = option.strip(' \t\n\r').lower()
            print_question_block(question,options)
            results = rank_answers(question,options)
			
            print_results(results)