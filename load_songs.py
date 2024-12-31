from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import selenium.common.exceptions as excepts
import pandas as pd
import time


# C:\Users\Simen\PycharmProjects\lyricl\venv\Scripts\python.exe C:\Users\Simen\PycharmProjects\lyricl\load_songs.py
# 286/2000 [13.78 s/song] Deurdonderen (Live) - Normaal
# ERROR on number 286
#
# 318/2000 [14.78 s/song] Born Slippy - Underworld
# ERROR on number 318
#
# 386/2000 [14.53 s/song] Zij Gelooft In Mij (2004) - André Hazes
# ERROR on number 386
#
# 389/2000 [14.69 s/song] Dansen Aan Zee - BLØF
# ERROR on number 389

# Genius missing: 286, 318, 386, 389, 390, 614, 660, 688, 724, 800, 841, 850, 1053, 1129, 1297, 1330, 1366, 1390,
# 1464, 1465, 1529, 1546, 1650, 1704, 1708, 1771, 1780, 1879, 1883, 1885, 1907,

# songtekst.net missing: 139, 253, 351, 377, 478, 518, 524, 544, 701, 702, 726, 756, 852, 953


def main():
    # top2000 = pd.read_excel('NPORadio2-Top-2000-2024.xlsx')
    # idx = [286, 318, 386, 389, 390, 614, 660, 688, 724, 800, 841, 850, 1053, 1129, 1297, 1330, 1366, 1390, 1464, 1465, 1529, 1546, 1650, 1704, 1708, 1771, 1780, 1879, 1883, 1885, 1907,]
    # idx = [i-1 for i in idx]
    # top2000 = top2000.iloc[idx]
    kryst = pd.read_csv("top_100_allertijden_nederlandstalig.csv")
    driver = open_genius()
    st = time.time()
    cnt = 0
    for i, song in kryst.iterrows():
        try:
            # rank, title, artist = song['Numering'], song['Titel'], song['Artiest']
            title, artist = song['Nummmernaam'], song['Naam van artiest']
            print("\r{:d}/{:d} [{:.2f} s/song] {:s} - {:s}".format(i, len(kryst), 0 if cnt == 0 else (time.time()-st)/cnt, title, artist), end='')
            txt = load_lyrics_genius(title, artist, driver=driver)
            filepath = 'static/data/songs/Hollands/song{:04d}.txt'.format(i)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(txt)
        except:
            print("\nERROR on number {:d}\n".format(i))
            # driver.close()
            driver = open_genius()
        cnt += 1
    driver.close()


def open_genius():
    privacy_selector = "#onetrust-accept-btn-handler"

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://genius.com/")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, privacy_selector))).click()
    return driver


def load_lyrics_genius(title, artist, driver=None):
    q = title + ' ' + artist
    q = q.replace(' ', '%20')
    q = q.replace('(', '').replace(')', '')
    q = q.replace('Albumversie', '')

    privacy_selector = "#onetrust-accept-btn-handler"
    link_selector = "mini-song-card > a"
    text_selector = 'div[data-lyrics-container="true"]'
    url = "https://genius.com/search?q=" + q

    opened_driver = False
    if driver is None:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        opened_driver = True

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    if opened_driver:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, privacy_selector))).click()

    link_elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, link_selector)))
    driver.get(link_elems[0].get_attribute('href'))
    lyrics_elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, text_selector)))
    lyrics = ""
    for elem in lyrics_elems:
        lyrics += elem.text
    if opened_driver:
        driver.close()
    return lyrics


def open_songtekst_net():
    iframe_selector = "body > div:nth-child(10) > iframe"
    privacy_selector = "#buttons > div.btn.green"
    cookie_selector = "body > div.cc-window.cc-banner.cc-type-opt-out.cc-theme-classic.cc-bottom.cc-color-override-176448821 > div > a.cc-btn.cc-dismiss"

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://songteksten.net/")

    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
    driver.switch_to.frame(iframe)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, privacy_selector))).click()
    driver.switch_to.default_content()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_selector))).click()
    return driver


def load_songtext(title, artist, driver=None):
    q = title + ' ' + artist
    q = q.replace(' ', '+')

    iframe_selector = "body > div:nth-child(10) > iframe"
    privacy_selector = "#buttons > div.btn.green"
    cookie_selector = "body > div.cc-window.cc-banner.cc-type-opt-out.cc-theme-classic.cc-bottom.cc-color-override-176448821 > div > a.cc-btn.cc-dismiss"
    link_selector = "body > div:nth-child(5) > div.st-main.uk-container.uk-container-center.uk-margin-large-bottom > div > main > div:nth-child(6) > div > a"
    link_selector = "main > div:nth-child(6) > div > a"
    text_selector = "body > div:nth-child(4) > div.st-main.uk-container.uk-container-center.uk-margin-large-bottom > div > main > article > div:nth-child(2)"
    text_selector = "main > article"
    url = "https://songteksten.net/search.html?q={:s}&type%5B%5D=lyric".format(q)

    opened_driver = False
    if driver is None:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        opened_driver = True

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    if opened_driver:
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
        driver.switch_to.frame(iframe)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, privacy_selector))).click()
        driver.switch_to.default_content()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cookie_selector))).click()

    link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))).get_attribute("href")
    driver.get(link)
    text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, text_selector))).text
    if opened_driver:
        driver.close()
    return text


if __name__ == '__main__':
    main()

