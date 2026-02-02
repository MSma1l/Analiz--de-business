## 1. bd_sqlite Baza de date.

### 1.1 conexiune.py conectare si activare Sqlite server si API pentru comunicare cu serverul. avem doar ce API se va deschide si care va fi URL lui si plus verificare daca serverul a fost pornit cu succes.

### 1.2 fuction_bd.py in acest fisier avem functiile noastre pentru BD de set si get afisare si colectare a datelor de la client, avem functia 

#### 1.2.1 get or create user  acesta functie ii colecteaza datele despre utilizator la momentul cand acesta doar a dat start la bot colectam user name, last name, telegram id si aceste date se salveaza in baza de date un vom putea sa fcem urmatoarele etiratii cu el.

#### 1.2.2 set user language estee o functie prin care utilizatorul selectand limba rusa sau romana, aceasta functie ne ajuta pe noi sa salvam limba pentru utilizator daca el a selectato, rusa sau romana, si in BD salvam indexul 1 ca curent limba curenta si limba ru sau ro pentru utilizator cu telegram id personal.

#### 1.2.3 ge user by telegram id prin acesta functie noi  primim userul clientului si il transmitem in prima  functie get or create user.Folosind select(user).where(user.telegram_id== telegram id) prin acesta linie de cod noi ii colectam telgram id.

#### 1.2.4 save answer prin acesta fucntie noi transmitem user ID, intrebare ID, valoare raspunsul utilizatrului cu boolean true or false asa cum din cele 3 variante e pastreaa doar 2 ca nu stiu si nu este la fel nu si true ca da valaore pozitiva,in BD se salveaza raspunsul la care intrebare si ce valoare are raspunsul.

#### 1.2.5 get current question este pentru a vedea care este intrebarea si ce valoare are acesta valaore,la limba selectata gen daca e ru atunci intrebarile sa fie in rusa si nu in romana sisa nu apara confuzie si invers 

### 1.3 models.py in aceast fisier noi avem scriese modelurile bazei de date ceea ce contine in ine ce tabele si ce campuri

### 1.4 scheme_bd.py este verificarea daca sa creat corect baza de date si daca ea deja exista sa nu se mai crieze 

## 2 Bot 
### 2.1 avem getionari unde avem comands meniul principal intrebarile raport pdf unde se genereaza acest pdf si mai corect primeste date  de la server si crieaza genereaaza acesta fisier,rezultate unde se salveaza si se primeste raspunsurile de la  client si le pastram si le tremitem in BD dupa vem start unde avem pornirea botului si principale fucntii de lucru cu selectarea limbeisi etc. si test unde avem testul cu intrebarile care sunt si cu intrebari si pozitia lor de afisare 

    ### voi adauga la intrebari ca el sa fie vazute gen enumerarea lor sa stim a cata intrebare este din numarul toatl de intrebari!

### 2.2 tastatura in tstatura vem tastatura de la meniu principal, limba pentru locatie contact meniu Button.py si pentru test tastatura 
