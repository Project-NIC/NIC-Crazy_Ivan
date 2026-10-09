<div align="center">

<img src="NIC-Crazy_Ivan.jpg" width="100%"/>

# NIC-Crazy_Ivan

[English](README.md) · **Čeština** · [Русский](README.ru.md)

**Neurální oblek:** 126 až 254 elektrod a 16 až 64 inerciálních jednotek na obleku, který si
skládáš z dílů, jako je rukáv, nohavice, trup nebo čelenka.

Vlastní signály svalů a pohyb těla jdou do počítače v batohu, Radxa ROCK 5T až se dvěma
AI akcelerátory Hailo-10H nebo Raspberry Pi 5 s jedním, a celé tělo se stává ovladačem počítače
nebo hry.

**Coming soon™.** No, zas *tak* brzy ne.

</div>

> **Beta 0.1:** koncept ve stádiu návrhu, nic ještě není postaveno; co je uzavřené, co otevřené a
> co je jen odhad, je ve [stavu projektu](STATUS.md) (anglicky). Ostatní stránky jsou anglicky.

---

## Co to je

Oblek pokrytý elektrodami a pohybovými senzory. Skládá se z dílů: rukáv, nohavice, trup, čelenka
kolem hlavy a další. Každý díl je samostatný modul a díly jdou spojovat v libovolné kombinaci.
Větší oblek je prostě víc dílů na téže sběrnici.

## Tomografie

Celý projekt stojí na tomografii. Elektrody nejsou vztažené k jednomu společnému bodu jako
v klasickém záznamu. V každém bloku se elektrody různých kanálů navzájem kříží, takže každý kanál
měří směs signálů.

Důvod je ten, že oblek si nikdy neoblékneš dvakrát úplně stejně. Nesledujeme tedy přesný bod na
těle. Sledujeme, jak se signály navzájem podobají a jak se vyvíjejí.

## Části

| část | co to je |
|---|---|
| [**Rubaška**](rubaska/README.md) | oblek sám: díly se snímacími moduly |
| [**Nataša**](natasa/README.md) | jednotka v čelence: sluchátka, dva mikrofony, vibrace a tlačítka |
| [**Mamka**](mamka/README.md) | základní deska: hodiny pro celý oblek, zvukový most, budiče linek a napájení obleku |
| [**Baťa**](bata/README.md) | počítač v batohu, Radxa ROCK 5T nebo Raspberry Pi 5, s Umnicí, Hailo-10H |
| [**Kormilica**](kormilica/README.md) | napájecí deska Raspberry Pi: jeho 5,1 V a jeho Hailo-10H |
| [**Terem**](terem/README.md) | deska pod ROCKem 5T: jeho dvě Hailo-10H, každé s vlastním zdrojem, a eFuse, která napájí ROCK |
| [**Babuška**](babuska/README.md) | baterie a její BMS, batoh s pevnou skořepinou, napájecí varianty |
| [**Porjadok**](porjadok/README.md) | co platí pro každý modul: procesor, firmware, spoje mezi deskami |
| [**software**](software/README.md) | kód: protokoly jako kodeky v Pythonu s testy, později firmware a Baťovy programy |

## Rodina v batohu

Mamka je ruský slang pro základní desku a zbytek batohu se k ní přidal jako rodina. Jména jsou
ruská, psaná latinkou po česku:

| kdo | význam | co dělá |
|---|---|---|
| **Mamka** | máma | základní deska: řídí oblek a živí své vlastní děti, Rebjata |
| **Baťa** | táta, slangově šéf | počítač A: ROCK 5T nebo Raspberry Pi 5, s Mamkou na svém headeru |
| **Umnica** | chytrá dcera | Hailo-10H, která za tátu přemýšlí |
| **Kormilica** | kojná | živí Raspberry Pi a jeho Umnici, na jeho headeru |
| **Terem** | horní komnata dcer | deska ve dvou slotech M.2 ROCKu 5T: obě Umnice, každá s vlastním zdrojem, a eFuse ROCKu |
| **Babuška** | babička | baterie: drží spižírnu a všichni jedí od ní |
| **Ključnica** | klíčnice | BMS: drží klíče od babiččiny spižírny |
| **Deduška** | dědeček, babiččin muž | počítač B, je-li chtěn: plný počítač vedle Bati přes Ethernet, s brýlemi a programy |
| **Ďaďa Sem** | strýček Sam, strýc z Ameriky | kamery, které vidí všechno: dvě USB kamery do Bati, čte je jeho druhá Umnica |
| **Budilnik** | budík | startovací tlačítko a jeho zámek: jeden stisk probudí domácnost, a když všichni skončí, nechá dům zhasnout |
| **Storož** | noční hlídač | Baťův zastavovací démon: při fatální chybě zastaví služby domácnosti, nechá otevřený terminál a řekne proč |
| **Kommunalka** | komunální byt | batoh: celá rodina v něm bydlí a sdílí jednu kuchyni, Babušku |
| **Chodiki** | nástěnné hodiny se závažími | hodiny obleku, podle kterých žije celá domácnost |

Na těle je oblek **Rubaška**, košilka, v níž se člověk rodí. Mamčiny vlastní děti, **Rebjata**
(snímací moduly), visí na **Pupovině**, pupeční šňůře: na linkách, které jim nosí napájení,
hodiny a data. Malé procesory v rukavici a na noze, **Vnučata**, jsou její vnoučata. Pravidla
domácnosti jsou **Porjadok** a její napájení, od Babušky dolů, **Pitanije**.

Díly se volně kombinují:

| díl | varianta | co to je |
|---|---|---|
| Baťa | Raspberry Pi 5 | Kormilica na jeho headeru a Mamka nad ní, Umnica na Kormilici |
| Baťa | Radxa ROCK 5T | Mamka na jeho headeru, Terem v jeho dvou slotech s jednou nebo dvěma Umnicemi; profily *normal* a *brutal* |
| napájení | 5 A | BMS pustí 5 A: Baťa sám |
| napájení | 10 A | BMS pustí 10 A: Baťa a Deduška, s rezervou |

- **Baťa na Raspberry Pi, 5 A:** prostý oblek, nejmenší spotřeba.
- **Baťa na ROCKu 5T, 5 A:** dvě Umnice a v profilu *brutal* celý systém s brýlemi na jeho USB-C.
- **Baťa a Deduška, 10 A:** Baťa řídí jen oblek a Deduška je plný počítač s brýlemi; oblek je jeho
  myš a klávesnice.

Podrobnosti jsou u [Bati](bata/README.md) a [Babušky](babuska/HARDWARE.md#power-variants), a
proč se kdo jak jmenuje, ve [jménech](NAMES.md).

## Asistenti

Nataša je hardware v čelence; asistenti jsou programy na Baťovi, které ji používají, každý
s vlastním jménem. Nepotřebují elektrody, takže jim stačí čelenka a batoh (Mamka, Baťa a
Babuška) bez snímacích modulů. Jen Míša přidává vlastní hardware: jednotku na čele s radarem,
ultrazvukem a IMU, zapojenou do Nataši.

| asistent | co dělá |
|---|---|
| [**Soňa**](sona/README.md) | pro neslyšící: pořád poslouchá a vibrací říká, co se kolem děje |
| [**Míša**](misa/README.md) | hlídač: radar a ultrazvuk hlídají překážky a varují sluchátky a čelenkou |
| [**Taťána**](tatana/README.md) | píše a čte: píše, co diktuješ, a předčítá text, knihy včetně |
| [**Nikita**](nikita/README.md) | rytmus, který cítíš: doba hudby jako vibrace |

Běží jako režimy, zapínané podle potřeby. Na společenské akci nebo kdekoli mezi mnoha lidmi a
při chůzi s průvodcem zůstávají Míša a Soňa vypnuté: vede průvodce, blízký kontakt by Míšu
spouštěl pořád a poplach je vidět na tom, jak lidé kolem reagují.

---

Licence MIT, viz [LICENSE](LICENSE).
