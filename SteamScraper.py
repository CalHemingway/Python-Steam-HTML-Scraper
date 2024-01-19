import requests
from bs4 import BeautifulSoup
from langdetect import detect
from datetime import datetime
from transformers import MarianMTModel, MarianTokenizer
import csv
import time
import os

gameGenre = "Test"
game_URLs = ["https://steamcommunity.com/app/2680370/discussions/"]

def writeToCSV(wGameName, wGameGenre, wThreadTitle, wThreadTitleLanguage, wThreadTranslatedTitle, wThreadOp, wReplyCount, wBodyText, wThreadLanguage, wTranslatedText, wCombinedText, wCombinedTranslatedText, wUrl, wDateTime, wThreadClass):
    fileName = wGameGenre + "_file.csv" 
    doesExist = os.path.exists(fileName)
    with open(fileName, mode='a', newline='', encoding='utf-8') as table:
        table_writer = csv.writer(table, quotechar='"', quoting=csv.QUOTE_ALL)
        if doesExist == False:
            table_writer.writerow(["Game Name", "Game Genre", "OP", "Reply Count", "Thread Title", "Title Language", "Translated Title", "Body Text", "Language", "Translated Text", "Combined Text", "Combined Translated Text", "URL", "Date/Time Posted (PST)", "Date/Time Collected (GMT)", "Class"])
        wCurrentTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        table_writer.writerow([wGameName, wGameGenre, wThreadOp, wReplyCount, wThreadTitle, wThreadTitleLanguage, wThreadTranslatedTitle, wBodyText, wThreadLanguage, wTranslatedText, wCombinedText, wCombinedTranslatedText, wUrl, wDateTime, wCurrentTime, wThreadClass])
    table.close()
    
def format_DateTime(datetime_text):
    datetime_text = datetime_text['title']

    return datetime.strptime(datetime_text[0:-4], "%d %B, %Y @ %I:%M:%S %p").strftime("%d/%m/%y %H:%M")

def translate(body_text, language):
    translated_text = "-"
    if language not in ["en", "Detection Failed"]:
        if language == "zh-cn":
            language = "zh"
        print("Helsinki-NLP/opus-mt-"+language+"-en")
        try:
            model = MarianMTModel.from_pretrained(str("Helsinki-NLP/opus-mt-"+language+"-en"))
            tokenizer = MarianTokenizer.from_pretrained(str("Helsinki-NLP/opus-mt-"+language+"-en"))

            input_ids = tokenizer(body_text, return_tensors="pt").input_ids

            output_ids = model.generate(input_ids)
            translated_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
            print(translated_text)
        except:
            translated_text = "Translation Failed"

    return translated_text

def get_Thread_Body_Text(script_tags):
    filtered_text = ""
    for script in script_tags:
        script_text = script.get_text(strip=True)
        if "InitializeForumTopic" in script_text:
            text_index = script_text.find("text")
            if text_index != -1:
                filtered_text = script_text[text_index + len("text:"):]
                filtered_text = filtered_text[2:-15]
                try:
                    filtered_text = filtered_text.encode('utf-8').decode('unicode_escape')
                    print(filtered_text)
                except:
                    filtered_text = "encoding failed"
    
    return filtered_text

def get_Thread_Data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    datetime = format_DateTime(soup.find('span', class_= 'date'))
    script_tags = soup.find_all('script', type='text/javascript')
    body_text = get_Thread_Body_Text(script_tags)

    try:
        language = detect(body_text)
    except:
        language = "Detection Failed"

    translated_Body_Text = translate(body_text, language)

    return body_text, language, datetime, translated_Body_Text

def get_Index_Data(url):
    t_Urls, t_Titles, t_TitleLanguages, t_TranslatedTitles, t_Replies, t_OPs = [], [], [], [], [], []
    page_num = 1

    while True:
        time.sleep(.2)
        index_url = url + "?fp=" + str(page_num)
        page = requests.get(index_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        gameName = soup.find('div', class_='apphub_AppName').get_text(strip=True)
        print(gameName)
        links = soup.find_all('a', class_='forum_topic_overlay')
        titles = soup.find_all(class_='forum_topic_name')
        replies = soup.find_all(class_='forum_topic_reply_count')
        posters = soup.find_all(class_='forum_topic_op')

        if links:
            print("Found Data on Page: " + str(page_num))
            discussion_count = len(links)

            for discussion in range(discussion_count):
                try:
                    currentLanguage = detect(titles[discussion].get_text(strip=True))
                except:
                    currentLanguage = "Detection Failed"

                t_Urls.append(links[discussion].get('href'))
                t_Titles.append(titles[discussion].get_text(strip=True))
                t_TitleLanguages.append(currentLanguage)
                t_TranslatedTitles.append(translate(titles[discussion].get_text(strip=True), currentLanguage))
                t_Replies.append(replies[discussion].get_text(strip=True))
                t_OPs.append(posters[discussion].get_text(strip=True))

            page_num += 1
        else:
            print("Data not found")
            break

    return gameName,t_Urls, t_Titles, t_TitleLanguages, t_TranslatedTitles, t_Replies, t_OPs

def generateCombinedText(nativeTitle, translatedTitle, titleLanguage, nativeText, translatedText, textLanguage):
    combinedText = nativeTitle + nativeText
    if translatedTitle in ["-", "Translation Failed"]:
        translatedTitle = nativeTitle
    if translatedText in ["-", "Translation Failed"]:
        translatedText = nativeText

    if titleLanguage not in ["en", "Detection Failed"] or textLanguage not in ["en", "Detection Failed"]:
        translatedCombinedText = translatedTitle + translatedText
    else:
        translatedCombinedText = "-"
        
    return combinedText, translatedCombinedText

def main():
    for url in game_URLs:
        gameName, thread_urls, thread_titles, thread_TitleLanguages, thread_TranslatedTitles, thread_replies, thread_ops = get_Index_Data(url)
        print(len(thread_urls))
        for row_index in range(len(thread_urls)):
            time.sleep(.2)
            thread_bodyText, thread_Language, thread_DateTime, thread_TranslatedBodyText = get_Thread_Data(thread_urls[row_index])
            thread_combinedText, thread_combinedTranslatedText = generateCombinedText(thread_titles[row_index], thread_TranslatedTitles[row_index], thread_TitleLanguages[row_index], thread_bodyText, thread_TranslatedBodyText, thread_Language,)
            writeToCSV(gameName, gameGenre, thread_titles[row_index], thread_TitleLanguages[row_index], thread_TranslatedTitles[row_index], thread_ops[row_index], thread_replies[row_index], thread_bodyText, thread_Language, thread_TranslatedBodyText, thread_combinedText, thread_combinedTranslatedText, thread_urls[row_index], thread_DateTime, "Bug Report")
            
            print("Row Completed: [" + str(row_index) + "/" + str(len(thread_urls)) + "]")
main()