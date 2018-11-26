import db.db_config as cfg


class DB:

    @staticmethod
    def create(cursor):

        msg = (
            'CREATE TABLE USERS ('
            '	id int auto_increment, '
            '	username VARCHAR(255) not null, '
            '	fname VARCHAR(255) not null, '
            '	lname VARCHAR(255) not null, '
            '	password varbinary(100) not null, '
            '	create_time timestamp NULL DEFAULT NULL,'
            '	constraint USERS_pk '
            '		primary key (id) '
            ');')
        cursor.execute(msg)

        msg = (
            'CREATE TABLE SESSIONS ('
            '	id int auto_increment,'
            '	user_id int not null,'
            '	sess_id VARCHAR(50) not null,'
            '	create_time timestamp NULL DEFAULT NULL,'
            '	constraint SESSIONS_pk'
            '		primary key (id),'
            '	constraint SESSIONS_USERS_id_fk'
            '		foreign key (user_id) references USERS (id)'
            ');')
        cursor.execute(msg)

        msg = (
            'CREATE TABLE BLOGS ('
            '	id int auto_increment,'
            '	user_id int not null,'
            '	title VARCHAR(255) not null,'
            '	descr VARCHAR(255) null,'
            '	active boolean default TRUE not null,'
            '	create_time timestamp NULL DEFAULT NULL,'
            '	constraint BLOGS_pk'
            '		primary key (id),'
            '	constraint BLOGS_USERS_id_fk'
            '		foreign key (user_id) references USERS (id)'
            ');')
        cursor.execute(msg)

        msg = (
            'CREATE TABLE POSTS ('
            '	id int auto_increment,'
            '	user_id int not null,'
            '	title VARCHAR(255) not null,'
            '	text TEXT not null,'
            '	create_time timestamp NULL DEFAULT NULL,'
            '	active boolean default TRUE not null,'
            '	constraint POSTS_pk'
            '		primary key (id),'
            '	constraint POSTS_USERS_id_fk'
            '		foreign key (user_id) references USERS (id)'
            ');')
        cursor.execute(msg)

        msg = (
            'CREATE TABLE COMMENTS ('
            '	id int auto_increment,'
            '	post_id int not null,'
            '	user_id int not null,'
            '	parent_comm_id int default NULL null,'
            '	title VARCHAR(255) not null,'
            '	text TEXT not null,'
            '	active boolean default TRUE not null,'
            '	create_time timestamp NULL DEFAULT NULL,'
            '	constraint COMMENTS_pk'
            '		primary key (id),'
            '	constraint COMMENTS_POSTS_id_fk'
            '		foreign key (post_id) references POSTS (id),'
            '	constraint COMMENTS_COMMENTS_id_fk'
            '		foreign key (parent_comm_id) references COMMENTS (id),'
            '	constraint COMMENTS_USERS_id_fk'
            '		foreign key (user_id) references USERS (id)'
            ');')
        cursor.execute(msg)

        msg = (
            'CREATE TABLE BLOGS_POSTS'
            '('
            '	id int auto_increment,'
            '	blog_id int not null,'
            '	post_id int not null,'
            '	constraint BLOGS_POSTS_pk'
            '		primary key (id),'
            '	constraint BLOGS_POSTS_BLOGS_id_fk'
            '		foreign key (blog_id) references BLOGS (id),'
            '	constraint BLOGS_POSTS_POSTS_id_fk'
            '		foreign key (post_id) references POSTS (id)'
            ');')
        cursor.execute(msg)

    @staticmethod
    def clear(cursor):
        try:
            cursor.execute(f'DROP DATABASE IF EXISTS {cfg.db};')
        except BaseException as err:
            """ IN CASE 'database doesn't exist'"""
            if err.args[0] == 1008:
                pass
