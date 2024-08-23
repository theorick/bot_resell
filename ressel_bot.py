from bs4 import BeautifulSoup
import requests
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import telebot



telegram_api_key = 'API KEY'
bot = telebot.TeleBot(telegram_api_key)

url_original = 'https://www.whentocop.fr'
url = 'https://www.whentocop.fr/drops'
hrefs = []




def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    while True:
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_load_state('networkidle')
        time.sleep(3)  # wait for 3 seconds
        
        # check if we've reached the end of the page
        if page.evaluate('document.body.scrollHeight') == page.evaluate('window.scrollY + window.innerHeight'):
            break

        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        products = soup.find_all('div', class_='DropCard__InfosContainer-sc-1f2e4y6-2 hWiPyA')
        all_info = soup.find_all('div', class_='infinite-scroll-component')

        for info in all_info:
            links = info.find_all('a')
            for link in links:
                href = link.get('href')
                if href:
                    #print(href)
                    hrefs.append(href)

        t = 0
        brand_models = []
        resell_status_all = []
        url_propre = []
        for product in products:
            brand_model = product.find('h3', class_='DropCard__CardBrandName-sc-1f2e4y6-5').text.strip()
            resell_status = product.find('p', class_='DropCard__CardResellIndex-sc-1f2e4y6-7')
            if resell_status is not None:
                resell_status = resell_status.text.strip()
                if resell_status != '(non disponible)':
                    if resell_status == 'bon resell':
                        url_merch = url_original + hrefs[t]
                        t += 1

                        #print(f"Modèle: {brand_model}, Note de revente: {resell_status}, href : {url_merch} ")
                        resell_status_all.append(resell_status)
                        brand_models.append(brand_model)
                        url_propre.append(url_merch)


            else:
                a = 0
                #print(f"Modèle: {brand_model}, Note de revente: (non disponible)")

        print(len(set(hrefs)))
        print(brand_models)
        print(resell_status_all)
        print(url_propre)
        if len(url_propre) >= 15:
            @bot.message_handler(commands=['resell'])
            def send_resell_info(message):
                for k in range(len(url_propre)):
                    bot.send_message(message.chat.id,
                                     f"✫ Modèle: {brand_models[k]} \n"
                                     f"✬ Note de revente: {resell_status_all[k]} \n"
                                     f"▪ href : {url_propre[k]} \n")

            # Cette ligne permet au bot de rester actif et de répondre aux commandes
            bot.infinity_polling()
        # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
