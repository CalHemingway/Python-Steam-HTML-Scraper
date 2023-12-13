import requests
from bs4 import BeautifulSoup
import csv
import time

page_num = 1
Run = True
discussion_urls = []
discussion_titles = []
discussion_replies = []
discussion_ops = []
discussion_contents = []

with open('data_file.csv', mode='a', newline='', encoding='utf-8') as table:
    table_writer = csv.writer(table)

    while Run:
        url = "https://steamcommunity.com/app/848450/discussions/1/" + "?fp=" + str(page_num)

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        links = soup.find_all('a', class_='forum_topic_overlay')
        titles = soup.find_all(class_='forum_topic_name')
        replies = soup.find_all(class_='forum_topic_reply_count')
        posters = soup.find_all(class_='forum_topic_op')

        if links:
            print("Found Data")
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



for index in range(len(discussion_urls)):
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
                print(filtered_text.strip())

    with open('data_file.csv', mode='a', newline='', encoding='utf-8') as table:
        table_writer = csv.writer(table)
        table_writer.writerow([title, op, reply_count, filtered_text, url])
    table.close()

        
