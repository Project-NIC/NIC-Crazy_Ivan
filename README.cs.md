<div align="center">

<img src="NIC-Crazy_Ivan.jpg" width="100%"/>

# NIC-Crazy_Ivan

[English](README.md) · **Čeština** · [Русский](README.ru.md)

**Neurální oblek:** až 288 elektrod a 84 inerciálních jednotek, 40 z nich ve dvou rukavicích, na
obleku, který si skládáš z dílů, jako je rukáv, nohavice, trup nebo čelenka.

Vlastní signály svalů a pohyb těla jdou do počítače v batohu, Radxa ROCK 5T s vlastním NPU nebo
až se dvěma AI akcelerátory Hailo-10H, a celé tělo se stává ovladačem počítače nebo hry.

**Coming soon™.** No, zas *tak* brzy ne.

</div>

> **Beta 0.4:** koncept ve stádiu návrhu, nic ještě není postaveno; co je uzavřené, co otevřené a
> co je jen odhad, je ve [stavu projektu](STATUS.md) (anglicky). Ostatní stránky jsou anglicky.

---

## Co to je

Oblek pokrytý elektrodami a pohybovými senzory. Skládá se z dílů: rukáv, nohavice, trup, čelenka
kolem hlavy a další. Každý díl je samostatný modul a díly jdou spojovat v libovolné kombinaci.
Větší oblek je prostě víc dílů na téže sběrnici. Každý nosí jen díly, které pro něj mají smysl,
třeba kvadruplegik. Měří jen tělo, svaly (EMG) a pohyb (IMU), na jedné časové základně.

## K čemu je

- **Především ovladač.** Jediné, co každý oblek potřebuje, je vyhodnocovací jednotka,
  [Baťa](bata/README.md), a ten slouží jen jako ovladač, takže oblek jde připojit k počítači,
  chytré televizi, čemukoli; počítač, na kterém se pracuje, je Borovičok. Hrát hry, kreslit
  v AutoCADu, programovat, psát zprávy: to všechno vestoje, při chůzi po louce, na lavičce v parku.
- **Za druhé rehabilitace.** Tak přesný oblek zachytí signály svalů zraněného nebo postiženého
  člověka; lékař je vidí, řekne, co ukazují, a nastaví zátěž, tuhle ruku víc, tamtu míň. Pomůcka
  vedle lékaře, ne certifikovaný zdravotnický prostředek.
- **Vedle nich asistenti** (níže), programy na Baťovi, které používají čelenku.

**Jak poznáme, že to funguje:** jako ovladač, když nositel dělá skutečnou práci místo myši a
klávesnice, nakreslí díl v AutoCADu, napíše zprávu, zahraje si hru, vestoje i při chůzi, a po
každém oblečení stačí krátká kalibrace, protože oblek se nikdy neoblékne dvakrát stejně; při
rehabilitaci, když lékař ze záznamu pozná, který sval pracuje a jak silně, stranu proti straně a
den proti dni, a souhlasí to s tím, co zjistí vyšetřením.

**Co musí umět,** v rozsazích: EMG na 3 840 SPS s pásmem do ~1 kHz, pro rychlé pohyby ve sportu a
pro záškuby nervové soustavy, která nefunguje, jak má, 1 920 SPS jako nastavení k vyzkoušení; IMU
v krocích po 120 Hz; nejvýš desítky milisekund od svalu k výstupu; gesta pro počítač a úhly
kloubů s chybou v jednotkách stupňů; kalibrace nejvýš několik minut; pracovní den, ~8 h, na jedno
nabití v menších osazeních; pot a slabý déšť, ne ponoření. Váha a cena se teprve ukážou.

## Tomografie

„Tomografie“, v uvozovkách: ne každá elektroda proti každé, to osm kanálů nedá, ale kanály, z nichž
každý bere směs svalů. Dvě elektrody kanálu leží 4–8 cm od sebe, kde to sval dovolí, na sousedních
svalech nebo podél jednoho, střídavě podél vláken a napříč, a přes páteř jen šikmo, takže se tětivy
kříží; dál od sebe by sbíraly víc přeslechů a na trupu víc srdce. Proti referenční elektrodě, druhým
způsobem na tomtéž obleku, měří osm elektrod každého modulu každá proti jednomu bodu a libovolný
jejich pár se složí v softwaru. Na ruce a na nártu má každý pár svůj sval; dlaň, chodidlo a sedací
část zůstávají bez elektrod, protože se na ně tlačí.

Důvod je ten, že oblek si nikdy neoblékneš dvakrát úplně stejně. Nesledujeme tedy přesný bod na
těle. Sledujeme, jak se signály navzájem podobají a jak se vyvíjejí. Jestli to funguje, nevíme;
studie naznačují, že by mohlo (viz [Bogatyr](bogatyr/README.md)).

## Části

| část | co to je |
|---|---|
| [**Rubaška**](rubaska/README.md) | oblek sám: díly se snímacími moduly, rukavice Vešč, elektrody a postroj |
| [**Bogatyr**](bogatyr/README.md) | rozložení na těle: kde sedí každá elektroda a každá IMU, sval po svalu, a proč |
| [**Nataša**](natasa/README.md) | jednotka v čelence: sluchátka, dva mikrofony, vibrace a tlačítka |
| [**Mamka**](mamka/README.md) | základní deska: hodiny pro celý oblek, zvukový most, budiče linek a napájení obleku |
| [**Baťa**](bata/README.md) | počítač v batohu, Radxa ROCK 5T, s Umnicí, Hailo-10H, nebo jen s vlastním NPU |
| [**Terem**](terem/README.md) | deska pod ROCKem 5T: jeho dvě Hailo-10H, každé s vlastním zdrojem |
| [**Babuška**](babuska/README.md) | baterie a její BMS, batoh s pevnou skořepinou, napájecí varianty |
| [**Porjadok**](porjadok/README.md) | co platí pro každý modul: procesor, firmware, spoje mezi deskami |
| [**software**](software/README.md) | kód: protokoly jako kodeky v Pythonu s testy, později firmware a Baťovy programy |

## Rodina v batohu

Mamka je ruský slang pro základní desku a zbytek batohu se k ní přidal jako rodina. Jména jsou
ruská, psaná latinkou po česku:

| kdo | význam | co dělá |
|---|---|---|
| **Mamka** | máma | základní deska: řídí oblek a živí své vlastní děti, Rebjata |
| **Baťa** | táta, slangově šéf | počítač A: ROCK 5T, s Mamkou na svém headeru |
| **Umnica** | chytrá dcera | Hailo-10H, která za tátu přemýšlí |
| **Terem** | horní komnata dcer | deska ve dvou slotech M.2 ROCKu 5T: obě Umnice, každá s vlastním zdrojem |
| **Babuška** | babička | baterie: drží spižírnu a všichni jedí od ní |
| **Ključnica** | klíčnice | BMS: drží klíče od babiččiny spižírny |
| **Kormilica** | kojná | Mamčina napájecí část: její vlastní napájení, měniče linek, eFuse počítačů |
| **Borovičok** | stařeček hříbeček, babiččin muž | počítač B, je-li chtěn: plný počítač vedle Bati přes Ethernet, s brýlemi a programy |
| **Ďaďa Sem** | strýček Sam, strýc z Ameriky | kamery, které vidí všechno: dvě USB kamery do Bati, čte je jeho druhá Umnica, v osazení small a normal jeho vlastní NPU |
| **Budilnik** | budík | startovací tlačítko a jeho zámek: jeden stisk probudí domácnost, a když všichni skončí, nechá dům zhasnout |
| **Storož** (Tron) | noční hlídač | Baťův zastavovací démon: při fatální chybě zastaví služby domácnosti, nechá otevřený terminál a řekne proč |
| **Kommunalka** | komunální byt | batoh: celá rodina v něm bydlí a sdílí jednu kuchyni, Babušku |
| **Chodiki** | nástěnné hodiny se závažími | hodiny obleku, podle kterých žije celá domácnost |

Na těle je oblek **Rubaška**, košilka, v níž se člověk rodí, na **Kaščejovi**, postroji; kde na něm
co sedí, je **Bogatyr**, Kaščej oblečený do masa. Mamčiny vlastní děti, **Rebjata** (snímací
moduly), visí na **Pupovině**, pupeční šňůře: na osmi linkách, jedné na díl obleku, které jim,
rukavicím, Nataše a Míšovi nosí napájení, hodiny a data. Hlavní procesor každé snímací jednotky je
**Staršaja**, ta starší; rukavice, **Vešč**, má na prstech její mladší bratříčky, **Bratiški**.
Pravidla domácnosti jsou **Porjadok** a její napájení, od Babušky dolů, **Pitanije**.

Díly se volně kombinují:

| díl | varianta | co to je |
|---|---|---|
| Baťa | *small* | Mamka na jeho headeru, model na jeho vlastním NPU, bez Teremu |
| Baťa | *normal*, *brutal* | Mamka na jeho headeru, Terem v jeho dvou slotech s jednou nebo dvěma Umnicemi |
| napájení | 5 A | BMS pustí 5 A: Baťa sám |
| napájení | 10 A | BMS pustí 10 A: Baťa a Borovičok, s rezervou |

- **Baťa *small*, 5 A:** malý oblek, čelenka a pár modulů, nejmenší spotřeba.
- **Baťa s Teremem, 5 A:** jedna nebo dvě Umnice a v osazení *brutal* celý systém s brýlemi na
  jeho USB-C.
- **Baťa a Borovičok, 10 A:** Baťa řídí jen oblek a Borovičok je plný počítač s brýlemi; oblek je
  jeho myš a klávesnice.

Podrobnosti jsou u [Bati](bata/README.md) a [Babušky](babuska/HARDWARE.md#power-variants), a
proč se kdo jak jmenuje, ve [jménech](NAMES.md).

## Asistenti

Nataša je hardware v čelence; asistenti jsou programy na Baťovi, které ji používají, každý
s vlastním jménem. Nepotřebují elektrody, takže jim stačí čelenka a batoh (Mamka, Baťa a
Babuška) bez snímacích modulů. Jen Míša přidává vlastní hardware: jednotku na čele s radarem,
ultrazvukem a IMU, s vlastním místem na lince 8 vedle Nataši.

| asistent | co dělá |
|---|---|
| [**Soňa**](sona/README.md) | pro neslyšící: pořád poslouchá a vibrací říká, co se kolem děje |
| [**Míša**](misa/README.md) | hlídač: radar a ultrazvuk hlídají překážky a varují sluchátky a čelenkou |
| [**Taťána**](tatana/README.md) | píše a čte: píše, co diktuješ, a předčítá text, knihy včetně |
| [**Nikita**](nikita/README.md) | rytmus, který cítíš: doba hudby jako vibrace |
| [**Pomoščnik**](pomoscnik/README.md) | pomocník: podívá se na součástku, přečte její označení a najde ji, s brýlemi a kamerami |

Běží jako režimy, zapínané podle potřeby. Na společenské akci nebo kdekoli mezi mnoha lidmi a
při chůzi s průvodcem zůstávají Míša a Soňa vypnuté: vede průvodce, blízký kontakt by Míšu
spouštěl pořád a poplach je vidět na tom, jak lidé kolem reagují.

## Poděkování

Asistentovi s umělou inteligencí Claudovi (Anthropic), velká pomoc v celém projektu: oblek je
navrhovaný s AI a tyto stránky jsou s ní psané.

---

Software pod licencí MIT, viz [LICENSE](LICENSE); návrh hardwaru, stránky a obrázky pod
CERN-OHL-P v2, viz [LICENSE-HW](LICENSE-HW).
