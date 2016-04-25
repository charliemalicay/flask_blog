import random
import datetime

user_list = ["person1", "person2", "person3", "person4", "person5"]
for u in user_list:
    new_user = User(u, "test")
    db.session.add(new_user)


tags = ["Python", "Flask", "SQLAlchemy", "Jinja", "Postgres"]
tag_list = []
for t in tags:
    new_tag = Tag(t)
    db.session.add(new_tag)
    tag_list.append(new_tag)




text = "Kale chips next level mlkshk, offal banh mi post-ironic portland brooklyn affogato keffiyeh pour-over deep v venmo. Normcore health goth +1, ramps deep v pabst beard kitsch mumblecore knausgaard meh ugh flexitarian photo booth cornhole. Umami ennui drinking vinegar, locavore cray ethical fixie tilde twee neutra kale chips thundercats gochujang single-origin coffee blog. 3 wolf moon pickled tote bag, gastropub YOLO lumbersexual vice food truck ethical truffaut brooklyn normcore ramps selvage everyday carry. Art party mixtape cred fingerstache, bespoke hella irony fap fixie twee messenger bag humblebrag umami. Four dollar toast readymade helvetica vegan, umami craft beer single-origin coffee. Brunch marfa pinterest XOXO, truffaut pickled synth artisan meh freegan bicycle rights sustainable +1."
for i in xrange(30):
    new_post = Post("Post " + str(i))
    new_post.user = User.query.get(random.randint(1, 5))
    new_post.publish_date = datetime.datetime.now()
    new_post.text = text
    new_post.tags = random.sample(tag_list, random.randint(1, 5))
    db.session.add(new_post)

db.session.commit()