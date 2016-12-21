#!/bin/bash
if [ $# -ne 1 ]; then
   bak_date=`date +%Y%m%d`
else
   bak_date=$1
fi

src_bak_path=/usr/local/ht_devops/dbsync/bak_data
dest_bak_path=/usr/local/ht_devops/dbsync/bak_data/ali
ali_puppet_server=114.55.129.230
rsa_file=/root/.ssh/id_rsa_2048

scp -i $rsa_file -rp $ali_puppet_server:$src_bak_path/mysql-$bak_date.tar.gz $dest_bak_path/
scp -i $rsa_file -rp $ali_puppet_server:$src_bak_path/mongo-$bak_date.tar.gz $dest_bak_path/

#clear bak data older than a week
find /usr/local/ht_devops/dbsync/bak_data -mtime +7 -type f -exec rm -f {} \;
