#!/bin/bash
# Author: wangjz@aigongzuo.com
# Copyright: Hongtoo Inc.

init () {
  mysql_host="mysql01.agz.com"
  mongo_host="mongo01.agz.com"

  bak_date=`date +%Y%m%d`
  cur_timestamp=`date +%Y%m%d%H%M%S`

  ht_devops=/usr/local/ht_devops
  move_to_prod=$ht_devops/move_to_prod
  bak_data=$move_to_prod/bak_data/$bak_date

  if [ ! -d "$bak_data" ];then
    mkdir -p $bak_data
  fi

  mongo_init
  mysql_init
}


mongo_init () {
  mongo_port=27017

  mongo_cmd='mongo'
  mongodump_cmd='mongodump'
  mongorestore_cmd='mongorestore'

  mongo_update_scripts=`find update_scripts/mongodb -name '*.js' -printf '%f\n' | sort | xargs `
}


mysql_init () {
  mysql_user='root'
  mysql_cmd="/usr/bin/mysql -h $mysql_host -u $mysql_user -e"

  # set MYSQL_PWD in env to suppress message "Warning: Using a password on the command line interface can be insecure"
  export MYSQL_PWD='admin123'

  #sort scripts by date nested in filename, asending
  mysql_update_scripts=`find update_scripts/mysql -name "*.sql" -printf "%f\n" | awk '{FS="_"; $0=$0;  print $NF"|"$0}' | sort | cut -d"|" -f2 | xargs`
}


backup_mongo () {
 echo -n "backuping mongodb on $mongo_host..."

  backup_data_folder=$bak_data/mongo-$cur_timestamp
  backup_tar_file=$bak_data/mongo.tar.gz.$cur_timestamp

  cmd="$mongodump_cmd --quiet -h $mongo_host:$mongo_port -o $backup_data_folder"
  `$cmd`
  check_status

  archive $backup_data_folder $backup_tar_file
}


exec_mongo_update_scripts () {
  if [ -n "$mongo_update_scripts" ];then
    for script in $mongo_update_scripts
    do
        echo -n "executing $script..."
        cmd="$mongo_cmd --quiet $mongo_host:$mongo_port/component update_scripts/mongodb/$script"
        `$cmd`
        check_status
    done
  fi
}


backup_mysql () {
  echo -n "backuping mysql on $mysql_host..."

  backup_sql_file=$bak_data/mysql-$cur_timestamp.sql
  backup_tar_file=$bak_data/mysql.tar.gz.$cur_timestamp

  cmd="mysqldump -h$mysql_host -u$mysql_user --all-databases --set-gtid-purged=OFF > $backup_sql_file"
  mysqldump -h$mysql_host -u$mysql_user --all-databases --set-gtid-purged=OFF > $backup_sql_file
  check_status

  archive $backup_sql_file $backup_tar_file
}


exec_mysql_update_scripts () {
  if [ -n "$mysql_update_scripts" ];then
    for script in $mysql_update_scripts
    do
        cmd="$mysql_cmd 'source update_scripts/mysql/$script'"

        echo -n "executing $script..."
        $mysql_cmd "source update_scripts/mysql/$script"

        check_status
    done
  fi
}


backup_file() {
    project_folder='/data/projects/ali'
    file_list=(agz-business.zip agz-message.zip agz_web_design.war agz_web_runtime.war)

   for(( i=0;i<${#file_list[@]};i++))
      do
        echo -n "backuping ${file_list[i]}..."

        cmd="cp $project_folder/${file_list[i]} $bak_data/${file_list[i]}.$cur_timestamp"
        `$cmd`
        check_status
      done
}


archive () {
  src=$1
  dest=$2

  echo -n "archiving backup data..."
  cmd="tar -zcf $dest $src"
  tar -zcPf $dest $src
  check_status

  rm -rf $src
}


print_detail () {
  echo "Please confirm following information: "
  echo "-----------------------------------------------------------------------"
  echo "run_type: $run_type"
  echo ""

  if [ $run_type = 'update_mysql' -o $run_type='run_all' ];then
    echo "mysql_host: $mysql_host"
    echo "mysql_update_scripts: $mysql_update_scripts"
    echo ""
  fi

  if [ $run_type = 'update_mongo' -o $run_type='run_all' ];then
    echo "mongo_host: $mongo_host"
    echo "mongo_update_script: $mongo_update_scripts"
    echo ""
  fi

  echo "data_date=$bak_date"
  echo "-----------------------------------------------------------------------"
}


prompt_for_confirmation () {
  print_detail
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
    echo "usage: `basename ${0}` <run_type>"
    echo "<run_type> can be"
    echo "  backup_file         backup agz-business.zip, agz-message.zip, agz_web_design.war, agz_web_runtime.war"
    echo "  backup_mongo        backup_mongo"
    echo "  backup_mysql        backup mysql"
    echo "  update_mongo        execute mongo update scripts"
    echo "  update_mysql        execute mysql update scripts"
    echo "  backup_all          execute backup_file, backup_mongo, backup_mysql in sequence"
    echo "  run_all             execute backup_file, backup_mongo, backup_mysql, update_mongo, update_mysql in sequence"
}


run_type="${1}"

init

case ${run_type} in
   backup_mysql)
          backup_mysql
      ;;
   update_mysql)
          prompt_for_confirmation
          exec_mysql_update_scripts
      ;;
   backup_mongo)
          backup_mongo
      ;;
   update_mongo)
          prompt_for_confirmation
          exec_mongo_update_scripts
      ;;
   backup_file)
          backup_file
      ;;
   backup_all)
          backup_file
          backup_mongo
          backup_mysql
      ;;
   run_all)
          prompt_for_confirmation
          backup_file
          backup_mongo
          backup_mysql
          exec_mongo_update_scripts
          exec_mysql_update_scripts
      ;;
   *)
      show_usage
      exit 1
      ;;
esac
