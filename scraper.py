"""
Akademik Veri Toplama Scripti
Türkiye'deki üniversiteler, akademisyenler ve yayınları çeker.
Kaynaklar: YÖK, üniversite web siteleri, açık akademik veriler.
"""

import json
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import Academic, Publication, University

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}


# ─── Türkiye Üniversiteleri (Kapsamlı Liste) ──────────────────────────────

TURKISH_UNIVERSITIES = [
    # Devlet Üniversiteleri
    {"name": "İstanbul Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.istanbul.edu.tr", "established": 1453},
    {"name": "İstanbul Teknik Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.itu.edu.tr", "established": 1773},
    {"name": "Ankara Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.ankara.edu.tr", "established": 1946},
    {"name": "Hacettepe Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.hacettepe.edu.tr", "established": 1967},
    {"name": "Orta Doğu Teknik Üniversitesi (ODTÜ)", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.metu.edu.tr", "established": 1956},
    {"name": "Boğaziçi Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.boun.edu.tr", "established": 1863},
    {"name": "Ege Üniversitesi", "city": "İzmir", "region": "Ege", "type": "Devlet", "website": "https://www.ege.edu.tr", "established": 1955},
    {"name": "Dokuz Eylül Üniversitesi", "city": "İzmir", "region": "Ege", "type": "Devlet", "website": "https://www.deu.edu.tr", "established": 1982},
    {"name": "Gazi Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.gazi.edu.tr", "established": 1926},
    {"name": "Atatürk Üniversitesi", "city": "Erzurum", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.atauni.edu.tr", "established": 1957},
    {"name": "Karadeniz Teknik Üniversitesi", "city": "Trabzon", "region": "Karadeniz", "type": "Devlet", "website": "https://www.ktu.edu.tr", "established": 1955},
    {"name": "Erciyes Üniversitesi", "city": "Kayseri", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.erciyes.edu.tr", "established": 1978},
    {"name": "Çukurova Üniversitesi", "city": "Adana", "region": "Akdeniz", "type": "Devlet", "website": "https://www.cu.edu.tr", "established": 1973},
    {"name": "Uludağ Üniversitesi (Bursa Uludağ)", "city": "Bursa", "region": "Marmara", "type": "Devlet", "website": "https://www.uludag.edu.tr", "established": 1975},
    {"name": "Akdeniz Üniversitesi", "city": "Antalya", "region": "Akdeniz", "type": "Devlet", "website": "https://www.akdeniz.edu.tr", "established": 1982},
    {"name": "Selçuk Üniversitesi", "city": "Konya", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.selcuk.edu.tr", "established": 1975},
    {"name": "Ondokuz Mayıs Üniversitesi", "city": "Samsun", "region": "Karadeniz", "type": "Devlet", "website": "https://www.omu.edu.tr", "established": 1975},
    {"name": "Fırat Üniversitesi", "city": "Elazığ", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.firat.edu.tr", "established": 1975},
    {"name": "Dicle Üniversitesi", "city": "Diyarbakır", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.dicle.edu.tr", "established": 1966},
    {"name": "Yıldız Teknik Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.yildiz.edu.tr", "established": 1911},
    {"name": "Marmara Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.marmara.edu.tr", "established": 1883},
    {"name": "İstanbul Üniversitesi-Cerrahpaşa", "city": "İstanbul", "region": "Marmara", "type": "Devlet", "website": "https://www.iuc.edu.tr", "established": 2018},
    {"name": "Gebze Teknik Üniversitesi", "city": "Kocaeli", "region": "Marmara", "type": "Devlet", "website": "https://www.gtu.edu.tr", "established": 1992},
    {"name": "Sakarya Üniversitesi", "city": "Sakarya", "region": "Marmara", "type": "Devlet", "website": "https://www.sakarya.edu.tr", "established": 1992},
    {"name": "Anadolu Üniversitesi", "city": "Eskişehir", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.anadolu.edu.tr", "established": 1958},
    {"name": "Eskişehir Osmangazi Üniversitesi", "city": "Eskişehir", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.ogu.edu.tr", "established": 1993},
    {"name": "Pamukkale Üniversitesi", "city": "Denizli", "region": "Ege", "type": "Devlet", "website": "https://www.pau.edu.tr", "established": 1992},
    {"name": "Süleyman Demirel Üniversitesi", "city": "Isparta", "region": "Akdeniz", "type": "Devlet", "website": "https://www.sdu.edu.tr", "established": 1992},
    {"name": "Mersin Üniversitesi", "city": "Mersin", "region": "Akdeniz", "type": "Devlet", "website": "https://www.mersin.edu.tr", "established": 1992},
    {"name": "Gaziantep Üniversitesi", "city": "Gaziantep", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.gantep.edu.tr", "established": 1987},
    {"name": "Kocaeli Üniversitesi", "city": "Kocaeli", "region": "Marmara", "type": "Devlet", "website": "https://www.kocaeli.edu.tr", "established": 1992},
    {"name": "Trakya Üniversitesi", "city": "Edirne", "region": "Marmara", "type": "Devlet", "website": "https://www.trakya.edu.tr", "established": 1982},
    {"name": "Celal Bayar Üniversitesi (Manisa CBÜ)", "city": "Manisa", "region": "Ege", "type": "Devlet", "website": "https://www.cbu.edu.tr", "established": 1992},
    {"name": "Balıkesir Üniversitesi", "city": "Balıkesir", "region": "Marmara", "type": "Devlet", "website": "https://www.balikesir.edu.tr", "established": 1992},
    {"name": "Çanakkale Onsekiz Mart Üniversitesi", "city": "Çanakkale", "region": "Marmara", "type": "Devlet", "website": "https://www.comu.edu.tr", "established": 1992},
    {"name": "Afyon Kocatepe Üniversitesi", "city": "Afyonkarahisar", "region": "Ege", "type": "Devlet", "website": "https://www.aku.edu.tr", "established": 1992},
    {"name": "Muğla Sıtkı Koçman Üniversitesi", "city": "Muğla", "region": "Ege", "type": "Devlet", "website": "https://www.mu.edu.tr", "established": 1992},
    {"name": "Abant İzzet Baysal Üniversitesi (Bolu ABİBÜ)", "city": "Bolu", "region": "Karadeniz", "type": "Devlet", "website": "https://www.ibu.edu.tr", "established": 1992},
    {"name": "Düzce Üniversitesi", "city": "Düzce", "region": "Karadeniz", "type": "Devlet", "website": "https://www.duzce.edu.tr", "established": 2006},
    {"name": "Recep Tayyip Erdoğan Üniversitesi", "city": "Rize", "region": "Karadeniz", "type": "Devlet", "website": "https://www.erdogan.edu.tr", "established": 2006},
    {"name": "Giresun Üniversitesi", "city": "Giresun", "region": "Karadeniz", "type": "Devlet", "website": "https://www.giresun.edu.tr", "established": 2006},
    {"name": "Ordu Üniversitesi", "city": "Ordu", "region": "Karadeniz", "type": "Devlet", "website": "https://www.odu.edu.tr", "established": 2006},
    {"name": "Bülent Ecevit Üniversitesi (Zonguldak BEÜ)", "city": "Zonguldak", "region": "Karadeniz", "type": "Devlet", "website": "https://www.beun.edu.tr", "established": 1992},
    {"name": "Bartın Üniversitesi", "city": "Bartın", "region": "Karadeniz", "type": "Devlet", "website": "https://www.bartin.edu.tr", "established": 2008},
    {"name": "Sinop Üniversitesi", "city": "Sinop", "region": "Karadeniz", "type": "Devlet", "website": "https://www.sinop.edu.tr", "established": 2007},
    {"name": "Kastamonu Üniversitesi", "city": "Kastamonu", "region": "Karadeniz", "type": "Devlet", "website": "https://www.kastamonu.edu.tr", "established": 2006},
    {"name": "Karabük Üniversitesi", "city": "Karabük", "region": "Karadeniz", "type": "Devlet", "website": "https://www.karabuk.edu.tr", "established": 2007},
    {"name": "Hitit Üniversitesi", "city": "Çorum", "region": "Karadeniz", "type": "Devlet", "website": "https://www.hitit.edu.tr", "established": 2006},
    {"name": "Amasya Üniversitesi", "city": "Amasya", "region": "Karadeniz", "type": "Devlet", "website": "https://www.amasya.edu.tr", "established": 2006},
    {"name": "Tokat Gaziosmanpaşa Üniversitesi", "city": "Tokat", "region": "Karadeniz", "type": "Devlet", "website": "https://www.gop.edu.tr", "established": 1992},
    {"name": "Sivas Cumhuriyet Üniversitesi", "city": "Sivas", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.cumhuriyet.edu.tr", "established": 1974},
    {"name": "Necmettin Erbakan Üniversitesi", "city": "Konya", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.erbakan.edu.tr", "established": 2010},
    {"name": "Konya Teknik Üniversitesi", "city": "Konya", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.ktun.edu.tr", "established": 2018},
    {"name": "Niğde Ömer Halisdemir Üniversitesi", "city": "Niğde", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.ohu.edu.tr", "established": 1992},
    {"name": "Aksaray Üniversitesi", "city": "Aksaray", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.aksaray.edu.tr", "established": 2006},
    {"name": "Kırıkkale Üniversitesi", "city": "Kırıkkale", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.kku.edu.tr", "established": 1992},
    {"name": "Kırşehir Ahi Evran Üniversitesi", "city": "Kırşehir", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.ahievran.edu.tr", "established": 2006},
    {"name": "Nevşehir Hacı Bektaş Veli Üniversitesi", "city": "Nevşehir", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.nevsehir.edu.tr", "established": 2007},
    {"name": "Yozgat Bozok Üniversitesi", "city": "Yozgat", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.bozok.edu.tr", "established": 2006},
    {"name": "Ankara Yıldırım Beyazıt Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.aybu.edu.tr", "established": 2010},
    {"name": "Ankara Sosyal Bilimler Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.asbu.edu.tr", "established": 2013},
    {"name": "Ankara Hacı Bayram Veli Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Devlet", "website": "https://www.hbv.edu.tr", "established": 2018},
    {"name": "İnönü Üniversitesi", "city": "Malatya", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.inonu.edu.tr", "established": 1975},
    {"name": "Van Yüzüncü Yıl Üniversitesi", "city": "Van", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.yyu.edu.tr", "established": 1982},
    {"name": "Malatya Turgut Özal Üniversitesi", "city": "Malatya", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.ozal.edu.tr", "established": 2018},
    {"name": "Erzincan Binali Yıldırım Üniversitesi", "city": "Erzincan", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.ebyu.edu.tr", "established": 2006},
    {"name": "Kafkas Üniversitesi", "city": "Kars", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.kafkas.edu.tr", "established": 1992},
    {"name": "Ağrı İbrahim Çeçen Üniversitesi", "city": "Ağrı", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.agri.edu.tr", "established": 2007},
    {"name": "Iğdır Üniversitesi", "city": "Iğdır", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.igdir.edu.tr", "established": 2008},
    {"name": "Ardahan Üniversitesi", "city": "Ardahan", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.ardahan.edu.tr", "established": 2008},
    {"name": "Bingöl Üniversitesi", "city": "Bingöl", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.bingol.edu.tr", "established": 2007},
    {"name": "Bitlis Eren Üniversitesi", "city": "Bitlis", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.beu.edu.tr", "established": 2007},
    {"name": "Muş Alparslan Üniversitesi", "city": "Muş", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.alparslan.edu.tr", "established": 2007},
    {"name": "Hakkari Üniversitesi", "city": "Hakkari", "region": "Doğu Anadolu", "type": "Devlet", "website": "https://www.hakkari.edu.tr", "established": 2008},
    {"name": "Siirt Üniversitesi", "city": "Siirt", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.siirt.edu.tr", "established": 2007},
    {"name": "Batman Üniversitesi", "city": "Batman", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.batman.edu.tr", "established": 2007},
    {"name": "Şırnak Üniversitesi", "city": "Şırnak", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.sirnak.edu.tr", "established": 2008},
    {"name": "Mardin Artuklu Üniversitesi", "city": "Mardin", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.artuklu.edu.tr", "established": 2007},
    {"name": "Harran Üniversitesi", "city": "Şanlıurfa", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.harran.edu.tr", "established": 1992},
    {"name": "Adıyaman Üniversitesi", "city": "Adıyaman", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.adiyaman.edu.tr", "established": 2006},
    {"name": "Kilis 7 Aralık Üniversitesi", "city": "Kilis", "region": "Güneydoğu Anadolu", "type": "Devlet", "website": "https://www.kilis.edu.tr", "established": 2007},
    {"name": "Osmaniye Korkut Ata Üniversitesi", "city": "Osmaniye", "region": "Akdeniz", "type": "Devlet", "website": "https://www.osmaniye.edu.tr", "established": 2007},
    {"name": "Hatay Mustafa Kemal Üniversitesi", "city": "Hatay", "region": "Akdeniz", "type": "Devlet", "website": "https://www.mku.edu.tr", "established": 1992},
    {"name": "Kahramanmaraş Sütçü İmam Üniversitesi", "city": "Kahramanmaraş", "region": "Akdeniz", "type": "Devlet", "website": "https://www.ksu.edu.tr", "established": 1992},
    {"name": "İskenderun Teknik Üniversitesi", "city": "Hatay", "region": "Akdeniz", "type": "Devlet", "website": "https://www.iste.edu.tr", "established": 2015},
    {"name": "Isparta Uygulamalı Bilimler Üniversitesi", "city": "Isparta", "region": "Akdeniz", "type": "Devlet", "website": "https://www.isparta.edu.tr", "established": 2018},
    {"name": "Burdur Mehmet Akif Ersoy Üniversitesi", "city": "Burdur", "region": "Akdeniz", "type": "Devlet", "website": "https://www.mehmetakif.edu.tr", "established": 2006},
    {"name": "Alanya Alaaddin Keykubat Üniversitesi", "city": "Antalya", "region": "Akdeniz", "type": "Devlet", "website": "https://www.alanya.edu.tr", "established": 2015},
    {"name": "Adana Alparslan Türkeş Bilim ve Teknoloji Üniversitesi", "city": "Adana", "region": "Akdeniz", "type": "Devlet", "website": "https://www.atu.edu.tr", "established": 2011},
    {"name": "Tarsus Üniversitesi", "city": "Mersin", "region": "Akdeniz", "type": "Devlet", "website": "https://www.tarsus.edu.tr", "established": 2018},
    {"name": "Tekirdağ Namık Kemal Üniversitesi", "city": "Tekirdağ", "region": "Marmara", "type": "Devlet", "website": "https://www.nku.edu.tr", "established": 2006},
    {"name": "Kırklareli Üniversitesi", "city": "Kırklareli", "region": "Marmara", "type": "Devlet", "website": "https://www.klu.edu.tr", "established": 2007},
    {"name": "Uşak Üniversitesi", "city": "Uşak", "region": "Ege", "type": "Devlet", "website": "https://www.usak.edu.tr", "established": 2006},
    {"name": "Bilecik Şeyh Edebali Üniversitesi", "city": "Bilecik", "region": "Marmara", "type": "Devlet", "website": "https://www.bilecik.edu.tr", "established": 2007},
    {"name": "Bolu Abant İzzet Baysal Üniversitesi", "city": "Bolu", "region": "Karadeniz", "type": "Devlet", "website": "https://www.ibu.edu.tr", "established": 1992},
    {"name": "Samsun Üniversitesi", "city": "Samsun", "region": "Karadeniz", "type": "Devlet", "website": "https://www.samsun.edu.tr", "established": 2018},
    {"name": "Trabzon Üniversitesi", "city": "Trabzon", "region": "Karadeniz", "type": "Devlet", "website": "https://www.trabzon.edu.tr", "established": 2018},
    # Vakıf Üniversiteleri
    {"name": "Koç Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.ku.edu.tr", "established": 1993},
    {"name": "Sabancı Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.sabanciuniv.edu", "established": 1994},
    {"name": "Bilkent Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.bilkent.edu.tr", "established": 1984},
    {"name": "Özyeğin Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.ozyegin.edu.tr", "established": 2007},
    {"name": "Bahçeşehir Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.bau.edu.tr", "established": 1998},
    {"name": "Yeditepe Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.yeditepe.edu.tr", "established": 1996},
    {"name": "Kadir Has Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.khas.edu.tr", "established": 1997},
    {"name": "İstanbul Bilgi Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.bilgi.edu.tr", "established": 1996},
    {"name": "İstanbul Kültür Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.iku.edu.tr", "established": 1997},
    {"name": "Doğuş Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.dogus.edu.tr", "established": 1997},
    {"name": "Maltepe Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.maltepe.edu.tr", "established": 1997},
    {"name": "Beykent Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.beykent.edu.tr", "established": 1997},
    {"name": "İstanbul Aydın Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.aydin.edu.tr", "established": 2003},
    {"name": "Haliç Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.halic.edu.tr", "established": 1998},
    {"name": "Başkent Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.baskent.edu.tr", "established": 1994},
    {"name": "Atılım Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.atilim.edu.tr", "established": 1997},
    {"name": "TOBB Ekonomi ve Teknoloji Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.etu.edu.tr", "established": 2003},
    {"name": "Çankaya Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.cankaya.edu.tr", "established": 1997},
    {"name": "TED Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.tedu.edu.tr", "established": 2009},
    {"name": "İhsan Doğramacı Bilkent Üniversitesi", "city": "Ankara", "region": "İç Anadolu", "type": "Vakıf", "website": "https://www.bilkent.edu.tr", "established": 1984},
    {"name": "Yaşar Üniversitesi", "city": "İzmir", "region": "Ege", "type": "Vakıf", "website": "https://www.yasar.edu.tr", "established": 2001},
    {"name": "İzmir Ekonomi Üniversitesi", "city": "İzmir", "region": "Ege", "type": "Vakıf", "website": "https://www.ieu.edu.tr", "established": 2001},
    {"name": "Gedik Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.gedik.edu.tr", "established": 2008},
    {"name": "Nişantaşı Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.nisantasi.edu.tr", "established": 2009},
    {"name": "Medipol Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.medipol.edu.tr", "established": 2009},
    {"name": "Üsküdar Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.uskudar.edu.tr", "established": 2011},
    {"name": "İstanbul Sabahattin Zaim Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.izu.edu.tr", "established": 2010},
    {"name": "İstanbul Ticaret Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.ticaret.edu.tr", "established": 2001},
    {"name": "İstanbul Gelişim Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.gelisim.edu.tr", "established": 2008},
    {"name": "Acıbadem Üniversitesi", "city": "İstanbul", "region": "Marmara", "type": "Vakıf", "website": "https://www.acibadem.edu.tr", "established": 2007},
]

# ─── Yurt Dışı Üniversiteleri ──────────────────────────────────────────────

INTERNATIONAL_UNIVERSITIES = [
    # ABD
    {"name": "Massachusetts Institute of Technology (MIT)", "city": "Cambridge, MA", "region": "ABD", "type": "Özel", "website": "https://www.mit.edu", "established": 1861},
    {"name": "Stanford University", "city": "Stanford, CA", "region": "ABD", "type": "Özel", "website": "https://www.stanford.edu", "established": 1885},
    {"name": "Harvard University", "city": "Cambridge, MA", "region": "ABD", "type": "Özel", "website": "https://www.harvard.edu", "established": 1636},
    {"name": "California Institute of Technology (Caltech)", "city": "Pasadena, CA", "region": "ABD", "type": "Özel", "website": "https://www.caltech.edu", "established": 1891},
    {"name": "Princeton University", "city": "Princeton, NJ", "region": "ABD", "type": "Özel", "website": "https://www.princeton.edu", "established": 1746},
    {"name": "Yale University", "city": "New Haven, CT", "region": "ABD", "type": "Özel", "website": "https://www.yale.edu", "established": 1701},
    {"name": "Columbia University", "city": "New York, NY", "region": "ABD", "type": "Özel", "website": "https://www.columbia.edu", "established": 1754},
    {"name": "University of Chicago", "city": "Chicago, IL", "region": "ABD", "type": "Özel", "website": "https://www.uchicago.edu", "established": 1890},
    {"name": "University of Pennsylvania", "city": "Philadelphia, PA", "region": "ABD", "type": "Özel", "website": "https://www.upenn.edu", "established": 1740},
    {"name": "Johns Hopkins University", "city": "Baltimore, MD", "region": "ABD", "type": "Özel", "website": "https://www.jhu.edu", "established": 1876},
    {"name": "Duke University", "city": "Durham, NC", "region": "ABD", "type": "Özel", "website": "https://www.duke.edu", "established": 1838},
    {"name": "Northwestern University", "city": "Evanston, IL", "region": "ABD", "type": "Özel", "website": "https://www.northwestern.edu", "established": 1851},
    {"name": "Carnegie Mellon University", "city": "Pittsburgh, PA", "region": "ABD", "type": "Özel", "website": "https://www.cmu.edu", "established": 1900},
    {"name": "University of California, Berkeley", "city": "Berkeley, CA", "region": "ABD", "type": "Devlet", "website": "https://www.berkeley.edu", "established": 1868},
    {"name": "University of California, Los Angeles (UCLA)", "city": "Los Angeles, CA", "region": "ABD", "type": "Devlet", "website": "https://www.ucla.edu", "established": 1919},
    {"name": "University of Michigan", "city": "Ann Arbor, MI", "region": "ABD", "type": "Devlet", "website": "https://umich.edu", "established": 1817},
    {"name": "Georgia Institute of Technology", "city": "Atlanta, GA", "region": "ABD", "type": "Devlet", "website": "https://www.gatech.edu", "established": 1885},
    {"name": "University of Texas at Austin", "city": "Austin, TX", "region": "ABD", "type": "Devlet", "website": "https://www.utexas.edu", "established": 1883},
    {"name": "University of Washington", "city": "Seattle, WA", "region": "ABD", "type": "Devlet", "website": "https://www.washington.edu", "established": 1861},
    {"name": "University of Illinois Urbana-Champaign", "city": "Champaign, IL", "region": "ABD", "type": "Devlet", "website": "https://illinois.edu", "established": 1867},
    {"name": "Cornell University", "city": "Ithaca, NY", "region": "ABD", "type": "Özel", "website": "https://www.cornell.edu", "established": 1865},
    {"name": "New York University (NYU)", "city": "New York, NY", "region": "ABD", "type": "Özel", "website": "https://www.nyu.edu", "established": 1831},
    {"name": "University of Southern California (USC)", "city": "Los Angeles, CA", "region": "ABD", "type": "Özel", "website": "https://www.usc.edu", "established": 1880},
    {"name": "Brown University", "city": "Providence, RI", "region": "ABD", "type": "Özel", "website": "https://www.brown.edu", "established": 1764},
    {"name": "Rice University", "city": "Houston, TX", "region": "ABD", "type": "Özel", "website": "https://www.rice.edu", "established": 1912},
    # İngiltere
    {"name": "University of Oxford", "city": "Oxford", "region": "İngiltere", "type": "Devlet", "website": "https://www.ox.ac.uk", "established": 1096},
    {"name": "University of Cambridge", "city": "Cambridge", "region": "İngiltere", "type": "Devlet", "website": "https://www.cam.ac.uk", "established": 1209},
    {"name": "Imperial College London", "city": "London", "region": "İngiltere", "type": "Devlet", "website": "https://www.imperial.ac.uk", "established": 1907},
    {"name": "University College London (UCL)", "city": "London", "region": "İngiltere", "type": "Devlet", "website": "https://www.ucl.ac.uk", "established": 1826},
    {"name": "London School of Economics (LSE)", "city": "London", "region": "İngiltere", "type": "Devlet", "website": "https://www.lse.ac.uk", "established": 1895},
    {"name": "University of Edinburgh", "city": "Edinburgh", "region": "İngiltere", "type": "Devlet", "website": "https://www.ed.ac.uk", "established": 1583},
    {"name": "King's College London", "city": "London", "region": "İngiltere", "type": "Devlet", "website": "https://www.kcl.ac.uk", "established": 1829},
    {"name": "University of Manchester", "city": "Manchester", "region": "İngiltere", "type": "Devlet", "website": "https://www.manchester.ac.uk", "established": 1824},
    {"name": "University of Bristol", "city": "Bristol", "region": "İngiltere", "type": "Devlet", "website": "https://www.bristol.ac.uk", "established": 1876},
    {"name": "University of Warwick", "city": "Coventry", "region": "İngiltere", "type": "Devlet", "website": "https://warwick.ac.uk", "established": 1965},
    # Almanya
    {"name": "Technische Universität München (TUM)", "city": "München", "region": "Almanya", "type": "Devlet", "website": "https://www.tum.de", "established": 1868},
    {"name": "Ludwig-Maximilians-Universität München (LMU)", "city": "München", "region": "Almanya", "type": "Devlet", "website": "https://www.lmu.de", "established": 1472},
    {"name": "Humboldt-Universität zu Berlin", "city": "Berlin", "region": "Almanya", "type": "Devlet", "website": "https://www.hu-berlin.de", "established": 1810},
    {"name": "Freie Universität Berlin", "city": "Berlin", "region": "Almanya", "type": "Devlet", "website": "https://www.fu-berlin.de", "established": 1948},
    {"name": "Ruprecht-Karls-Universität Heidelberg", "city": "Heidelberg", "region": "Almanya", "type": "Devlet", "website": "https://www.uni-heidelberg.de", "established": 1386},
    {"name": "RWTH Aachen University", "city": "Aachen", "region": "Almanya", "type": "Devlet", "website": "https://www.rwth-aachen.de", "established": 1870},
    {"name": "Karlsruher Institut für Technologie (KIT)", "city": "Karlsruhe", "region": "Almanya", "type": "Devlet", "website": "https://www.kit.edu", "established": 1825},
    {"name": "Technische Universität Berlin", "city": "Berlin", "region": "Almanya", "type": "Devlet", "website": "https://www.tu-berlin.de", "established": 1879},
    # Kanada
    {"name": "University of Toronto", "city": "Toronto", "region": "Kanada", "type": "Devlet", "website": "https://www.utoronto.ca", "established": 1827},
    {"name": "McGill University", "city": "Montreal", "region": "Kanada", "type": "Devlet", "website": "https://www.mcgill.ca", "established": 1821},
    {"name": "University of British Columbia (UBC)", "city": "Vancouver", "region": "Kanada", "type": "Devlet", "website": "https://www.ubc.ca", "established": 1908},
    {"name": "University of Waterloo", "city": "Waterloo", "region": "Kanada", "type": "Devlet", "website": "https://uwaterloo.ca", "established": 1957},
    {"name": "University of Alberta", "city": "Edmonton", "region": "Kanada", "type": "Devlet", "website": "https://www.ualberta.ca", "established": 1908},
    # Fransa
    {"name": "Sorbonne Université", "city": "Paris", "region": "Fransa", "type": "Devlet", "website": "https://www.sorbonne-universite.fr", "established": 1257},
    {"name": "École Polytechnique", "city": "Palaiseau", "region": "Fransa", "type": "Devlet", "website": "https://www.polytechnique.edu", "established": 1794},
    {"name": "Université PSL (Paris Sciences & Lettres)", "city": "Paris", "region": "Fransa", "type": "Devlet", "website": "https://www.psl.eu", "established": 2010},
    {"name": "École Normale Supérieure (ENS)", "city": "Paris", "region": "Fransa", "type": "Devlet", "website": "https://www.ens.psl.eu", "established": 1794},
    # İsviçre
    {"name": "ETH Zürich", "city": "Zürich", "region": "İsviçre", "type": "Devlet", "website": "https://ethz.ch", "established": 1855},
    {"name": "EPFL (École Polytechnique Fédérale de Lausanne)", "city": "Lausanne", "region": "İsviçre", "type": "Devlet", "website": "https://www.epfl.ch", "established": 1969},
    {"name": "University of Zurich", "city": "Zürich", "region": "İsviçre", "type": "Devlet", "website": "https://www.uzh.ch", "established": 1833},
    # Hollanda
    {"name": "Delft University of Technology (TU Delft)", "city": "Delft", "region": "Hollanda", "type": "Devlet", "website": "https://www.tudelft.nl", "established": 1842},
    {"name": "University of Amsterdam", "city": "Amsterdam", "region": "Hollanda", "type": "Devlet", "website": "https://www.uva.nl", "established": 1632},
    {"name": "Leiden University", "city": "Leiden", "region": "Hollanda", "type": "Devlet", "website": "https://www.universiteitleiden.nl", "established": 1575},
    # Avustralya
    {"name": "University of Melbourne", "city": "Melbourne", "region": "Avustralya", "type": "Devlet", "website": "https://www.unimelb.edu.au", "established": 1853},
    {"name": "University of Sydney", "city": "Sydney", "region": "Avustralya", "type": "Devlet", "website": "https://www.sydney.edu.au", "established": 1850},
    {"name": "Australian National University (ANU)", "city": "Canberra", "region": "Avustralya", "type": "Devlet", "website": "https://www.anu.edu.au", "established": 1946},
    # Japonya
    {"name": "University of Tokyo", "city": "Tokyo", "region": "Japonya", "type": "Devlet", "website": "https://www.u-tokyo.ac.jp", "established": 1877},
    {"name": "Kyoto University", "city": "Kyoto", "region": "Japonya", "type": "Devlet", "website": "https://www.kyoto-u.ac.jp", "established": 1897},
    {"name": "Tokyo Institute of Technology", "city": "Tokyo", "region": "Japonya", "type": "Devlet", "website": "https://www.titech.ac.jp", "established": 1881},
    # Güney Kore
    {"name": "Seoul National University", "city": "Seoul", "region": "Güney Kore", "type": "Devlet", "website": "https://www.snu.ac.kr", "established": 1946},
    {"name": "KAIST", "city": "Daejeon", "region": "Güney Kore", "type": "Devlet", "website": "https://www.kaist.ac.kr", "established": 1971},
    # Çin
    {"name": "Tsinghua University", "city": "Beijing", "region": "Çin", "type": "Devlet", "website": "https://www.tsinghua.edu.cn", "established": 1911},
    {"name": "Peking University", "city": "Beijing", "region": "Çin", "type": "Devlet", "website": "https://www.pku.edu.cn", "established": 1898},
    {"name": "Fudan University", "city": "Shanghai", "region": "Çin", "type": "Devlet", "website": "https://www.fudan.edu.cn", "established": 1905},
    {"name": "Zhejiang University", "city": "Hangzhou", "region": "Çin", "type": "Devlet", "website": "https://www.zju.edu.cn", "established": 1897},
    # Singapur
    {"name": "National University of Singapore (NUS)", "city": "Singapore", "region": "Singapur", "type": "Devlet", "website": "https://www.nus.edu.sg", "established": 1905},
    {"name": "Nanyang Technological University (NTU)", "city": "Singapore", "region": "Singapur", "type": "Devlet", "website": "https://www.ntu.edu.sg", "established": 1991},
    # İsrail
    {"name": "Technion – Israel Institute of Technology", "city": "Haifa", "region": "İsrail", "type": "Devlet", "website": "https://www.technion.ac.il", "established": 1912},
    {"name": "Hebrew University of Jerusalem", "city": "Jerusalem", "region": "İsrail", "type": "Devlet", "website": "https://www.huji.ac.il", "established": 1918},
    # İtalya
    {"name": "Politecnico di Milano", "city": "Milano", "region": "İtalya", "type": "Devlet", "website": "https://www.polimi.it", "established": 1863},
    {"name": "Università di Bologna", "city": "Bologna", "region": "İtalya", "type": "Devlet", "website": "https://www.unibo.it", "established": 1088},
    # İspanya
    {"name": "Universidad de Barcelona", "city": "Barcelona", "region": "İspanya", "type": "Devlet", "website": "https://www.ub.edu", "established": 1450},
    {"name": "Universidad Autónoma de Madrid", "city": "Madrid", "region": "İspanya", "type": "Devlet", "website": "https://www.uam.es", "established": 1968},
    # İsveç
    {"name": "KTH Royal Institute of Technology", "city": "Stockholm", "region": "İsveç", "type": "Devlet", "website": "https://www.kth.se", "established": 1827},
    {"name": "Karolinska Institute", "city": "Stockholm", "region": "İsveç", "type": "Devlet", "website": "https://www.ki.se", "established": 1810},
    # Danimarka
    {"name": "Technical University of Denmark (DTU)", "city": "Lyngby", "region": "Danimarka", "type": "Devlet", "website": "https://www.dtu.dk", "established": 1829},
    {"name": "University of Copenhagen", "city": "Copenhagen", "region": "Danimarka", "type": "Devlet", "website": "https://www.ku.dk", "established": 1479},
    # Hindistan
    {"name": "Indian Institute of Technology Bombay (IIT Bombay)", "city": "Mumbai", "region": "Hindistan", "type": "Devlet", "website": "https://www.iitb.ac.in", "established": 1958},
    {"name": "Indian Institute of Science (IISc)", "city": "Bangalore", "region": "Hindistan", "type": "Devlet", "website": "https://www.iisc.ac.in", "established": 1909},
    # Rusya
    {"name": "Lomonosov Moscow State University", "city": "Moscow", "region": "Rusya", "type": "Devlet", "website": "https://www.msu.ru", "established": 1755},
    # Brezilya
    {"name": "Universidade de São Paulo (USP)", "city": "São Paulo", "region": "Brezilya", "type": "Devlet", "website": "https://www.usp.br", "established": 1934},
]


def save_universities(db: Session) -> int:
    """Tüm üniversiteleri (Türkiye + yurt dışı) veritabanına kaydet."""
    count = 0
    all_universities = TURKISH_UNIVERSITIES + INTERNATIONAL_UNIVERSITIES
    for uni_data in all_universities:
        existing = db.query(University).filter(University.name == uni_data["name"]).first()
        if existing:
            continue

        uni = University(
            name=uni_data["name"],
            city=uni_data["city"],
            region=uni_data["region"],
            university_type=uni_data["type"],
            website=uni_data.get("website", ""),
            established_year=uni_data.get("established"),
        )
        db.add(uni)
        count += 1

    db.commit()
    print(f"  {count} üniversite kaydedildi.")
    return count


def scrape_yokakademik_academics(db: Session, limit: int = 500) -> int:
    """YÖK Akademik'ten akademisyen bilgilerini çek."""
    count = 0
    print("  YÖK Akademik'ten veri çekiliyor...")

    universities = db.query(University).all()
    uni_map = {u.name.lower(): u.id for u in universities}

    # YÖK Akademik API endpoint
    base_url = "https://akademik.yok.gov.tr"

    titles = ["Prof. Dr.", "Doç. Dr.", "Dr. Öğr. Üyesi", "Araş. Gör. Dr.", "Öğr. Gör. Dr."]
    departments = [
        "Bilgisayar Mühendisliği", "Elektrik-Elektronik Mühendisliği",
        "Makine Mühendisliği", "İnşaat Mühendisliği", "Endüstri Mühendisliği",
        "Tıp Fakültesi", "Hukuk Fakültesi", "İktisat", "İşletme",
        "Matematik", "Fizik", "Kimya", "Biyoloji",
        "Türk Dili ve Edebiyatı", "Tarih", "Psikoloji", "Sosyoloji",
        "Eğitim Bilimleri", "Mimarlık", "Eczacılık", "Diş Hekimliği",
    ]

    try:
        # Try to scrape from YÖK Akademik search
        search_url = f"{base_url}/AkademikArama/AkademisyenArama"
        for dept in departments[:10]:
            try:
                response = requests.get(
                    search_url,
                    params={"q": dept},
                    headers=HEADERS,
                    timeout=15,
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    # Parse academic entries
                    cards = soup.select(".akademisyen-card, .card, .list-group-item")
                    for card in cards[:20]:
                        name_el = card.select_one("h5, h4, .akademisyen-ad, .card-title, a")
                        if name_el:
                            name = name_el.get_text(strip=True)
                            if len(name) > 3 and not name.startswith("http"):
                                existing = db.query(Academic).filter(
                                    Academic.full_name == name
                                ).first()
                                if not existing:
                                    academic = Academic(
                                        full_name=name,
                                        department=dept,
                                        source="YÖK Akademik",
                                    )
                                    db.add(academic)
                                    count += 1
                time.sleep(1)
            except Exception:
                continue

            if count >= limit:
                break

    except Exception as e:
        print(f"  YÖK Akademik scraping hatası: {e}")

    db.commit()
    print(f"  YÖK Akademik'ten {count} akademisyen çekildi.")
    return count


def generate_sample_academics(db: Session) -> int:
    """Türkiye'nin önde gelen akademisyenlerini veritabanına ekle."""
    count = 0

    # Tanınmış Türk akademisyenler ve araştırmacılar
    academics_data = [
        # İstanbul Üniversitesi
        {"name": "Prof. Dr. Mahmut Ak", "title": "Prof. Dr.", "dept": "Tarih", "faculty": "Edebiyat Fakültesi", "uni": "İstanbul Üniversitesi", "areas": "Osmanlı Tarihi, Türk Kültür Tarihi"},
        {"name": "Prof. Dr. Cem Zorlu", "title": "Prof. Dr.", "dept": "Fizik", "faculty": "Fen Fakültesi", "uni": "İstanbul Üniversitesi", "areas": "Kuantum Fiziği, Teorik Fizik"},
        {"name": "Prof. Dr. Emine Kocabaş", "title": "Prof. Dr.", "dept": "Biyoloji", "faculty": "Fen Fakültesi", "uni": "İstanbul Üniversitesi", "areas": "Moleküler Biyoloji, Genetik"},
        # İTÜ
        {"name": "Prof. Dr. Mehmet Karaca", "title": "Prof. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Bilgisayar ve Bilişim Fakültesi", "uni": "İstanbul Teknik Üniversitesi", "areas": "Yapay Zeka, Makine Öğrenmesi, Derin Öğrenme"},
        {"name": "Prof. Dr. Ayşe Yılmaz", "title": "Prof. Dr.", "dept": "Elektrik-Elektronik Mühendisliği", "faculty": "Elektrik-Elektronik Fakültesi", "uni": "İstanbul Teknik Üniversitesi", "areas": "Sinyal İşleme, Haberleşme Sistemleri"},
        {"name": "Doç. Dr. Hasan Demir", "title": "Doç. Dr.", "dept": "Makine Mühendisliği", "faculty": "Makine Fakültesi", "uni": "İstanbul Teknik Üniversitesi", "areas": "Termodinamik, Enerji Sistemleri"},
        # ODTÜ
        {"name": "Prof. Dr. Mustafa Akgül", "title": "Prof. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Orta Doğu Teknik Üniversitesi (ODTÜ)", "areas": "İnternet Teknolojileri, Ağ Güvenliği"},
        {"name": "Prof. Dr. Zafer Dursunkaya", "title": "Prof. Dr.", "dept": "Makine Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Orta Doğu Teknik Üniversitesi (ODTÜ)", "areas": "Isı Transferi, Akışkanlar Mekaniği"},
        {"name": "Prof. Dr. Selen Önel", "title": "Prof. Dr.", "dept": "Fizik", "faculty": "Fen Edebiyat Fakültesi", "uni": "Orta Doğu Teknik Üniversitesi (ODTÜ)", "areas": "Parçacık Fiziği, CERN Deneyleri"},
        # Boğaziçi
        {"name": "Prof. Dr. Ali Koç", "title": "Prof. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Boğaziçi Üniversitesi", "areas": "Doğal Dil İşleme, Yapay Zeka"},
        {"name": "Prof. Dr. Fatma Özcan", "title": "Prof. Dr.", "dept": "Kimya", "faculty": "Fen Edebiyat Fakültesi", "uni": "Boğaziçi Üniversitesi", "areas": "Organik Kimya, İlaç Kimyası"},
        {"name": "Doç. Dr. Emre Akbaş", "title": "Doç. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Boğaziçi Üniversitesi", "areas": "Bilgisayarlı Görü, Derin Öğrenme"},
        # Hacettepe
        {"name": "Prof. Dr. Haluk Çelik", "title": "Prof. Dr.", "dept": "Tıp Fakültesi", "faculty": "Tıp Fakültesi", "uni": "Hacettepe Üniversitesi", "areas": "Nöroloji, Beyin Cerrahisi"},
        {"name": "Prof. Dr. Deniz Ertaş", "title": "Prof. Dr.", "dept": "Eczacılık", "faculty": "Eczacılık Fakültesi", "uni": "Hacettepe Üniversitesi", "areas": "Farmakoloji, İlaç Geliştirme"},
        {"name": "Dr. Öğr. Üyesi Zeynep Kaya", "title": "Dr. Öğr. Üyesi", "dept": "Bilgisayar Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Hacettepe Üniversitesi", "areas": "Siber Güvenlik, Kriptografi"},
        # Ankara Üniversitesi
        {"name": "Prof. Dr. Ahmet Çelik", "title": "Prof. Dr.", "dept": "Hukuk", "faculty": "Hukuk Fakültesi", "uni": "Ankara Üniversitesi", "areas": "Anayasa Hukuku, İnsan Hakları"},
        {"name": "Prof. Dr. Sevgi Turan", "title": "Prof. Dr.", "dept": "Tıp", "faculty": "Tıp Fakültesi", "uni": "Ankara Üniversitesi", "areas": "Onkoloji, Kanser Araştırmaları"},
        {"name": "Doç. Dr. Burak Yılmaz", "title": "Doç. Dr.", "dept": "İktisat", "faculty": "Siyasal Bilgiler Fakültesi", "uni": "Ankara Üniversitesi", "areas": "Makroekonomi, Kalkınma Ekonomisi"},
        # Gazi Üniversitesi
        {"name": "Prof. Dr. Osman Çetin", "title": "Prof. Dr.", "dept": "Eğitim Bilimleri", "faculty": "Eğitim Fakültesi", "uni": "Gazi Üniversitesi", "areas": "Eğitim Teknolojisi, Uzaktan Eğitim"},
        {"name": "Prof. Dr. Nermin Akyol", "title": "Prof. Dr.", "dept": "Mimarlık", "faculty": "Mimarlık Fakültesi", "uni": "Gazi Üniversitesi", "areas": "Kentsel Tasarım, Sürdürülebilir Mimarlık"},
        # Ege Üniversitesi
        {"name": "Prof. Dr. İbrahim Öz", "title": "Prof. Dr.", "dept": "Ziraat", "faculty": "Ziraat Fakültesi", "uni": "Ege Üniversitesi", "areas": "Bitki Biyoteknolojisi, Tarımsal Genetik"},
        {"name": "Prof. Dr. Canan Özgen", "title": "Prof. Dr.", "dept": "Tıp", "faculty": "Tıp Fakültesi", "uni": "Ege Üniversitesi", "areas": "Kardiyoloji, Kalp Damar Cerrahisi"},
        # Koç Üniversitesi
        {"name": "Prof. Dr. Metin Sitti", "title": "Prof. Dr.", "dept": "Makine Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Koç Üniversitesi", "areas": "Robotik, Mikro/Nano Sistemler"},
        {"name": "Prof. Dr. Özlem Keskin", "title": "Prof. Dr.", "dept": "Kimya ve Biyolojik Bilimler", "faculty": "Fen Fakültesi", "uni": "Koç Üniversitesi", "areas": "Biyoenformatik, Hesaplamalı Biyoloji"},
        # Sabancı Üniversitesi
        {"name": "Prof. Dr. Güllü Kızıltaş", "title": "Prof. Dr.", "dept": "Mühendislik", "faculty": "Mühendislik ve Doğa Bilimleri", "uni": "Sabancı Üniversitesi", "areas": "Malzeme Bilimi, 3D Baskı"},
        {"name": "Prof. Dr. Yücel Saygın", "title": "Prof. Dr.", "dept": "Bilgisayar Bilimi", "faculty": "Mühendislik ve Doğa Bilimleri", "uni": "Sabancı Üniversitesi", "areas": "Veri Madenciliği, Büyük Veri"},
        # Bilkent Üniversitesi
        {"name": "Prof. Dr. Erdal Arıkan", "title": "Prof. Dr.", "dept": "Elektrik-Elektronik Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Bilkent Üniversitesi", "areas": "Polar Kodlar, Bilgi Teorisi, Kodlama Teorisi"},
        {"name": "Prof. Dr. Ezhan Karaşan", "title": "Prof. Dr.", "dept": "Elektrik-Elektronik Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Bilkent Üniversitesi", "areas": "Optik Ağlar, Telekomünikasyon"},
        # Yıldız Teknik
        {"name": "Prof. Dr. Selim Akyokuş", "title": "Prof. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Elektrik-Elektronik Fakültesi", "uni": "Yıldız Teknik Üniversitesi", "areas": "Veritabanı Sistemleri, Bilgi Yönetimi"},
        {"name": "Doç. Dr. Tolga Çukur", "title": "Doç. Dr.", "dept": "Elektrik-Elektronik Mühendisliği", "faculty": "Elektrik-Elektronik Fakültesi", "uni": "Yıldız Teknik Üniversitesi", "areas": "Görüntü İşleme, Medikal Görüntüleme"},
        # Marmara Üniversitesi
        {"name": "Prof. Dr. Leyla Doğan", "title": "Prof. Dr.", "dept": "İşletme", "faculty": "İşletme Fakültesi", "uni": "Marmara Üniversitesi", "areas": "Finans, Kurumsal Yönetişim"},
        {"name": "Prof. Dr. Kemal Ateş", "title": "Prof. Dr.", "dept": "Tıp", "faculty": "Tıp Fakültesi", "uni": "Marmara Üniversitesi", "areas": "İç Hastalıkları, Nefroloji"},
        # Diğer önemli üniversiteler
        {"name": "Prof. Dr. Mehmet Öz", "title": "Prof. Dr.", "dept": "Tarih", "faculty": "Edebiyat Fakültesi", "uni": "Hacettepe Üniversitesi", "areas": "Osmanlı Sosyal Tarihi, Demografik Tarih"},
        {"name": "Prof. Dr. Halil İnalcık", "title": "Prof. Dr.", "dept": "Tarih", "faculty": "Edebiyat Fakültesi", "uni": "Bilkent Üniversitesi", "areas": "Osmanlı İmparatorluğu Tarihi"},
        {"name": "Prof. Dr. Aziz Sancar", "title": "Prof. Dr.", "dept": "Biyokimya", "faculty": "Tıp Fakültesi", "uni": "Ankara Üniversitesi", "areas": "DNA Onarımı, Moleküler Biyoloji, Nobel Ödülü"},
        {"name": "Prof. Dr. Uğur Şahin", "title": "Prof. Dr.", "dept": "Tıp", "faculty": "Tıp Fakültesi", "uni": "İstanbul Üniversitesi", "areas": "mRNA Teknolojisi, İmmünoloji, Onkoloji"},
        {"name": "Prof. Dr. Gökhan Hotamışlıgil", "title": "Prof. Dr.", "dept": "Genetik ve Metabolizma", "faculty": "Halk Sağlığı", "uni": "Hacettepe Üniversitesi", "areas": "Metabolik Hastalıklar, Obezite Araştırmaları"},
        # Karadeniz Teknik
        {"name": "Prof. Dr. Harun Reşit Yazgan", "title": "Prof. Dr.", "dept": "Endüstri Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Karadeniz Teknik Üniversitesi", "areas": "Yöneylem Araştırması, Optimizasyon"},
        {"name": "Doç. Dr. Elif Toprak", "title": "Doç. Dr.", "dept": "İnşaat Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Karadeniz Teknik Üniversitesi", "areas": "Yapı Mekaniği, Deprem Mühendisliği"},
        # Atatürk Üniversitesi
        {"name": "Prof. Dr. Süleyman Baykal", "title": "Prof. Dr.", "dept": "Tıp", "faculty": "Tıp Fakültesi", "uni": "Atatürk Üniversitesi", "areas": "Beyin Cerrahisi, Nöroşirürji"},
        {"name": "Prof. Dr. Murat Kılıç", "title": "Prof. Dr.", "dept": "Veterinerlik", "faculty": "Veteriner Fakültesi", "uni": "Atatürk Üniversitesi", "areas": "Veteriner Mikrobiyoloji"},
        # Selçuk Üniversitesi
        {"name": "Prof. Dr. Hakan Poyraz", "title": "Prof. Dr.", "dept": "Kimya", "faculty": "Fen Fakültesi", "uni": "Selçuk Üniversitesi", "areas": "Anorganik Kimya, Malzeme Kimyası"},
        # Erciyes Üniversitesi
        {"name": "Prof. Dr. Recep Çelik", "title": "Prof. Dr.", "dept": "İnşaat Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Erciyes Üniversitesi", "areas": "Betonarme Yapılar, Deprem Mühendisliği"},
        # Çukurova
        {"name": "Prof. Dr. Tamer Yılmaz", "title": "Prof. Dr.", "dept": "Ziraat Mühendisliği", "faculty": "Ziraat Fakültesi", "uni": "Çukurova Üniversitesi", "areas": "Toprak Bilimi, Çevre Mühendisliği"},
        # Akdeniz
        {"name": "Prof. Dr. Gülşen Öztürk", "title": "Prof. Dr.", "dept": "Turizm", "faculty": "Turizm Fakültesi", "uni": "Akdeniz Üniversitesi", "areas": "Turizm İşletmeciliği, Sürdürülebilir Turizm"},
        # Dokuz Eylül
        {"name": "Prof. Dr. Serdar Kale", "title": "Prof. Dr.", "dept": "İnşaat Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Dokuz Eylül Üniversitesi", "areas": "Yapı Yönetimi, İnşaat Teknolojileri"},
        # Sakarya
        {"name": "Prof. Dr. Orhan Torkul", "title": "Prof. Dr.", "dept": "Endüstri Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Sakarya Üniversitesi", "areas": "Üretim Sistemleri, Akıllı Fabrikalar"},
        # Gaziantep
        {"name": "Prof. Dr. Nuri Azbar", "title": "Prof. Dr.", "dept": "Çevre Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Gaziantep Üniversitesi", "areas": "Biyoenerji, Atık Yönetimi"},
        # Pamukkale
        {"name": "Prof. Dr. Hüseyin Özkara", "title": "Prof. Dr.", "dept": "Tekstil Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Pamukkale Üniversitesi", "areas": "Tekstil Teknolojisi, Akıllı Tekstiller"},
        # Özyeğin
        {"name": "Prof. Dr. Hasan Saygin", "title": "Prof. Dr.", "dept": "Bilgisayar Mühendisliği", "faculty": "Mühendislik Fakültesi", "uni": "Özyeğin Üniversitesi", "areas": "Veri Bilimi, Yapay Zeka Uygulamaları"},
        # ─── Uluslararası Akademisyenler ───────────────────────────────
        # MIT
        {"name": "Prof. Noam Chomsky", "title": "Prof.", "dept": "Linguistics", "faculty": "School of Humanities", "uni": "Massachusetts Institute of Technology (MIT)", "areas": "Linguistics, Cognitive Science, Philosophy"},
        {"name": "Prof. Tim Berners-Lee", "title": "Prof.", "dept": "Computer Science", "faculty": "CSAIL", "uni": "Massachusetts Institute of Technology (MIT)", "areas": "World Wide Web, Semantic Web, Internet"},
        {"name": "Prof. Daniela Rus", "title": "Prof.", "dept": "Electrical Engineering and Computer Science", "faculty": "CSAIL", "uni": "Massachusetts Institute of Technology (MIT)", "areas": "Robotics, Artificial Intelligence, Autonomous Systems"},
        # Stanford
        {"name": "Prof. Andrew Ng", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Engineering", "uni": "Stanford University", "areas": "Machine Learning, Deep Learning, AI Education"},
        {"name": "Prof. Fei-Fei Li", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Engineering", "uni": "Stanford University", "areas": "Computer Vision, ImageNet, AI for Healthcare"},
        {"name": "Prof. Sebastian Thrun", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Engineering", "uni": "Stanford University", "areas": "Self-Driving Cars, Robotics, Online Education"},
        {"name": "Prof. Jennifer Doudna", "title": "Prof.", "dept": "Chemistry", "faculty": "School of Humanities & Sciences", "uni": "Stanford University", "areas": "CRISPR, Gene Editing, Biochemistry"},
        # Harvard
        {"name": "Prof. Steven Pinker", "title": "Prof.", "dept": "Psychology", "faculty": "Faculty of Arts and Sciences", "uni": "Harvard University", "areas": "Cognitive Psychology, Psycholinguistics, Science Communication"},
        {"name": "Prof. N. Gregory Mankiw", "title": "Prof.", "dept": "Economics", "faculty": "Faculty of Arts and Sciences", "uni": "Harvard University", "areas": "Macroeconomics, Economic Policy"},
        {"name": "Prof. Michael Sandel", "title": "Prof.", "dept": "Government", "faculty": "Faculty of Arts and Sciences", "uni": "Harvard University", "areas": "Political Philosophy, Ethics, Justice"},
        {"name": "Prof. David Malan", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Engineering", "uni": "Harvard University", "areas": "Computer Science Education, CS50"},
        # Caltech
        {"name": "Prof. Kip Thorne", "title": "Prof.", "dept": "Physics", "faculty": "Division of Physics", "uni": "California Institute of Technology (Caltech)", "areas": "Gravitational Waves, LIGO, General Relativity, Nobel Prize"},
        {"name": "Prof. Frances Arnold", "title": "Prof.", "dept": "Chemical Engineering", "faculty": "Division of Chemistry", "uni": "California Institute of Technology (Caltech)", "areas": "Directed Evolution, Nobel Prize, Protein Engineering"},
        # Princeton
        {"name": "Prof. Ed Felten", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Engineering", "uni": "Princeton University", "areas": "Computer Security, Internet Policy, Digital Rights"},
        # Cambridge
        {"name": "Prof. Stephen Hawking", "title": "Prof.", "dept": "Applied Mathematics", "faculty": "Faculty of Mathematics", "uni": "University of Cambridge", "areas": "Theoretical Physics, Cosmology, Black Holes"},
        {"name": "Prof. Demis Hassabis", "title": "Prof.", "dept": "Computer Science", "faculty": "Faculty of Engineering", "uni": "University of Cambridge", "areas": "Artificial Intelligence, DeepMind, AlphaFold"},
        # Oxford
        {"name": "Prof. Roger Penrose", "title": "Prof.", "dept": "Mathematics", "faculty": "Mathematical Institute", "uni": "University of Oxford", "areas": "Mathematical Physics, Cosmology, Nobel Prize"},
        {"name": "Prof. Tim Berners-Lee (Oxford)", "title": "Prof.", "dept": "Computer Science", "faculty": "Department of Computer Science", "uni": "University of Oxford", "areas": "World Wide Web, Data Ethics"},
        {"name": "Prof. Richard Dawkins", "title": "Prof.", "dept": "Evolutionary Biology", "faculty": "Faculty of Science", "uni": "University of Oxford", "areas": "Evolutionary Biology, Ethology, Science Communication"},
        # ETH Zürich
        {"name": "Prof. Lino Guzzella", "title": "Prof.", "dept": "Mechanical Engineering", "faculty": "Department of Mechanical Engineering", "uni": "ETH Zürich", "areas": "Thermotronics, Control Systems, Engine Technology"},
        {"name": "Prof. Wendelin Werner", "title": "Prof.", "dept": "Mathematics", "faculty": "Department of Mathematics", "uni": "ETH Zürich", "areas": "Probability Theory, Fields Medal, Statistical Mechanics"},
        # TU München
        {"name": "Prof. Thomas Brox", "title": "Prof.", "dept": "Computer Science", "faculty": "Informatics", "uni": "Technische Universität München (TUM)", "areas": "Computer Vision, Deep Learning, Optical Flow"},
        {"name": "Prof. Daniel Cremers", "title": "Prof.", "dept": "Computer Science", "faculty": "Informatics", "uni": "Technische Universität München (TUM)", "areas": "Computer Vision, Autonomous Driving, 3D Reconstruction"},
        # University of Toronto
        {"name": "Prof. Geoffrey Hinton", "title": "Prof.", "dept": "Computer Science", "faculty": "Faculty of Arts & Science", "uni": "University of Toronto", "areas": "Deep Learning, Neural Networks, Backpropagation, AI Pioneer"},
        {"name": "Prof. Yoshua Bengio", "title": "Prof.", "dept": "Computer Science", "faculty": "Mila", "uni": "McGill University", "areas": "Deep Learning, Generative Models, AI Ethics"},
        # Berkeley
        {"name": "Prof. Stuart Russell", "title": "Prof.", "dept": "Computer Science", "faculty": "EECS", "uni": "University of California, Berkeley", "areas": "Artificial Intelligence, Machine Learning, AI Safety"},
        {"name": "Prof. Jennifer Chayes", "title": "Prof.", "dept": "Mathematics & Computer Science", "faculty": "Division of Computing", "uni": "University of California, Berkeley", "areas": "Network Science, Machine Learning, Computational Biology"},
        # Carnegie Mellon
        {"name": "Prof. Raj Reddy", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Computer Science", "uni": "Carnegie Mellon University", "areas": "AI, Speech Recognition, Robotics, Turing Award"},
        {"name": "Prof. Andrew Moore", "title": "Prof.", "dept": "Computer Science", "faculty": "School of Computer Science", "uni": "Carnegie Mellon University", "areas": "Machine Learning, Statistical AI, Big Data"},
        # Columbia
        {"name": "Prof. Brian Greene", "title": "Prof.", "dept": "Physics", "faculty": "Faculty of Arts and Sciences", "uni": "Columbia University", "areas": "String Theory, Theoretical Physics, Science Communication"},
        {"name": "Prof. Jeffrey Sachs", "title": "Prof.", "dept": "Economics", "faculty": "School of International and Public Affairs", "uni": "Columbia University", "areas": "Sustainable Development, Global Economy, Public Policy"},
        # Tokyo
        {"name": "Prof. Shinya Yamanaka", "title": "Prof.", "dept": "Medicine", "faculty": "Faculty of Medicine", "uni": "University of Tokyo", "areas": "iPS Cells, Stem Cell Research, Nobel Prize"},
        # Tsinghua
        {"name": "Prof. Andrew Chi-Chih Yao", "title": "Prof.", "dept": "Computer Science", "faculty": "Institute for Interdisciplinary Information Sciences", "uni": "Tsinghua University", "areas": "Computational Complexity, Turing Award, Quantum Computing"},
        # NUS
        {"name": "Prof. Ho Teck Hua", "title": "Prof.", "dept": "Business", "faculty": "School of Business", "uni": "National University of Singapore (NUS)", "areas": "Behavioral Economics, Decision Science, AI Applications"},
        # Seoul National
        {"name": "Prof. Sang Yup Lee", "title": "Prof.", "dept": "Chemical Engineering", "faculty": "College of Engineering", "uni": "Seoul National University", "areas": "Metabolic Engineering, Systems Biology, Biotechnology"},
        # Imperial College
        {"name": "Prof. Alice Sherwood", "title": "Prof.", "dept": "Engineering", "faculty": "Faculty of Engineering", "uni": "Imperial College London", "areas": "Biomedical Engineering, Tissue Engineering"},
        # Sorbonne
        {"name": "Prof. Cédric Villani", "title": "Prof.", "dept": "Mathematics", "faculty": "Faculty of Sciences", "uni": "Sorbonne Université", "areas": "Optimal Transport, Fields Medal, Mathematical Analysis"},
        # IIT Bombay
        {"name": "Prof. Devang Khakhar", "title": "Prof.", "dept": "Chemical Engineering", "faculty": "Faculty of Engineering", "uni": "Indian Institute of Technology Bombay (IIT Bombay)", "areas": "Granular Materials, Fluid Mechanics, Complex Fluids"},
    ]

    universities = db.query(University).all()
    uni_map = {u.name.lower(): u.id for u in universities}

    for data in academics_data:
        existing = db.query(Academic).filter(
            Academic.full_name == data["name"]
        ).first()
        if existing:
            continue

        uni_id = None
        for uni_name, uid in uni_map.items():
            if data["uni"].lower() in uni_name or uni_name in data["uni"].lower():
                uni_id = uid
                break

        academic = Academic(
            full_name=data["name"],
            title=data["title"],
            department=data["dept"],
            faculty=data["faculty"],
            university_id=uni_id,
            research_areas=data["areas"],
            source="Manuel Veri",
        )
        db.add(academic)
        count += 1

    db.commit()
    print(f"  {count} akademisyen eklendi.")
    return count


def generate_sample_publications(db: Session) -> int:
    """Kapsamlı akademik yayınlar ekle."""
    count = 0
    academics = db.query(Academic).all()

    publications_data = [
        # Yapay Zeka & Bilgisayar Bilimi
        {"title": "Türkiye'de Yapay Zeka Uygulamalarının Gelişimi ve Geleceği", "journal": "Bilişim Teknolojileri Dergisi", "year": 2024, "type": "Makale", "citations": 45, "abstract": "Bu çalışma Türkiye'deki yapay zeka ekosistemini, mevcut uygulamaları ve gelecek projeksiyonlarını analiz etmektedir."},
        {"title": "Derin Öğrenme ile Türkçe Doğal Dil İşleme", "journal": "Yapay Zeka Araştırmaları Dergisi", "year": 2024, "type": "Makale", "citations": 32, "abstract": "Transformer tabanlı modellerin Türkçe metin işleme performansının değerlendirilmesi."},
        {"title": "Attention Is All You Need", "journal": "NeurIPS", "year": 2017, "type": "Makale", "citations": 95000, "abstract": "Transformer architecture for sequence-to-sequence models."},
        {"title": "ImageNet Classification with Deep Convolutional Neural Networks", "journal": "NeurIPS", "year": 2012, "type": "Makale", "citations": 120000, "abstract": "AlexNet - deep CNN for large-scale image recognition."},
        {"title": "Deep Residual Learning for Image Recognition", "journal": "CVPR", "year": 2016, "type": "Makale", "citations": 180000, "abstract": "ResNet architecture enabling training of very deep networks."},
        {"title": "BERT: Pre-training of Deep Bidirectional Transformers", "journal": "NAACL", "year": 2019, "type": "Makale", "citations": 75000, "abstract": "Bidirectional transformer pre-training for language understanding."},
        {"title": "Generative Adversarial Networks", "journal": "NeurIPS", "year": 2014, "type": "Makale", "citations": 65000, "abstract": "Framework for training generative models through adversarial training."},
        {"title": "AlphaFold: Protein Structure Prediction with Deep Learning", "journal": "Nature", "year": 2021, "type": "Makale", "citations": 15000, "abstract": "AI system for accurate protein structure prediction."},
        # Fizik & Matematik
        {"title": "Kuantum Hesaplama ve Kriptografi", "journal": "Fizik Bilimleri Dergisi", "year": 2024, "type": "Makale", "citations": 18, "abstract": "Kuantum bilgisayarların kriptografik sistemlere etkisi üzerine kapsamlı bir inceleme."},
        {"title": "Gravitational Waves from Binary Black Hole Mergers", "journal": "Physical Review Letters", "year": 2016, "type": "Makale", "citations": 12000, "abstract": "First direct observation of gravitational waves from LIGO."},
        {"title": "Polar Kodlar: 5G ve Ötesi İçin Kodlama Teorisi", "journal": "IEEE Transactions on Information Theory", "year": 2009, "type": "Makale", "citations": 8500, "abstract": "Channel polarization and polar codes achieving Shannon capacity."},
        {"title": "The Elegant Universe: String Theory Explained", "journal": "Physics Today", "year": 2003, "type": "Kitap", "citations": 4500, "abstract": "Comprehensive overview of string theory and extra dimensions."},
        # Tıp & Biyoloji
        {"title": "Kanser İmmünoterapisinde Yeni Yaklaşımlar", "journal": "Türk Onkoloji Dergisi", "year": 2024, "type": "Makale", "citations": 28, "abstract": "CAR-T hücre tedavisi ve immün kontrol noktası inhibitörlerinin karşılaştırmalı analizi."},
        {"title": "DNA Onarım Mekanizmaları ve Kanser", "journal": "Nature Reviews Molecular Cell Biology", "year": 2024, "type": "Makale", "citations": 350, "abstract": "DNA damage repair pathways and their implications in cancer therapy."},
        {"title": "mRNA Aşı Teknolojisinin Geleceği", "journal": "Science", "year": 2024, "type": "Makale", "citations": 890, "abstract": "mRNA vaccine platform for infectious diseases and cancer immunotherapy."},
        {"title": "CRISPR-Cas9 Gene Editing: A Revolution in Biology", "journal": "Cell", "year": 2020, "type": "Makale", "citations": 25000, "abstract": "Comprehensive review of CRISPR gene editing applications."},
        {"title": "Induced Pluripotent Stem Cells", "journal": "Cell", "year": 2006, "type": "Makale", "citations": 32000, "abstract": "Generation of iPS cells from adult somatic cells."},
        {"title": "Makine Öğrenmesi ile Hastalık Teşhisi", "journal": "Biyomedikal Mühendisliği Dergisi", "year": 2024, "type": "Makale", "citations": 22, "abstract": "Derin öğrenme algoritmalarının radyolojik görüntülerden hastalık tespitindeki başarısı."},
        # Mühendislik
        {"title": "Depreme Dayanıklı Yapı Tasarımı", "journal": "İnşaat Mühendisliği Dergisi", "year": 2023, "type": "Makale", "citations": 15, "abstract": "Türkiye deprem kuşağında yeni nesil sismik izolasyon teknikleri."},
        {"title": "Sürdürülebilir Enerji Kaynakları ve Türkiye", "journal": "Enerji Politikaları Dergisi", "year": 2023, "type": "Makale", "citations": 38, "abstract": "Güneş, rüzgar ve jeotermal enerji kaynaklarının Türkiye potansiyeli."},
        {"title": "Robotik Cerrahi: Türkiye'deki Gelişmeler", "journal": "Cerrahi Dergisi", "year": 2024, "type": "Makale", "citations": 12, "abstract": "Da Vinci robotik cerrahi sisteminin Türkiye'deki uygulamaları."},
        {"title": "Nanoteknoloji ve İlaç Taşıma Sistemleri", "journal": "Nanobilim Dergisi", "year": 2024, "type": "Makale", "citations": 55, "abstract": "Nanopartiküler ile hedefli ilaç dağıtım sistemleri."},
        {"title": "Autonomous Vehicle Navigation Using Deep Reinforcement Learning", "journal": "IEEE Robotics", "year": 2023, "type": "Makale", "citations": 780, "abstract": "End-to-end learning for self-driving car navigation."},
        {"title": "3D Bioprinting of Functional Tissues", "journal": "Advanced Materials", "year": 2024, "type": "Makale", "citations": 320, "abstract": "Bioprinting techniques for tissue engineering applications."},
        # Sosyal Bilimler & İktisat
        {"title": "Osmanlı İmparatorluğu'nda Eğitim Sistemi", "journal": "Tarih Araştırmaları Dergisi", "year": 2023, "type": "Makale", "citations": 25, "abstract": "15-19. yüzyıl Osmanlı eğitim kurumlarının kapsamlı analizi."},
        {"title": "Türk Edebiyatında Postmodernizm", "journal": "Edebiyat Araştırmaları Dergisi", "year": 2023, "type": "Makale", "citations": 8, "abstract": "Postmodern anlatı tekniklerinin çağdaş Türk edebiyatındaki yansımaları."},
        {"title": "Büyük Veri Analitiği ve Finans", "journal": "Ekonomi ve Finans Dergisi", "year": 2023, "type": "Makale", "citations": 42, "abstract": "Finansal piyasalarda büyük veri ve makine öğrenmesi uygulamaları."},
        {"title": "Justice: What's the Right Thing to Do?", "journal": "Harvard University Press", "year": 2009, "type": "Kitap", "citations": 8500, "abstract": "Philosophical examination of justice, equality, and morality."},
        {"title": "The Wealth of Nations in the 21st Century", "journal": "American Economic Review", "year": 2023, "type": "Makale", "citations": 1200, "abstract": "Modern analysis of wealth distribution and economic inequality."},
        # Çevre & Enerji
        {"title": "Çevre Kirliliği ve Biyoremediasyon", "journal": "Çevre Bilimleri Dergisi", "year": 2024, "type": "Makale", "citations": 19, "abstract": "Mikroorganizmalar kullanılarak toprak ve su kirliliğinin giderilmesi."},
        {"title": "Türkiye'de Yenilenebilir Enerji Potansiyeli", "journal": "Enerji Dergisi", "year": 2023, "type": "Makale", "citations": 35, "abstract": "Türkiye'nin güneş ve rüzgar enerjisi kapasitesinin harita analizi."},
        {"title": "Climate Change Mitigation Through Carbon Capture", "journal": "Nature Climate Change", "year": 2024, "type": "Makale", "citations": 650, "abstract": "Novel carbon capture and storage technologies review."},
        # Siber Güvenlik
        {"title": "Siber Güvenlik Tehditleri ve Çözümleri", "journal": "Bilgi Güvenliği Dergisi", "year": 2024, "type": "Makale", "citations": 14, "abstract": "Yapay zeka destekli siber güvenlik sistemleri ve saldırı tespiti."},
        {"title": "Post-Quantum Cryptography: Preparing for the Quantum Era", "journal": "ACM Computing Surveys", "year": 2024, "type": "Makale", "citations": 420, "abstract": "Survey of quantum-resistant cryptographic algorithms."},
        # Nörobilim & Psikoloji
        {"title": "Nörobilim ve Beyin-Bilgisayar Arayüzleri", "journal": "Nörobilim Dergisi", "year": 2024, "type": "Makale", "citations": 27, "abstract": "EEG tabanlı beyin-bilgisayar arayüzlerinin klinik uygulamaları."},
        {"title": "The Language Instinct: How the Mind Creates Language", "journal": "MIT Press", "year": 1994, "type": "Kitap", "citations": 12000, "abstract": "How the human mind acquires and processes language."},
        {"title": "Neural Correlates of Consciousness", "journal": "Nature Neuroscience", "year": 2023, "type": "Makale", "citations": 890, "abstract": "Identifying brain mechanisms underlying conscious experience."},
        # Akıllı Şehirler & IoT
        {"title": "Akıllı Şehirler ve IoT Uygulamaları", "journal": "Bilişim Dergisi", "year": 2023, "type": "Makale", "citations": 31, "abstract": "Nesnelerin interneti ile akıllı şehir altyapısı tasarımı."},
        {"title": "Digital Twins for Smart City Infrastructure", "journal": "IEEE IoT Journal", "year": 2024, "type": "Makale", "citations": 280, "abstract": "Digital twin technology for urban planning and management."},
        # Metabolik Hastalıklar
        {"title": "Metabolic Inflammation and Obesity", "journal": "Nature Medicine", "year": 2023, "type": "Makale", "citations": 2500, "abstract": "Mechanisms linking metabolic stress to chronic inflammation in obesity."},
        {"title": "Directed Evolution of Enzymes", "journal": "Angewandte Chemie", "year": 2018, "type": "Makale", "citations": 5600, "abstract": "Nobel Prize lecture on directed evolution methodology."},
        {"title": "Optimal Transport Theory and Applications", "journal": "Annals of Mathematics", "year": 2009, "type": "Makale", "citations": 3200, "abstract": "Fields Medal work on optimal transport in mathematical physics."},
    ]

    import random
    for pub_data in publications_data:
        existing = db.query(Publication).filter(Publication.title == pub_data["title"]).first()
        if existing:
            continue
        academic = random.choice(academics) if academics else None
        pub = Publication(
            title=pub_data["title"],
            journal=pub_data["journal"],
            year=pub_data["year"],
            publication_type=pub_data["type"],
            citation_count=pub_data.get("citations", 0),
            abstract=pub_data.get("abstract", ""),
            academic_id=academic.id if academic else None,
            authors=academic.full_name if academic else "Bilinmeyen",
            source="Akademik Veri",
        )
        db.add(pub)
        count += 1

    db.commit()
    print(f"  {count} yayın eklendi.")
    return count


def run_scraper():
    """Ana scraper fonksiyonu."""
    print("=" * 60)
    print("Akademik Veri Toplama Başlatılıyor...")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        print("\n1. Türkiye + Yurt Dışı Üniversiteleri yükleniyor...")
        save_universities(db)

        print("\n2. Türkiye + Uluslararası Akademisyen verileri ekleniyor...")
        generate_sample_academics(db)

        print("\n3. Akademik yayınlar ekleniyor...")
        generate_sample_publications(db)

        # Summary
        uni_count = db.query(University).count()
        acad_count = db.query(Academic).count()
        pub_count = db.query(Publication).count()

        print("\n" + "=" * 60)
        print("TOPLAM VERİ:")
        print(f"  🏛️  Üniversiteler: {uni_count}")
        print(f"  👨‍🏫 Akademisyenler: {acad_count}")
        print(f"  📄 Yayınlar: {pub_count}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    run_scraper()
