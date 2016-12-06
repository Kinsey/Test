#!/bin/bash
if [ $# -ne 1 ]; then
   bak_date=`date +%Y%m%d`
else
   bak_date=$1
fi

bak_path=/usr/local/ht_devops/bak_data
production_puppet_server=114.55.129.230
rsa_file=/root/.ssh/id_rsa_2048

scp -i $rsa_file -rp $production_puppet_server:$bak_path/mysql-$bak_date.tar.gz $bak_path/
scp -i $rsa_file -rp $production_puppet_server:$bak_path/mongo-$bak_date.tar.gz $bak_path/

#clear bak data older than a week
find /usr/local/ht_devops/bak_data -mtime +7 -type f -exec rm -f {} \;
