import unittest
import blog as bg


class MyTestCase(unittest.TestCase):

    def test_blog(self):
        blog = bg.Blog()
        blog.clear()
        self.assertFalse(blog.blog_create('My first blog', 'Technical reviews', sess_id='random'))
        password = 'Pass123'
        self.assertTrue(blog.user_add('alex', 'Alexander', 'Kolue', password))
        password2 = blog.user_add('hannamon12', 'Hanna', 'Monta')
        sess_id = blog.login('alex', password)
        sess_id2 = blog.login('hannamon12', password2)
        self.assertTrue(blog.blog_create('My first blog', 'Technical reviews', sess_id=sess_id))
        self.assertTrue(blog.blog_create('My second blog', 'Nat Geo news', sess_id=sess_id))
        self.assertTrue(blog.blog_create('My third blog', 'Nat Geo Wild', sess_id=sess_id))
        self.assertTrue(blog.blog_edit(title='My first blog', new_title='My new blog', sess_id=sess_id))
        self.assertTrue(blog.blog_edit(title='My new blog', new_desc='NASA news', sess_id=sess_id))
        self.assertTrue(blog.post_create(title='Hello',
                                         text='Hi, all!',
                                         blogs=['My first blog', 'My second blog', 'Unreal blog'],
                                         sess_id=sess_id))
        self.assertEqual(['alex', 'hannamon12'], blog.get_users(sess_id=sess_id))
        self.assertTrue(blog.post_edit('Hello',
                                       new_title='Hello everyone!',
                                       new_text='Hello world!',
                                       new_blogs=['My second blog', 'My third blog'],
                                       sess_id=sess_id))
        self.assertFalse(blog.post_delete('Hello', sess_id=sess_id))
        self.assertEqual(['My new blog', 'My second blog', 'My third blog'],
                         blog.get_active_blogs(sess_id=sess_id))
        self.assertTrue(blog.blog_delete('My second blog', sess_id=sess_id))
        self.assertTrue(blog.post_delete('Hello everyone!', sess_id=sess_id))
        self.assertTrue(blog.post_create(title='Hello',
                                         text='Hi, all!',
                                         blogs=['My new blog', 'My second blog'],
                                         sess_id=sess_id))
        self.assertTrue(blog.blog_create("Hanna's blog", "Hanna's interviews", sess_id=sess_id2))
        self.assertTrue(blog.post_create(title="My first post",
                                         text="Hi, all! I'm Hanna",
                                         blogs=["Hanna's blog"],
                                         sess_id=sess_id2))
        self.assertEqual(['My new blog', 'My third blog', "Hanna's blog"],
                         blog.get_active_blogs(sess_id=sess_id2))
        self.assertTrue(blog.comment_create(post_title="My first post",
                                            post_owner="hannamon12",
                                            comment_title="First comment",
                                            comment_text="You are done great job!",
                                            sess_id=sess_id))
        password3 = blog.user_add('johnS', 'John', 'Sours')
        sess_id3 = blog.login('johnS', password3)
        self.assertTrue(blog.comment_create(post_title="My first post",
                                            post_owner="hannamon12",
                                            comment_title="Second comment",
                                            comment_text="It's a cool blog, Hanna!",
                                            sess_id=sess_id3))
        self.assertTrue(blog.comment_create(post_title="My first post",
                                            post_owner="hannamon12",
                                            to_comment_title="First comment",
                                            to_comment_user="alex",
                                            comment_title="Comment to comment",
                                            comment_text="Hello, Alexander!",
                                            sess_id=sess_id3))
        self.assertTrue(blog.comment_create(post_title="My first post",
                                            post_owner="hannamon12",
                                            comment_title="Third comment",
                                            comment_text="I like it!",
                                            sess_id=sess_id))

        self.assertEqual(['First comment', 'Third comment'],
                         blog.get_comments(post_title="My first post",
                                           post_owner="hannamon12",
                                           comment_user="alex",
                                           sess_id=sess_id))


if __name__ == '__main__':
    unittest.main()
