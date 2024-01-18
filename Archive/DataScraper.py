import requests
from bs4 import BeautifulSoup
from langdetect import detect
from datetime import datetime
from transformers import MarianMTModel, MarianTokenizer
import csv
import time
import re


page_num = 1
Run = True
discussion_urls = []
discussion_titles = []
discussion_replies = []
discussion_ops = []
discussion_contents = []

master_links = ["https://steamcommunity.com/app/521890/discussions/1/","https://steamcommunity.com/app/1321680/discussions/1/","https://steamcommunity.com/app/242760/discussions/1/","https://steamcommunity.com/app/739630/discussions/2/"]
names = ["Hello Neighbor", "Hello Neighbor 2", "The Forest", "Phasmophobia"]

#with open('data_file.csv', mode='a', newline='', encoding='utf-8') as table:
    #table_writer = csv.writer(table, quotechar='"', quoting=csv.QUOTE_ALL)
    #table_writer.writerow(["Game Name", "Genre", "Thread Title", "OP", "Replies Count", "Content", "Language", "URL", "Date/Time Collected", "Class"])

while Run:
    time.sleep(.2)
    url = "https://steamcommunity.com/app/427520/discussions/5/" + "?fp=" + str(page_num)
    name = "Factorio"
    genre = "Sandbox"

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    gamename = soup.find_all('div', class_='apphub_AppName')
    links = soup.find_all('a', class_='forum_topic_overlay')
    titles = soup.find_all(class_='forum_topic_name')
    replies = soup.find_all(class_='forum_topic_reply_count')
    posters = soup.find_all(class_='forum_topic_op')

    if links:
        print("Found Data on Page: " + str(page_num))
        discussion_count = len(links)

        for discussion in range(discussion_count):
            url = links[discussion].get('href')
            discussion_urls.append(url)

            title = titles[discussion].get_text(strip=True)
            discussion_titles.append(title)

            reply_count = replies[discussion].get_text(strip=True)
            discussion_replies.append(reply_count)

            op = posters[discussion].get_text(strip=True)
            discussion_ops.append(op)


        page_num += 1
    else:
        print("Data not found")
        Run = False

collected_threads = 0
for index in range(len(discussion_urls)):
    time.sleep(.2)
    title = discussion_titles[index]
    op = discussion_ops[index]
    reply_count = discussion_replies[index]
    url = discussion_urls[index]

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    script_tags = soup.find_all('script', type='text/javascript')
    filtered_text = ""

    for script in script_tags:
        script_text = script.get_text(strip=True)
        if "InitializeForumTopic" in script_text:
            text_index = script_text.find("text")
            if text_index != -1:
                filtered_text = script_text[text_index + len("text:"):]
                filtered_text = filtered_text[2:-15]
                unicode_escape_pattern = re.compile(r'\\u[0-9a-fA-F]{4}')
                try:
                    if unicode_escape_pattern.search(filtered_text):
                        filtered_text = filtered_text.encode('utf-8').decode('unicode_escape')
                        print(filtered_text)
                except:
                    filtered_text = "encoding failed"
    try:
        language = detect(filtered_text)
    except:
        language = "Detection Failed"

    translated_text = "-"
    if language != "en":
        if language != "Detection Failed":
            if language == "zh-cn":
                language = "zh"
            try:
                model_name = "Helsinki-NLP/opus-mt-"+language+"-en"
                tokenizer_name = "Helsinki-NLP/opus-mt-"+language+"-en"

                model = MarianMTModel.from_pretrained(model_name)
                tokenizer = MarianTokenizer.from_pretrained(tokenizer_name)

                input_ids = tokenizer(filtered_text, return_tensors="pt").input_ids

                output_ids = model.generate(input_ids)
                translated_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]

                unicode_escape_pattern = re.compile(r'\\u[0-9a-fA-F]{4}')

            except:
                translated_text = "translation failed"
        
    with open('data_file.csv', mode='a', newline='', encoding='utf-8') as table:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        table_writer = csv.writer(table, quotechar='"', quoting=csv.QUOTE_ALL)
        table_writer.writerow([name, genre, title, op, reply_count, filtered_text, language, translated_text, url, dt_string, "bug report"])
    table.close()

    collected_threads += 1
    print("[" + str(collected_threads) + "/" + str(len(discussion_urls)) + "]")

        
