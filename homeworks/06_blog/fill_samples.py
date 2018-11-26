import os
import blog as bg

blog = bg.Blog()
blog.clear()
sample_file = os.path.join(os.getcwd(), "name_samples.txt")
if not os.path.isfile(sample_file):
    raise ValueError
f = open(sample_file)
blog_count = 0

while True:
    line = f.readline()
    if not line:
        break
    # TO FILL USERS
    first_name, last_name, password = line.strip().split()
    username = (first_name + last_name).lower()
    blog.user_add(username=username,
                  first_name=first_name,
                  last_name=last_name,
                  password=password)

    if blog_count % 10 == 0:
        # TO FILL BLOGS
        sess_id = blog.login(username=username,
                             password=password)
        blog_title = f"{username}'s blog"
        blog.blog_create(title=blog_title,
                         description=f"{first_name} {last_name}",
                         sess_id=sess_id)

        for i in range(1, 101):
            # TO FILL POSTS
            post_title = f"{username}'s post #{i}"
            blog.post_create(
                title=post_title,
                text=f"Hello, world! I'm {first_name}",
                blogs=[blog_title],
                sess_id=sess_id)

            for j in range(1, 11):
                # TO FILL COMMENTS
                blog.comment_create(post_title=post_title,
                                    post_owner=username,
                                    comment_title=f"Comment #{j}",
                                    comment_text=f"My {j} comment in this post",
                                    sess_id=sess_id)

    blog_count += 1
f.close()
