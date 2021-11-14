# Deployment Guide

### 1) In the root directory of the project create ***.env*** file and add some keys:
```dotenv
SECRET_KEY=very_secret_key

AWS_S3_ACCESS_KEY_ID=your_aws_access_key_id
AWS_S3_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_STORAGE_BUCKET_NAME=your-unique-bucket-name

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
```

### 2) Next step it's deploy
If you already have ***docker*** and ***docker-compose*** just go to the directory with docker-compose.yml in the 
terminal and run this command:
```shell
docker-compose up --build
```
**or**
```shell
sudo docker-compose up --build
```

If you don't have both of these things just go throw 
[this guide](https://support.netfoundry.io/hc/en-us/articles/360057865692-Installing-Docker-and-docker-compose-for-Ubuntu-20-04).
And after that use one of these commands.

### 3) Create superuser
Now after all containers run you need go inside one. That would be web service.
First you need to know  CONTAINER ID or NAME. For this type command in new opened **terminal** or in second split window in
**tmux** session:
```shell
docker ps
```
Find image ***test_task_web*** and copy CONTAINER ID or NAME. After this type next command:
```shell
docker exec -it <CONTAINER ID | CONTAINER NAME> bash
```

Now you inside the container and you need type command for the creating superuser:
```shell
python manage.py createsuperuser
```
or
```shell
./manage.py createsuperuser
```

And follow the instructions. Write the email and password.

## Deployment end

# If you want to fill the DB

### Now if you want to fill db some data you need to use *data_migration.py* script
For this you need again go inside the web container or if you already in and type this command:
```shell
python data_migration.py
```
And wait until script finished it's work 


