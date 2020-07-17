#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'Must pass as an argument the data folder'
    exit 0
fi
DATA_FOLDER=$1

find $DATA_FOLDER -name '*.json' -type f -exec sed -i 's/"due_time":\(\s\?"[0-9]\{1,2\}:[0-9]\{1,2\}"\)/"start_time":\1,"end_time":\1/g' {} \;

echo 'Migration of json data complete. Data files are not backwards compatible with versions previous to v1.0.'
