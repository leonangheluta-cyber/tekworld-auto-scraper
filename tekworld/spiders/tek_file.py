import scrapy
import requests
import logging
import os
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    filename="script_tekworld.log")

telegram_bot=os.environ.get("TELEGRAM_BOT")
chat_id=os.environ.get("CHAT_ID")
      
class TekFileSpider(scrapy.Spider):
    name = "tek_file"
    allowed_domains = ["www.tekworld.it"]
    urls_category={"lavatrici" : "https://www.tekworld.it/1004-lavatrici",
                    "frigoriferi" : "https://www.tekworld.it/1005-frigoriferi",
                    "lavastoviglie" : "https://www.tekworld.it/1177-lavastoviglie",
                    "cucine" : "https://www.tekworld.it/1350-cucine", 
                    "cappe" : "https://www.tekworld.it/1248-cappe"}
    labels={"lavatrici" : ["Larghezza", "Profondità", "Altezza", "Durata della garanzia","Classe di efficienza della centrifuga", "Programmi di lavaggio", "Velocità di centrifuga massima", "Durata del ciclo (max)", "Consumo di energia per lavaggio", "Tipo di controllo"], 
               "frigoriferi" : ["Larghezza", "Profondità","Altezza", "Durata della garanzia", "Consumo d'energia", "Numero di cassetti per verdura", "Balconcini del frigorifero", "Tipo di cerniera della porta", "Numero di ripiani frigorifero", "Peso"], 
               "lavastoviglie" : ["Larghezza", "Profondità", "Altezza", "Durata della garanzia","Spia brillantante", "Numero di cestini", "Sistema di dosaggio automatico", "Display incorporato", "Emissione acustica", "Ciclo", "Consumo di acqua per ciclo"], 
               "cucine" : ["Larghezza", "Profondità", "Altezza","Durata della garanzia", "Numero di fuochi", "Sorgente di alimentazione del forno", "Materiale di rivestimento", "Tipo di accensione elettronica", "Numero totale di fuochi", "Numero di piani cottura utilizzabili contemporaneamente"], 
               "cappe" : ["Larghezza", "Profondità", "Potenza motore", "Numero di velocità", "Consumo energetico annuo", "Emissione acustica", "Potenza massima di estrazione", "Diametro del raccordo di scarico", "Numero di lampadine", "Display incorporato"]}

    names_missing=0

    def closed(self, reason):
        self.notify_allert("Step 1 finished")

    def notify_allert(self, message):
        url=f"https://api.telegram.org/bot{telegram_bot}/sendMessage"
        try:
            stat=requests.get(url, params={"chat_id": chat_id, "text": message})
            status=stat.status_code
            if status!=200:
                logging.warning(f"Failed to send {message} due to status")
        except requests.exceptions.RequestException as error:
            logging.warning(f"Failed to send {message}: {error}")

    async def start(self):
        for cat, link in self.urls_category.items():
            yield scrapy.Request(link, callback=self.parse, cb_kwargs={"category": cat})

    def parse(self, response, category, page_number=1):
        names=response.css("div.js-product-miniature-wrapper")
        if not names:
            return
        next_page=f"{self.urls_category[category]}?page={page_number+1}"
        yield response.follow(next_page, callback=self.parse, cb_kwargs={"page_number": page_number+1, "category": category})
        for n in names:
            link=n.css("div.thumbnail-container a::attr(href)").get()
            yield response.follow(link, callback=self.product_parse, cb_kwargs={"category": category})

    def product_parse(self, response, category):
        name=response.css("h1.page-title span::text").get()
        if not name:
            self.names_missing+=1
            logging.warning("Name not found")
            if self.names_missing==50:
                self.notify_allert("Names in page not found")
        avv=response.css("div.tw-buy-availability strong::text").get()
        if not avv:
            logging.warning(f"Availability not found for {name}")
        item_code=response.css("div.tw-product-code strong::text").get()
        if not item_code:
            logging.warning(f"Item_code not found for {name}")
        price=response.css("div.current-price span::attr(content)").get()
        if not price:
            logging.warning(f"Price not found for {name}")
        efficiency_class_ok=None
        efficiency_class=response.css("div.tw-energy-copy h2::text").get()
        if efficiency_class:
            efficiency_class_ok=efficiency_class.replace("Classe energetica", "").strip()
        else:
            logging.warning(f"Efficiency_class not found for {name}")
        catalogue={"Name": name, "Item_code": item_code, "Price": price, "Category": category, "Efficiency_class": efficiency_class_ok, "Availability": avv}
        details=response.css("div.tw-spec-row")
        for d in details:
            label=d.css("span::text").get()
            text=d.css("strong::text").get()
            if label in self.labels[category]:
                catalogue[label]=text
        yield catalogue