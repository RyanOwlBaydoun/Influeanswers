import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3


def determine_date_for_article(article_time, current_time):
    # Calculate the difference in hours and minutes
    time_difference = (current_time.hour - article_time.hour) * 60 + (current_time.minute - article_time.minute)
    
    if time_difference < 0:
        return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        return datetime.now().strftime('%Y-%m-%d')
    

def scrape_aljadeed_highlights():
    # Connect to SQLite database
    conn = sqlite3.connect('C:\\Al Jadeed\\aljadeed_data.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "Al Jadeed" (
        date TEXT,
        headline TEXT,
        link TEXT
    )
    ''')

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().time()

    seen_links = set()

    # Initial URL
    url = "https://www.aljadeed.tv/news/category/55/%D9%85%D8%AD%D9%84%D9%8A%D8%A7%D8%AA"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the news highlights and timestamps from the new div
    news_items = soup.select('div.card-header-container.order-3 h2.u-inheritStyle > a')
    timestamps_initial = soup.select('div.card-header-container.order-3 div.card-date.card-body-nextto-header-date.text-title-8.hide-sm.hide-xs')
    
    # Get the most recent link from the database
    cursor.execute("SELECT link FROM 'Al Jadeed' ORDER BY date DESC LIMIT 1")
    most_recent_link = cursor.fetchone()
    if most_recent_link:
        most_recent_link = most_recent_link[0]
    else:
        most_recent_link = None

    for i, news in enumerate(news_items):
      title = news.text
      link = news['href']
      article_time = datetime.strptime(timestamps_initial[i].text.strip(), "%H:%M").time()
      
      date_for_article = determine_date_for_article(article_time, current_time)
    
      time_stamp = f"{date_for_article} {timestamps_initial[i].text.strip()}"
      # Convert relative URL to absolute
      if not link.startswith('http'):
          link = 'https://www.aljadeed.tv' + link
    
      # Check if the scraped link matches the most recent link in the database
      if link == most_recent_link:
            print("Most recent link matches the scraped link. Stopping scraping process.")
            conn.commit()
            conn.close()
            return  # Exit the function

      # Check if the link already exists in the database
      cursor.execute("SELECT * FROM 'Al Jadeed' WHERE link=?", (link,))
      existing_entry = cursor.fetchone()


      if not existing_entry:
          # Insert data into the database
          try:
              cursor.execute("INSERT INTO 'Al Jadeed' (date, headline, link) VALUES (?, ?, ?)", (time_stamp, title, link))
              print(f'Timestamp: {time_stamp}')
              print(f'Title: {title}')
              print(f'Link: {link}')
          except sqlite3.Error as e:
              print(f"SQLite error: {e}")

    # Continue with the requests and BeautifulSoup script for "Load More"
    base_url = "https://www.aljadeed.tv/Website/DynamicPages/LoadMore/Loadmore_ArticleCategoryTemplate1.aspx?loadindex={}&lang=ar&rnd=581&ID=55&mostreadperiod=daily"
    loadindex = 1  # Starting index
    max_iterations = 100  # 10 iterations = 10 baches = 60 headlines= one day HHHHHHHHHHHHEEEEEEERRRRRRREEEEEEEEEEEEEEEEE

    time_pattern = re.compile(r"\d{2}:\d{2}")

    while loadindex <= max_iterations:
        response = requests.get(base_url.format(loadindex))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = soup.select('h2.u-inheritStyle > a')
        timestamps = soup.select('div.card-date.card-body-nextto-header-date.text-title-8.hide-sm.hide-xs')
        
        # If no more news items found, break the loop
        if not news_items:
            break

        timestamp_index = 0
        for i, news in enumerate(news_items):
            title = news.text
            link = news['href']
            time_only = timestamps[timestamp_index].text.strip()

            # If the timestamp is in the format "08:13", determine the date based on the time difference
            if time_pattern.match(time_only):
                article_time = datetime.strptime(time_only, "%H:%M").time()
                date_for_article = determine_date_for_article(article_time, current_time)
                time_stamp = f"{date_for_article} {time_only}"
            else:
                time_stamp = time_only


            # Convert relative URL to absolute
            if not link.startswith('http'):
                link = 'https://www.aljadeed.tv' + link

            # Check if link is already seen
            if link not in seen_links:
                print(f'Timestamp: {time_stamp}')
                print(f'Title: {title}')
                print(f'Link: {link}')
                seen_links.add(link)  # Add the link to the set

            # Use the same timestamp for every two headlines
            if i % 2 != 0:
                timestamp_index += 1

            # Check if the scraped link matches the most recent link in the database
            if link == most_recent_link:
                print("Most recent link matches the scraped link. Stopping scraping process.")
                conn.commit()
                conn.close()
                return  # Exit the function

            # Check if the link already exists in the database
            cursor.execute("SELECT * FROM 'Al Jadeed' WHERE link=?", (link,))
            existing_entry = cursor.fetchone()

            if not existing_entry:
                try:
                    cursor.execute("INSERT INTO 'Al Jadeed' (date, headline, link) VALUES (?, ?, ?)", (time_stamp, title, link))
                except sqlite3.Error as e:
                    print(f"SQLite error: {e}")
 

        loadindex += 1  # Increment to get the next batch of articles

    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_aljadeed_highlights()
