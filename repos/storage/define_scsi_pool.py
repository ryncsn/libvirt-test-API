#!/usr/bin/env python
# Define a storage pool of 'iscsi' type

import os
import re
import sys

import libvirt
from libvirt import libvirtError

from src import sharedmod

required_params = ('poolname', 'sourcename',)
optional_params = {'targetpath': '/dev/disk/by-path',
                   'xml': 'xmls/scsi_pool.xml',
                   }


def display_pool_info(conn):
    """Display current storage pool information"""
    logger.debug("current define storage pool: %s" %
                 conn.listDefinedStoragePools())
    logger.debug("current active storage pool: %s" %
                 conn.listStoragePools())


def check_pool_define(poolname):
    """This function will check if the storage pool with
       the given poolname existed already.It first checks
       if the storagepool xml file exists in /etc/libvirt/storage
       directory
    """
    path = "/etc/libvirt/storage/%s.xml" % poolname
    logger.debug("%s xml file path: %s" % (poolname, path))

    if os.access(path, os.R_OK):
        return True
    else:
        return False


def define_scsi_pool(params):
    """Define a scsi type storage pool from xml"""

    global logger
    logger = params['logger']
    poolname = params['poolname']
    sourcename = params['sourcename']
    xmlstr = params['xml']

    logger.info("the poolname is %s, pooltype is scsi, sourcename is %s" %
                (poolname, sourcename))

    conn = sharedmod.libvirtobj['conn']

    if check_pool_define(poolname):
        logger.error("%s storage pool is defined" % poolname)
        return 1

    logger.debug("storage pool xml:\n%s" % xmlstr)

    pool_num1 = conn.numOfDefinedStoragePools()
    logger.info("original storage pool define number: %s" % pool_num1)
    display_pool_info(conn)

    try:
        logger.info("define %s storage pool" % poolname)
        conn.storagePoolDefineXML(xmlstr, 0)
        pool_num2 = conn.numOfDefinedStoragePools()
        logger.info("current storage pool define number: %s" % pool_num2)
        display_pool_info(conn)
        if check_pool_define(poolname) and pool_num2 > pool_num1:
            logger.info(
                "It is successful to define %s storage pool" %
                poolname)
        else:
            logger.error("%s storage pool was not defined successfully" %
                         poolname)
            return 1
    except libvirtError as e:
        logger.error("API error message: %s, error code is %s"
                     % (e.message, e.get_error_code()))
        return 1

    return 0
