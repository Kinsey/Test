#!/bin/bash
# Author: wangjz@aigongzuo.com
# Copyright: Hongtoo Inc.

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
  mongo_port=27017

  mongo_cmd='/root/mongodb/bin/mongo'
  mongodump_cmd='/root/mongodb/bin/mongodump'
  mongorestore_cmd='/root/mongodb/bin/mongorestore'

  mongo_data_file=$bak_data/mongo-$bak_date.tar.gz
  uncompress_file_to_workspace $mongo_data_file

  mongo_update_scripts=`find update_scripts -name '*.js' -printf '%f\n' | sort | xargs `
}


mysql_init () {
  mysql_user='root'
  mysql_cmd="/usr/bin/mysql -h $mysql_host -u $mysql_user -e"

  # set MYSQL_PWD in env to suppress message "Warning: Using a password on the command line interface can be insecure"
  export MYSQL_PWD='admin123'

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


drop_and_update_mongo () {
  backup_mongo
  import_mongo_data
  exec_mongo_update_scripts
}


backup_mongo () {
 echo -n "backuping mongodb on $mongo_host..."

  cur_date=`date +%Y%m%d`

  backup_data_folder=bak_data/$environment/mongo-$cur_date
  backup_tar_file=bak_data/$environment/mongo-$cur_date.tar.gz

  cmd="$mongodump_cmd --quiet -h $mongo_host:$mongo_port -o $backup_data_folder"
  `$cmd`
  check_status

  archive $backup_data_folder $backup_tar_file
}


import_mongo_data () {
  echo -n "importing mongodb data..."
  cmd="$mongorestore_cmd -h $mongo_host:$mongo_port --batchSize=10 --quiet $workspace/$bak_date --drop"
  `$cmd`

  check_status
}


exec_mongo_update_scripts () {
  if [ -n "$mongo_update_scripts" ];then
    for script in $mongo_update_scripts
    do
        echo -n "executing $script..."
        cmd="$mongo_cmd --quiet $mongo_host:$mongo_port/component update_scripts/$script"
        `$cmd`
        check_status
    done
  fi
}


drop_and_update_mysql () {
  backup_mysql
  drop_mysql_databases
  import_mysql_data
  exec_mysql_update_scripts
  flush_service
}


backup_mysql () {
  echo -n "backuping mysql on $mysql_host..."

  cur_date=`date +%Y%m%d`

  backup_sql_file=bak_data/$environment/mysql-$cur_date.sql
  backup_tar_file=bak_data/$environment/mysql-$cur_date.tar.gz

  cmd="mysqldump -h$mysql_host -u$mysql_user --all-databases > $backup_sql_file"
  mysqldump -h$mysql_host -u$mysql_user --all-databases > $backup_sql_file
  check_status

  archive $backup_sql_file $backup_tar_file
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
  if [ -n "$mysql_update_scripts" ];then
    for script in $mysql_update_scripts
    do
        cmd="$mysql_cmd 'source update_scripts/$script'"

        echo -n "executing $script..."
        $mysql_cmd "source update_scripts/$script"

        check_status
    done
  fi
}


flush_service () {
  # flush redis and restart mycat service
  python flush_service.py $environment
}


archive () {
  src=$1
  dest=$2

  echo -n "archiving backup data..."
  cmd="tar -zcf $dest $src"
  tar -zcf $dest $src
  check_status

  rm -rf $src
}


print_sync_detail () {
  echo "Please confirm following information: "
  echo "-----------------------------------------------------------------------"
  echo "run_type: $run_type"
  echo ""

  if [ $run_type = 'drop_and_update_all' -o $run_type = 'drop_and_update_mysql' -o $run_type = 'update_mysql' ];then
    echo "mysql_host: $mysql_host"
    echo "mysql_update_scripts: $mysql_update_scripts"
    echo ""
  fi

  if [ $run_type = 'drop_and_update_all' -o $run_type = 'drop_and_update_mongo' -o $run_type = 'update_mongo' ];then
    echo "mongo_host: $mongo_host"
    echo "mongo_update_script: $mongo_update_scripts"
    echo ""
  fi

  echo "data_date=$bak_date"
  echo "-----------------------------------------------------------------------"
}


prompt_for_confirmation () {
  print_sync_detail
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


show_usage () {
    echo "usage: `basename ${0}` (dev01|tev02|lb01|cp01|cp02) <run_type>"
    echo "<run_type> can be"
    echo "  drop_and_update_all          drop mongo and mysql databases and import"
    echo "  drop_and_update_mongo        drop mongo data and import"
    echo "  drop_and_update_mysql        drop mysql data and import"
    echo "  update_mongo                 execute mongo update scripts only"
    echo "  update_mysql                 execute mysql update scripts only"
    echo "  flush_service                restart mycat and flush redis"
}


environment="${1}"
run_type="${2}"

case ${environment} in
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
      show_usage
      exit 1
      ;;
esac

sync_init

case ${run_type} in
   drop_and_update_all)
          prompt_for_confirmation
          drop_and_update_mongo
          drop_and_update_mysql
      ;;
   drop_and_update_mongo)
          prompt_for_confirmation
          drop_and_update_mongo
      ;;
   drop_and_update_mysql)
          prompt_for_confirmation
          drop_and_update_mysql
      ;;
   update_mongo)
          prompt_for_confirmation
          exec_mongo_update_scripts
      ;;
   update_mysql)
          prompt_for_confirmation
          exec_mysql_update_scripts
      ;;
   flush_service)
          flush_service
      ;;
   *)
      show_usage
      exit 1
      ;;
esac