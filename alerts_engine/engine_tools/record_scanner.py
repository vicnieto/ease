"""
Contains TriggerScan, the task to be run at regular intervals.
"""

############
# Standard #
############
import logging
import sys
import os
import datetime

###############
# Third Party #
###############
import django
from archapp.interactive import EpicsArchive

##########
# Custom #
##########
#import django_connect
#from .django_connect import prepare
from . import django_connect

#################
# Configuration #
#################
logger = logging.getLogger(__name__)
django_connect.prepare()
from alert_config_app.models import *
from account_mgr_app.models import *



def test_db():
    """
    teset db connection by scanning models in the config_app. Only intended for
    diagnostic use
    """
    #print("testing")
    for x in Alert.objects.all():
        print("\n--+",x)
        for y in x.trigger_set.all():
            print('  |-->',y)


class TriggerScan:
    def __init__(self, hostname="pscaa02", rep_t=datetime.timedelta(minutes=1)):
        """

        Parameters
        ----------
        hostname : string
            specify location of archiver

        rep_t : datetime.timedelta
            specify duration of each period between scans
        """
        #timing info etc probs useful
        self.arch = EpicsArchive(hostname=hostname)
        self.rep_t = rep_t
        pass

    def dbPvPull(self,live=True):
        """
        Return queryset of relevant PVs. 

        Parameters
        ----------
        live : bool
            If true, filter the pvs to only those with triggers. Defaults to
            true.

        Returns
        -------
        django.db.models.query.QuerySet (Pv type)

        """
        if live:
            return Pv.objects.filter(trigger__isnull=False)
        else:
            return Pv.objects.all()

    def archPull(self, pv_list, end_time=datetime.datetime.now(),
                 start_time=None):
        """
        return xarray of archiver data for a collection of pvs. Duration of
        data is specified by the interval (rep_t) until the current_time 
        argument.  
        
        Note
        ----
            xarray is preferred for its ability to easily store metadata in the
            attributes field. 
            
        Paramaters
        ----------
        pv_list : django.db.models.query.Queryset (Pv type) or list of strings
            This specifies the list to be pulled from the archiver. This can
            either be in the form of a 
        
        end_time : datetime.datetime 
            current_time is the end time for the pulled data

        start_time : datetime.datetime
            start_time is the start time for the pulled data. Defaults to None
            in which the interval set for the TriggerScan class calculates the
            start_time. 

        Returns
        -------
        dict of xarray.DataArray
            xarray with PV data
        """
        if type(pv_list) == django.db.models.query.QuerySet:
            pv_names = []
            for entry in pv_list:
                pv_names.append(entry.name)
        
        if type(pv_list) == list:
            pv_names = pv_list

        if start_time == None:
            start_time = end_time - self.rep_t

        pv_data = {}

        for name in pv_names:
            pv_data[name] = self.arch.get(
                name,
                xarray = True,
                start = start_time,
                end = end_time,
            )

        return pv_data
        

    def compare(self, dbpv, dbtrig, archpv):
        #examine 1 pv for violations
        logger.debug("compare {} {}".format(str(dbpv.name),str(dbtrig.name)))
        comparison = dbtrig.compare
        # if the value field has been left empty
        if comparison == None:
            return False
        if dbtrig.value == None:
            return False
        status = False
        if comparison == "==":
            raise NotImplementedError
        elif comparison == "<=":
            minimum = archpv[dbpv.name].sel(field='vals').min().item(0)
            if minimum <= dbtrig.value:
                status = True
        elif comparison == ">=":
            maximum = archpv[dbpv.name].sel(field='vals').max().item(0)
            if maximum >= dbtrig.value:
                status = True
        elif comparison == "<":
            minimum = archpv[dbpv.name].sel(field='vals').min().item(0)
            if minimum < dbtrig.value:
                status = True
        elif comparison == ">":
            maximum = archpv[dbpv.name].sel(field='vals').max().item(0)
            if maximum > dbtrig.value:
                status = True
        elif comparison == "!=":
            raise NotImplementedError
        else:
            raise NotImplementedError
        return status


    def scanTask(self, target_time=None, *args, **kwargs):
        """
        Run the entire alert-detecting suite of features and send the according
        email

        Paramters
        ---------
        target_time : datetime.datetime
            ideal scan time 

        Returns
        -------
        None 
        """
        if target_time == None:
            target_time = datetime.datetime.now()

        pv_qset = self.dbPvPull()
        arch_data = self.archPull(pv_qset, target_time)

        # loop through all PVs
        for pv in pv_qset:
            trigger_set = pv.trigger_set.all()
            # all triggers must be compared - ensures all triggers visited once
            for trigger in trigger_set:
                if(self.compare(pv,trigger,arch_data[pv.name])):
                    logger.debug("TRIPPED")




if __name__ == '__main__':
    test_db()
