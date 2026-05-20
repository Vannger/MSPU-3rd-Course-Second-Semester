# Отчет по ДЗ №2

##Вывод команды "ls -ld top_secret"

##"drwx------ 2 ubuntu ubuntu 60 May 20 19:09 top_secret"

##Вывод команды "ls -ld top_secret"

##"-rw------- 1 ubuntu ubuntu 26 May 20 19:09 top_secret/codes.txt"

##Вывод попытки получить доступ к файлу без разрешения

##"vannger@ubuntu:~$ echo "Am i retarded?" >> /home/ubuntu/top_secret/codes.txt
-bash: /home/ubuntu/top_secret/codes.txt: Отказано в доступе"

## Вывод команды "ls -ld top_secret"

##"total 12
drwx------ 2 ubuntu ubuntu 100 May 20 19:28 .
drwxr-x--- 9 ubuntu ubuntu 240 May 20 19:56 ..
-rw------- 1 ubuntu ubuntu  95 May 20 19:28 authorised_keys
-rw------- 1 ubuntu ubuntu 399 May 20 19:25 id_ed25519
-rw------- 1 ubuntu ubuntu  95 May 20 19:25 id_ed25519.pub"
