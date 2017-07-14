import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__),os.pardir,os.pardir,"web_interface")))

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'web_interface.settings'
django.setup()

import random

from account_mgr_app.models import *
from alert_config_app.models import *
from django.contrib.auth.models import User

def populate():
	a = "test_alert_"
	p = "test_pv_"
	t = "test_trigger_"
	compares = ['==', '>=', '<=', '!=']
	for i in range(1,6):
		al = a + str(i)
		temp_alert = Alert(name=al)
		temp_alert.save()		

		pr = p + str(i)
		temp_pv = Pv(name=pr)
		temp_pv.save()

		tr = t + str(i)
		
		if (random.randint(100, 10000)%2 == 0):
			temp_trigger = Trigger(name=tr, alert=temp_alert, pv=temp_pv, value=random.randint(0,100), compare=random.choice(compares))
			temp_trigger.save()
		else:
			temp_trigger = Trigger(name=tr, alert=temp_alert, pv=temp_pv)
			temp_trigger.save()


def depopulate():
	Alert.objects.all().delete()
	Pv.objects.all().delete()
	Trigger.objects.all().delete()


populate()

	
