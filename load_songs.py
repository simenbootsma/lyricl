from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import selenium.common.exceptions as excepts
import pandas as pd
import time


# songtekst.net missing: 139, 253, 351, 377, 478, 518, 524, 544, 701, 702, 726, 756, 852, 953


def main():
    top2000 = pd.read_excel('NPORadio2-Top-2000-2024.xlsx')
    top2000 = top2000.iloc[251:]
    driver = open_genius()
    st = time.time()
    cnt = 0
    for i, song in top2000.iterrows():
        try:
            print("\r{:d}/{:d} [{:.2f} s/song] {:s} - {:s}".format(song['Notering'], 2000, 0 if cnt == 0 else (time.time()-st)/cnt, song['Titel'], song['Artiest']), end='')
            txt = load_lyrics_genius(song['Titel'], song['Artiest'], driver=driver)
            filepath = 'static/data/songs/Top2000_genius/song{:04d}.txt'.format(song['Notering'])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(txt)
        except:
            print("\nERROR on number {:d}\n".format(song["Notering"]))
            driver.close()
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

