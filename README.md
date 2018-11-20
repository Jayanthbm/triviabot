# Trivia_Bot 🤖
A bot to help answer questions on trivia apps like Loco and Brainbaazi.
This bot takes screenshot of the game on the phone and uses Google Vision API to read the questions and options.
It automates the process of googling of the answers and gives the most likely answer!
and the probable answer is displayed
**It is not 100% accurate....**




Since it is against the policy of Loco-trivia i do not encourage anyone to use this during a live game and this is purely for educational purposes.


## Packages Used

Use python 3.6. In particular the packages/libraries used are...

- JSON - Data Storage
- Pillow - Image manipulation
- beautifulsoup4 - Parse google searches/html


To easily install these
1. Install python 3.6
2. Install above packages
     -  $ pip3 install -r requirements.txt
     

 ## Usage
 
 1. First mirror the screen to pc. 
 2. Set the co-ordinates for the questions and options
 3.  Run the script
 
 ###Screen Mirroring
 
 For Screen Mirroring Use any of the below Softwares
 
 1. ApowerMirror - https://www.apowersoft.com/phone-mirror
 2. Vysor -http://vysor.io/
 
 ###Setting Corodrinates
 
 -Edit line no 145 to set coridnates for the screenshot 
 -Edit line no 151 to crop the image for question
 -Edit line no 153 to crop the image for option 1
 -Edit line no 155 to crop the image for option 2
 -Edit line no 157 to crop the image for option 3
 
 ###Run the Script
 
 python3 bot.py
