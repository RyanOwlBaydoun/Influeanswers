import sqlite3
import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Slowing the code so that it's less detectable
def random_sleep(min_time, max_time):
    """Sleeps for a random duration between min_time and max_time seconds."""
    time.sleep(random.uniform(min_time, max_time))


def human_like_scroll(browser, iterations):
    """Simulates human-like scrolling."""
    for _ in range(iterations):
        browser.execute_script('window.scrollBy(0, -100);')
        random_sleep(0.3, 0.8)

# Setting up Chrome options
chrome_options = webdriver.ChromeOptions()
# Creating a User in the Local Disk C and Using it inside the function so that we only need to scrape the QR code once
chrome_options.add_argument("--user-data-dir=C:/post_block_whatsapp_scraper")

# Set up the browser with the specified options
webdriver_service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Navigate to WhatsApp Web
browser.get('https://web.whatsapp.com/')

# Wait for the search box to appear
wait = WebDriverWait(browser, 40)  # wait for 40 seconds

group_names = ["موقع صدى الضاحية 150",
               "موقع بيروت الحرة 20",
               "Enooma - 6",
               "Lebanon Now⓻⓵",
               "أبناء بيروت الإخبارية (3)", 
               "Leb economy 8",
               "أخباري ٣٩",
               "ثورة وجع الإنسان ٥٣",
                "أخباري ٥٢",
               "حصل اليوم في لبنان ",             
               " شـبـكـة الحدث عـاجـل ",
               "أخبار التحرّي | 11",
               "هنا لبنان ⓪⑧①",
               "Lebanon Mirror 49",
               "Beirut Daily News ➎➊",
               "المَرْصَد الإخبَاري(100)",
               "لبنان والعالم{٢٤}",
               " أخــــبـار SBI ",
               "VDLnews-1",
               "❸❶❸ⓃⒺⓌⓈ➠❶⓿",
               " مـجـتـمـع الـحـدث عـاجـل ",
               "NEWS L",
               "961Times[299]",
               "Lebanon 365 News ",
               "أخبار المستقبل ٤ ( منسقية صيدا والجنوب )",
               "التحري نيوز (2)",
               "Addiyar -20-",]

               
"""
"🇱🇧𝙉𝙀𝙒𝙎 𝙁𝙊𝙍 𝙇𝙀𝘽𝘼𝙉𝙊𝙉🇱🇧",
               "𝟡𝟞𝟙𝐓𝐎𝐃𝐀𝐘.𝐂𝐎𝐌 ",
"""

back_button_xpath = '//*[@id="side"]/div[1]/div/div/button/div[2]/span'
group_profile_picture_xpath = '//*[@id="pane-side"]/div[1]/div/div/div[1]/div/div/div/div[1]'

# Retry mechanism function
def retry_action(action, max_retries=3, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            return action()
        except Exception as e:
            if "stale element reference" in str(e).lower():
                print(f"Stale element encountered. Retry {retries + 1} of {max_retries}.")
                time.sleep(delay)
                retries += 1
            else:
                raise e
    raise Exception("Max retries reached.")

for group_name in group_names:
    print(f"Processing group: {group_name}")  # Debugging print

    try:
        # Use the retry mechanism
        def search_and_select_group():
            # Random wait before searching for the next group
            random_sleep(0.3, 1)
            
            # Always re-find the search box before interacting
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='side']/div[1]/div/div/div[2]/div/div[1]/p")))
            
            # Clear the search box
            search_box.click()
            random_sleep(0.4, 0.9)
            search_box.send_keys(Keys.CONTROL + "a")  # Select all text in the search box
            random_sleep(0.3, 0.8)
            search_box.send_keys(Keys.DELETE)  # Delete the selected text (clear the search box)

            # Type the group name
            search_box.send_keys(group_name)
            random_sleep(0.3, 1.1)

            # Use keyboard to select the group and enter
            search_box.send_keys(Keys.DOWN)
            random_sleep(0.3, 0.8)
            search_box.send_keys(Keys.ENTER)
            random_sleep(0.3, 0.8)

            # Human-like scrolling
            human_like_scroll(browser, 3)

            # Scroll to load messages (iterations)
            iterations = 2
            for _ in range(iterations):
                browser.execute_script('window.scrollTo(0, 0);')
                sleep_duration = random.uniform(0.6, 2)
                time.sleep(sleep_duration)

        # Use the retry function to perform the action
        retry_action(search_and_select_group, max_retries=3)

        print(f"Scraping messages for group: {group_name}")

    except Exception as e:
        print(f"Error processing group {group_name}: {e}")

    # Get the page source
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract data
    messages_data = []

    # Locate each message container
    message_containers = soup.find_all('span', class_='_11JPr selectable-text copyable-text')

    for container in message_containers:
        content_span = container.find('span', class_='f804f6gw ln8gz9je')
        if not content_span:
            continue

        # Extract the entire message content
        full_text = content_span.get_text().strip()

        # Extract all links
        link_elements = content_span.find_all('a')
        all_links = [link['href'] for link in link_elements if link.has_attr('href')] if link_elements else []

        # Extracting the timestamp for this specific message container
        timestamp_container = container.find_next('span', class_='l7jjieqr fewfhwl7')
        timestamp_text = timestamp_container.text if timestamp_container else None

        # Extracting the date for this specific message container
        date_container = container.find_parent('div', class_='_1DETJ copyable-text')
        date_text = None
        if date_container:
            date_info = date_container.get('data-pre-plain-text', '')
            date_parts = date_info.split(']')
            if len(date_parts) > 1:
                date_text = date_parts[0].split(',')[1].strip()

        # Append to the list
        messages_data.append((full_text, ', '.join(all_links), date_text, timestamp_text))

    # Store in SQLite
    conn = sqlite3.connect("whatsapp_messages.db")
    cursor = conn.cursor()

    # Create a sanitized table name based on the group name
    sanitized_group_name = ''.join(e if e.isalnum() else '_' for e in group_name)
    table_name = 'group_' + (sanitized_group_name if not sanitized_group_name[0].isdigit() else "_" + sanitized_group_name)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        content TEXT UNIQUE,
        link TEXT,
        date DATE,
        timestamp TIME
    )
    """)

    for message in messages_data:
        try:
            cursor.execute(f"INSERT INTO {table_name} (content, link, date, timestamp) VALUES (?, ?, ?, ?)", message)
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    # Clear the messages_data list for the next group
    messages_data.clear()

conn.close()
browser.close()
