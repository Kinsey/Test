#!/bin/bash

sync_init () {
  bak_date=`date +%Y%m%d`

  ht_devops=/usr/local/ht_devops
  dbsync=$ht_devops/dbsync
  bak_data=$dbsync/bak_data
  workspace=$dbsync/workspace
  rm -rf /usr/local/ht_devops/dbsync/workspace/*

  mongo_init
  mysql_init
}

mongo_init () {
  mongo_cmd='/root/mongodb/bin/mongo'
  mongorestore_cmd='/root/mongodb/bin/mongorestore'

  mongo_data_file=$bak_data/mongo-$bak_date.tar.gz
  uncompress_file_to_workspace $mongo_data_file

  mongo_update_scripts=`find update_scripts -name '*.js' -printf '%f\n' | sort | xargs `
}

mysql_init () {
  mysql_user='root'
  mysql_pwd='admin123'
  mysql_cmd="/usr/bin/mysql -h $mysql_host -u $mysql_user -p$mysql_pwd -e"

  mysql_data_file=$bak_data/mysql-$bak_date.tar.gz
  uncompress_file_to_workspace $mysql_data_file

  #sort scripts by date nested in filename, asending
  mysql_update_scripts=`find update_scripts -name "*.sql" -printf "%f\n" | awk '{FS="_"; $0=$0;  print $NF"|"$0}' | sort | cut -d"|" -f2 | xargs`
}


uncompress_file_to_workspace () {
  file_name=$1

  tar -zxf $file_name -C $workspace

  if [ $? -ne 0 ];then
    echo "uncompress file $file_name failed"
    exit -1
  fi  
}


mongo_sync_start () {
  mongo_port=27017
  import_mongo_data

  if [ -n "$mongo_update_scripts" ];then
    exec_mongo_update_scripts
  fi
}


import_mongo_data () {
  echo -n "importing mongodb data..."
  cmd="$mongorestore_cmd -h $mongo_host:$mongo_port --batchSize=10 --quiet $workspace/$bak_date --drop"
  `$cmd`

  check_status
}


exec_mongo_update_scripts () {
  for script in $mongo_update_scripts
  do
    echo -n "executing $script..."
    cmd="$mongo_cmd --quiet $mongo_host:$mongo_port/component update_scripts/$script"
    `$cmd`
    check_status
  done
}


mysql_sync_start () {
  drop_mysql_databases
  import_mysql_data

  if [ -n "$mysql_update_scripts" ];then
    exec_mysql_update_scripts
  fi

  echo ""

  # flush redis and restart mycat service
  python flush_service.py $option
}


drop_mysql_databases () {
  echo -n "dropping mysql databases..."

  #clear all databases prefixed with agz_ and database app_platform_config
  for db in `$mysql_cmd "show databases" | grep -E '(agz_|app_platform_config)' `
  do
         $mysql_cmd "drop database if exists $db;"
  done
  echo "ok"
}


import_mysql_data () {
  echo -n "importing mysql data..."

  sed -i '/GLOBAL.GTID_PURGED/d' $workspace/$bak_date.sql

  cmd="$mysql_cmd 'source $workspace/$bak_date.sql'"

  $mysql_cmd "source $workspace/$bak_date.sql"

  check_status
}


exec_mysql_update_scripts () {
  for script in $mysql_update_scripts
  do
    cmd="$mysql_cmd 'source update_scripts/$script'"
     
    echo -n "executing $script..."   
    $mysql_cmd "source update_scripts/$script"

    check_status
  done
}


print_sync_detail () {
  echo "Please confirm following information: "
  echo "-----------------------------------------------------------------------"
  echo "mysql_host: $mysql_host"
  echo "mysql_update_scripts: $mysql_update_scripts"
  echo ""
  echo "mongo_host: $mongo_host"
  echo "mongo_update_script: $mongo_update_scripts"
  echo ""
  echo "data_date=$bak_date"
  echo "-----------------------------------------------------------------------"
}

prompt_for_confirmation () {
  echo -n "Type 'continue' to proceed: "
  read answer
  if [ "$answer" != "continue" ];then
    echo "exit due to user abort"
    exit 1
  fi
  echo ""
}

check_status () {
  if [ $? -eq 0 ];then
    echo "ok"
  else
    echo "command \"$cmd\" failed to execute"
    exit -1
  fi    
}

option="${1}"
case ${option} in
   dev01) mysql_host="dev01.demo.com"
          mongo_host="dev01.demo.com"
      ;;
   tev02) mysql_host="mysql02.demo.com"
          mongo_host="mongo02.demo.com"
      ;;
   lb01)  mysql_host="mysql03.demo.com"
          mongo_host="IM03.demo.com"
      ;;
   cp01)  mysql_host="mysql01.demo.com"
          mongo_host="mongo01.demo.com"
      ;;
   cp02)  mysql_host="cp02.demo.com"
          mongo_host="cp02.demo.com"
      ;;
   testjk)  mysql_host="testjk.demo.com"
          mongo_host="testjk.demo.com"
      ;;
   *)
      echo "usage: `basename ${0}` [dev01|tev02|lb01|cp01|cp02]"
      exit 1
      ;;
esac

sync_init

print_sync_detail
prompt_for_confirmation

mongo_sync_start
mysql_sync_start


