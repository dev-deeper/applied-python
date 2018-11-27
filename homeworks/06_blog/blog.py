import random
import string
from datetime import datetime
from uuid import uuid4

import db.db_config as cfg
from bcrypt import hashpw, gensalt
from db.db_prepare import DB
from prettytable import PrettyTable
from pymysql import connect


class Blog:
    def __init__(self):
        self._connection = connect(host=cfg.host,
                                   user=cfg.user,
                                   port=cfg.port,
                                   password=cfg.password)
        self._cursor = self._connection.cursor()
        self._timestamp_format = '%Y-%m-%d %H:%M:%S'

        try:
            self._cursor.execute(f"SELECT DATABASE();")
            res = self._cursor.fetchall()
            if res[0][0] is None:
                self._cursor.execute(f"USE \"{cfg.db}\";")
        except BaseException as err:
            if err.args[0] == 1049:
                """IN CASE 'Unknown database'"""
                self._cursor.execute(f"CREATE DATABASE \"{cfg.db}\";")
                self._cursor.execute(f"USE \"{cfg.db}\";")
                DB.create(self._cursor)

    def _user_exist(self, username):
        """CHECK THAT USER EXIST"""
        self._cursor.execute(f"SELECT COUNT(*) FROM USERS "
                             f"WHERE username = \"{username}\";")
        return bool(self._cursor.fetchall()[0][0])

    def _authorised(self, session_id):
        """
        CHECK THAT USER LOGGED IN
        Return user_id if so, else False
        """
        self._cursor.execute(f"SELECT user_id FROM SESSIONS "
                             f"WHERE sess_id = \"{session_id}\";")
        res = self._cursor.fetchall()
        return res[0][0] if res else False

    def user_add(self, username=None, first_name=None,
                 last_name=None, password=None):
        if username is None or first_name is None or last_name is None:
            return False

        if self._user_exist(username):
            print(f"User '{username}' already exist")
            return False

        if password is None:
            """Generate password if isn't set"""
            new_password = ''.join(random.SystemRandom().choice
                                   (string.ascii_letters + string.digits) for _ in range(12))
        else:
            new_password = password
        pass_hash = hashpw(new_password.encode(), gensalt()).decode()
        timestamp = datetime.now().strftime(self._timestamp_format)
        self._cursor.execute(
            f"INSERT INTO USERS (username, fname, lname, password, create_time) VALUES "
            f"(\"{username}\", \"{first_name}\", \"{last_name}\", \"{pass_hash}\", \"{timestamp}\");")
        self._connection.commit()
        return new_password if password is None else True

    def login(self, username=None, password=None):
        if username is None or password is None:
            return False

        if not self._user_exist(username):
            print(f"User '{username}' doesn't exist")
            return False

        self._cursor.execute(f"SELECT password FROM USERS "
                             f"WHERE username = \"{username}\";")
        db_hash = self._cursor.fetchall()[0][0]
        """CHECK THAT PASSWORDS MATCH"""
        if not hashpw(password.encode(), db_hash) == db_hash:
            print('Password is incorrect')
            return False

        self._cursor.execute(f"SELECT id FROM USERS WHERE username = \"{username}\";")
        user_id = self._cursor.fetchall()[0][0]

        self._cursor.execute(f"SELECT sess_id FROM SESSIONS WHERE user_id = \"{user_id}\";")
        session_id = self._cursor.fetchall()
        """CHECK THAT USER ALREADY IN SYSTEM"""
        if session_id:
            return session_id[0][0]

        session_id = uuid4()
        timestamp = datetime.now().strftime(self._timestamp_format)
        self._cursor.execute(f"INSERT INTO SESSIONS (user_id, sess_id, create_time) VALUES "
                             f"(\"{user_id}\", \"{session_id}\", \"{timestamp}\");")
        self._connection.commit()
        return str(session_id)

    def get_users(self, sess_id=None, pretty=False):
        if sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT username, fname, lname FROM USERS;")
        users = self._cursor.fetchall()
        if users:
            if pretty:
                """RETURN LIKE A TABLE"""
                t = PrettyTable(['username', 'First name', 'Last name'])
                for user in users:
                    t.add_row(user)
                return t
            else:
                lst = []
                for user in users:
                    lst.append(user[0])
                return lst
        else:
            print("Users not found")
            return False

    def blog_create(self, title=None, description=None, sess_id=None):
        if title is None or description is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT COUNT(*) FROM BLOGS "
                             f"WHERE title = \"{title}\" "
                             f"AND user_id = \"{user_id}\" "
                             f"AND active = true;")
        blog_exist = bool(self._cursor.fetchall()[0][0])

        if blog_exist:
            print(f"Blog '{title}' already exist")
            return False

        timestamp = datetime.now().strftime(self._timestamp_format)
        self._cursor.execute(f"INSERT INTO BLOGS (user_id, title, descr, create_time) VALUES "
                             f"(\"{user_id}\", \"{title}\", \"{description}\", \"{timestamp}\");")
        self._connection.commit()
        return True

    def blog_edit(self, title=None, new_title=None, new_desc=None, sess_id=None):
        if title is None or new_title is None and new_desc is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT COUNT(*) FROM BLOGS "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        blog_exist = bool(self._cursor.fetchall()[0][0])

        if not blog_exist:
            print(f"Blog '{title}' doesn't exist")
            return False

        self._cursor.execute(f"SELECT COUNT(*) FROM BLOGS "
                             f"WHERE title = \"{new_title}\" "
                             f"AND user_id = \"{user_id}\" "
                             f"AND active = true;")
        new_blog_exist = bool(self._cursor.fetchall()[0][0])

        if new_blog_exist:
            print(f"Blog '{new_title}' already exist")
            return False

        s_descr = '' if new_desc is None else f"descr = \"{new_desc}\""
        s_title = '' if new_title is None else f"title = \"{new_title}\""
        q = ', '.join(filter(None, (s_title, s_descr)))
        self._cursor.execute(f"UPDATE BLOGS SET {q} "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\";")
        self._connection.commit()
        return True

    def blog_delete(self, title=None, sess_id=None):
        if title is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT COUNT(*) FROM BLOGS "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        blog_exist = bool(self._cursor.fetchall()[0][0])

        if not blog_exist:
            print(f"Blog '{title}' doesn't exist")
            return False
        self._cursor.execute(f"UPDATE BLOGS SET active = false "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        self._connection.commit()
        return True

    def get_active_blogs(self, sess_id=None, pretty=False):
        if sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT title, descr FROM BLOGS "
                             f"WHERE active = true;")
        blogs = self._cursor.fetchall()
        if blogs:
            if pretty:
                """RETURN LIKE A TABLE"""
                t = PrettyTable(['Title', 'Description'])
                for blog in blogs:
                    t.add_row(blog)
                return t
            else:
                lst = []
                for blog in blogs:
                    lst.append(blog[0])
                return lst
        else:
            print("Active blogs not found")
            return True

    def get_my_active_blogs(self, sess_id=None, pretty=False):
        if sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT title, descr FROM BLOGS "
                             f"WHERE active = true "
                             f"AND user_id = \"{user_id}\";")
        blogs = self._cursor.fetchall()
        if blogs:
            if pretty:
                """RETURN LIKE A TABLE"""
                t = PrettyTable(['Title', 'Description'])
                for blog in blogs:
                    t.add_row(blog)
                return t
            else:
                lst = []
                for blog in blogs:
                    lst.append(blog[0])
                return lst
        else:
            print("Active blogs not found")

    def post_create(self, title=None, text=None, blogs=None, sess_id=None):
        if title is None or text is None or blogs is None or not blogs or sess_id is None:
            return False

        if not (isinstance(blogs, tuple) or isinstance(blogs, list)):
            print(f"Incorrect type of blogs: '{type(blogs)}'")
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        new_active_blogs = set(blogs).intersection(self.get_my_active_blogs(sess_id=sess_id))
        if not new_active_blogs:
            print("There aren't active blogs in given blogs")
            return False

        timestamp = datetime.now().strftime(self._timestamp_format)
        self._cursor.execute(f"INSERT INTO POSTS (title, text, create_time, user_id) VALUES "
                             f"(\"{title}\", \"{text}\", \"{timestamp}\", \"{user_id}\");")
        post_id = self._cursor.lastrowid

        for blog in new_active_blogs:
            self._cursor.execute(f"SELECT id FROM BLOGS "
                                 f"WHERE title = \"{blog}\" "
                                 f"AND user_id = {user_id} "
                                 f"AND active = true;")
            blog_id = self._cursor.fetchall()
            if blog_id:
                self._cursor.execute(f"INSERT INTO BLOGS_POSTS (blog_id, post_id) VALUES "
                                     f"(\"{blog_id[0][0]}\", \"{post_id}\");")
        self._connection.commit()
        return True

    def post_edit(self, title=None, new_title=None, new_text=None, new_blogs=None, sess_id=None):
        if title is None or new_title is None and new_text is None \
                or new_blogs is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT id FROM POSTS "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        post_exist = self._cursor.fetchall()

        if not post_exist:
            print(f"Post '{title}' doesn't exist")
            return False
        else:
            post_id = post_exist[0][0]

        s_title = '' if new_title is None else f"title = \"{new_title}\""
        s_text = '' if new_text is None else f"text = \"{new_text}\""
        q = ', '.join(filter(None, (s_title, s_text)))
        if q:
            self._cursor.execute(f"UPDATE POSTS SET {q} "
                                 f"WHERE user_id = \"{user_id}\" "
                                 f"AND title = \"{title}\";")

        if new_blogs is not None:
            new_active_blogs = set(new_blogs).intersection(self.get_my_active_blogs(sess_id=sess_id))
            if not new_active_blogs:
                print("There aren't active blogs in given blogs")
                return False

            self._cursor.execute(f"SELECT title FROM BLOGS B, BLOGS_POSTS BP "
                                 f"WHERE B.ID = BP.blog_id "
                                 f"AND B.user_id = \"{user_id}\" "
                                 f"AND B.active = true "
                                 f"AND BP.post_id = \"{post_id}\";")
            blogs_published = self._cursor.fetchall()
            published_blogs = {blog[0] for blog in blogs_published if blogs_published}

            to_detach = published_blogs - new_active_blogs
            to_attach = new_active_blogs - published_blogs
            if to_detach:
                for blog_title in to_detach:
                    self._cursor.execute(f"SELECT id FROM BLOGS "
                                         f"WHERE title = \"{blog_title}\" "
                                         f"AND user_id = \"{user_id}\" "
                                         f"AND active = true;")
                    blog_id = self._cursor.fetchall()[0][0]
                    self._cursor.execute(f"DELETE FROM BLOGS_POSTS "
                                         f"WHERE blog_id = \"{blog_id}\" "
                                         f"AND post_id = \"{post_id}\";")

            if to_attach:
                for blog_title in to_attach:
                    self._cursor.execute(f"SELECT id FROM BLOGS "
                                         f"WHERE title = \"{blog_title}\" "
                                         f"AND user_id = \"{user_id}\" "
                                         f"AND active = true;")
                    blog_id = self._cursor.fetchall()[0][0]
                    self._cursor.execute(f"INSERT INTO BLOGS_POSTS (blog_id, post_id) VALUES "
                                         f"(\"{blog_id}\", \"{post_id}\");")

        self._connection.commit()
        return True

    def post_delete(self, title=None, sess_id=None):
        if title is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT COUNT(*) FROM POSTS "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        blog_exist = bool(self._cursor.fetchall()[0][0])

        if not blog_exist:
            print(f"Post '{title}' doesn't exist")
            return False

        self._cursor.execute(f"UPDATE POSTS SET active = false "
                             f"WHERE user_id = \"{user_id}\" "
                             f"AND title = \"{title}\" "
                             f"AND active = true;")
        self._connection.commit()
        return True

    def comment_create(self, post_title=None, post_owner=None,
                       to_comment_title=None, to_comment_user=None,
                       comment_title=None, comment_text=None, sess_id=None):
        if post_title is None or comment_title is None or \
                post_owner is None or comment_text is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        self._cursor.execute(f"SELECT id FROM USERS "
                             f"WHERE username = \"{post_owner}\";")
        post_owner_id = self._cursor.fetchall()

        if not post_owner_id:
            print(f"User '{post_owner}' doesn't exist")
            return False
        else:
            post_owner_id = post_owner_id[0][0]

        self._cursor.execute(f"SELECT id FROM POSTS "
                             f"WHERE user_id = \"{post_owner_id}\" "
                             f"AND title = \"{post_title}\" "
                             f"AND active = true;")
        post_id = self._cursor.fetchall()

        if not post_id:
            print(f"Post '{post_title}' of '{post_owner}' doesn't exist")
            return False
        else:
            post_id = post_id[0][0]

        timestamp = datetime.now().strftime(self._timestamp_format)
        if not to_comment_title:
            """ADD SIMPLE COMMENT"""
            self._cursor.execute(
                f"INSERT INTO COMMENTS "
                f"(post_id, user_id, title, text, create_time) VALUES "
                f"(\"{post_id}\", \"{user_id}\", \"{comment_title}\", "
                f"\"{comment_text}\", \"{timestamp}\");")
        else:
            """ADD COMMENT TO COMMENT"""
            if not to_comment_user:
                print('Incorrect syntax')
                return False

            self._cursor.execute(f"SELECT id FROM USERS "
                                 f"WHERE username = \"{to_comment_user}\";")
            to_comment_user_id = self._cursor.fetchall()
            if not to_comment_user_id:
                print(f"User '{to_comment_user}' doesn't exist")
                return False
            else:
                to_comment_user_id = to_comment_user_id[0][0]
            self._cursor.execute(f"SELECT id FROM COMMENTS "
                                 f"WHERE user_id = \"{to_comment_user_id}\" "
                                 f"AND post_id = \"{post_id}\" "
                                 f"AND title = \"{to_comment_title}\" "
                                 f"AND active = true;")
            parent_comm_id = self._cursor.fetchall()
            if not parent_comm_id:
                print(f"Comment '{to_comment_title}' of '{to_comment_user}' doesn't exist")
                return False
            else:
                parent_comm_id = parent_comm_id[0][0]
            self._cursor.execute(
                f"INSERT INTO COMMENTS "
                f"(post_id, parent_comm_id, user_id, title, text, create_time) VALUES "
                f"(\"{post_id}\", \"{parent_comm_id}\", \"{user_id}\", "
                f"\"{comment_title}\", \"{comment_text}\", \"{timestamp}\");")

        self._connection.commit()
        return True

    def get_comments(self, post_title=None, post_owner=None,
                     comment_user=None, sess_id=None, pretty=False):
        if post_title is None or post_owner is None or \
                comment_user is None or sess_id is None:
            return False

        user_id = self._authorised(sess_id)
        if not user_id:
            print('You are not logged in')
            return False

        # GET post_id of post owner
        self._cursor.execute(f"SELECT id FROM POSTS "
                             f"WHERE user_id = "
                             f"(SELECT id FROM USERS WHERE username = \"{post_owner}\") "
                             f"AND title = \"{post_title}\" "
                             f"AND active = true;")
        post_id = self._cursor.fetchall()

        if not post_id:
            print(f"Post '{post_title}' of '{post_owner}' doesn't exist")
            return False
        else:
            post_id = post_id[0][0]

        # GET comments of 'comment_user' in the post
        self._cursor.execute(f"SELECT title, text FROM COMMENTS "
                             f"WHERE active = true "
                             f"AND user_id = "
                             f"(SELECT id FROM USERS WHERE username = \"{comment_user}\") "
                             f"AND post_id = \"{post_id}\";")
        comments = self._cursor.fetchall()
        if comments:
            if pretty:
                t = PrettyTable(['Comment title', 'Text'])
                for comment in comments:
                    t.add_row(comment)
                return t
            else:
                lst = []
                for comment in comments:
                    lst.append(comment[0])
                return lst
        else:
            print("Active comments not found")
            return True

    def clear(self):
        DB.clear(self._cursor)
        self._cursor.execute(f'CREATE DATABASE {cfg.db};')
        self._cursor.execute(f'USE {cfg.db};')
        DB.create(self._cursor)
