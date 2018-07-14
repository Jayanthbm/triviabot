from base64 import b64encode
import io, os, urllib.request, urllib.parse, urllib.error, requests, re, webbrowser, json
from os import makedirs
from os.path import join, basename
from sys import argv
from PIL import Image
import PIL.ImageGrab
import re
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

api_key = " " # Google Vision API Key

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
""" Screen Shot of the Screen with Question and Options """
def take_screenshot():
	img_name = PIL.ImageGrab.grab(bbox=(30,334,288,542)) 
	img_name.save("screen.png")

""" Spliting Screen into Question and Options """
def split_screen_to_question_and_options(): 
    i = Image.open('screen.png')
    width, height = i.size
    frame = i.crop(((0,0,width,65))) #cropping the question
    frame.save('question.png')
    frame = i.crop(((0,65,width,110))) 
    frame.save('1.png')
    frame = i.crop(((0,110,width,160)))
    frame.save('2.png')
    frame = i.crop(((0,160,width,200)))
    frame.save('3.png')
	
def print_question_block(question,question_block):

	""" 
		Prints the q to the terminal

	"""

	#webbrowser.open('http://google.com/search?q=' +question)  #uncomment this if you need webbrowser to be opened
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
	count= 64
	for (i,r) in enumerate(results):
		text = "%s - %s" % (r["ans"], r["count"])
		
		count=count+1

		if r["ans"] == large["ans"]:
			k=r["ans"]+"("+str(r["count"])+")"
			print(colors.green + text + colors.end)
		elif r["ans"] == small["ans"]:
			p=r["ans"]+"("+str(r["count"])+")"
			print(colors.red + text + colors.end)
		else:
			print(text)

	print("\n")
	res=[]
	for r in results :
		
		res.append(r["count"])
	res=str(res)
	if 'not' in question:
		res= "Choose:" + "<b>" + p + "</b>" + "<pre>" + res + "</pre>"
	else:
		res= "Choose:" + "<b>" + k + "</b>" + "<pre>" + res + "</pre>"

	""" Sends the result via telegram """	
	#t="https://api.telegram.org/botyour telegram bot api key /sendMessage?chat_id=Your telegram group id &text="+res + "&parse_mode=html"
	#response= requests.get(t)


if __name__ == '__main__':        
        #take_screenshot()
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