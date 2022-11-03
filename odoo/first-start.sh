#!/bin/bash

CONTAINER_ALREADY_FIRST_START="/var/lib/odoo/CONTAINER_ALREADY_FIRST_START"
if [ ! -e $CONTAINER_ALREADY_FIRST_START ]; then
    touch $CONTAINER_ALREADY_FIRST_START
    echo "-- First container startup --"
    exec odoo -i base
else
    echo "-- Not first container startup --"
fi