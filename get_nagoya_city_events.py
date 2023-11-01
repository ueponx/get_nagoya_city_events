import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import csv

def extract_event_info(date_tag):
    """
    HTMLの日付タグからイベント情報を抽出する関数。
    
    :param date_tag: BeautifulSoupオブジェクトの日付タグ
    :return: イベント情報のリスト
    """
    date_text = date_tag.get_text(strip=True)
    day, weekday = date_text[:-3], date_text[-3:]
    weekday_dict = {'月曜日': '月', '火曜日': '火', '水曜日': '水', '木曜日': '木', '金曜日': '金', '土曜日': '土', '日曜日': '日'}
    date = f"{day}({weekday_dict.get(weekday, '?')})"
    events = []
    events_td = date_tag.find_next_sibling('td')
    if events_td:
        for li in events_td.find_all('li'):
            event_title_tag = li.find('a')
            event_title = event_title_tag.get_text(strip=True) if event_title_tag else "タイトル不明"
            event_url = event_title_tag['href'] if event_title_tag and event_title_tag.has_attr('href') else "URL不明"
            event_categories = [span.text for span in li.find_all('span', class_=re.compile('eve_cate'))]
            events.append({
                '日付': date,
                'イベントタイトル': event_title,
                'イベントURL': event_url,
                'カテゴリ': ','.join(event_categories)
            })
    return events

def parse_html_from_url(url):
    """
    URLからHTMLを取得し、イベント情報を抽出する関数。
    
    :param url: イベント情報が含まれるウェブページのURL
    :return: イベント情報のリスト
    """
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    html_content = response.text.encode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    date_tags = soup.find_all('th', {'scope': 'row', 'class': 'cal_date'})
    all_events = []
    for date_tag in date_tags:
        all_events.extend(extract_event_info(date_tag))
    return all_events

def save_to_csv(events, output_path):
    """
    イベント情報をCSVファイルに保存する関数。
    
    :param events: イベント情報のリスト（辞書形式）
    :param output_path: 出力するCSVファイルのパス
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['日付', 'イベントタイトル', 'イベントURL', 'カテゴリ']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for event in events:
            writer.writerow(event)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="イベント情報を抽出してCSVファイルに保存します。")
    parser.add_argument('url', help="イベント情報が含まれるウェブページのURL")
    parser.add_argument('csv_file', help="抽出したイベント情報を保存するCSVファイルのパス")
    args = parser.parse_args()

    events = parse_html_from_url(args.url)
    save_to_csv(events, args.csv_file)
    print(f"イベント情報を{args.csv_file}に保存しました。")
