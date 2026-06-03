#!/bin/bash
set -e
cd /usr/app/dbt
dbt deps
exec bash
