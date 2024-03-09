from unittest import TestCase

from app import app
from models import db, User, Post, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyUserViewsTestCase(TestCase):
    """Tests Blogly View Functions."""

    def setUp(self):
        """Add John Doe as Test User."""

        User.query.delete()
        Post.query.delete()
        Tag.query.delete()

        user = User(first_name='John', last_name='Doe')

        db.session.add(user)
        db.session.commit()

        post = Post(title='Very Happy Days!', content='There are days, when people are happy!', user_id=user.id, created_at="2024-03-07 15:42:19.872619")

        db.session.add(post)
        db.session.commit()

        tag = Tag(name='Cool')

        db.session.add(tag)
        db.session.commit()

        self.user_id = user.id
        self.user = user

        self.post_id = post.id
        self.post = post

        self.tag_id = tag.id
        self.tag = tag

    def tearDown(self):
        """Clean up left over transactions."""

        db.session.rollback()

    def test_user_list(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertIn('John Doe', html)
            self.assertEqual(resp.status_code, 200)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertIn('<h1 class="display-2">John Doe</h1>', html)
            self.assertIn(f'<p class="display-6">ID: {self.user_id}</p>', html)
            self.assertIn('src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"', html)
            self.assertEqual(resp.status_code, 200)

    def test_add_user(self):
        with app.test_client() as client:
            new_user_info = {'first_name':'Jane', 'last_name':'Smith', 'image_url':'https://contentgrid.homedepot-static.com/hdus/en_US/DTCCOMNEW/Articles/discover-the-secret-language-of-flowers-2022-thumbnail.jpeg'}
            resp = client.post("/users", data=new_user_info, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn('<h1 class="display-2">Jane Smith</h1>', html)
            self.assertIn('<p class="display-6">ID: 2</p>', html)
            self.assertIn('src="https://contentgrid.homedepot-static.com/hdus/en_US/DTCCOMNEW/Articles/discover-the-secret-language-of-flowers-2022-thumbnail.jpeg"', html)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):
        with app.test_client() as client:
            delete_action_call = {'ACTION':'delete'}
            resp = client.post(f"/users/{self.user_id}", data=delete_action_call, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn('John Doe', html)
            self.assertEqual(resp.status_code, 200)

    def test_edit_user(self):
        with app.test_client() as client:
            edit_data = {'first_name':'Walter', 'last_name':'White', 'image_url':'data:image/jpeg;base64,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'}
            resp = client.post(f'/users/{self.user_id}/edit', data=edit_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn('<h1 class="display-2">John Doe</h1>', html)
            self.assertIn('<h1 class="display-2">Walter White</h1>', html)
            self.assertIn(f'<p class="display-6">ID: {self.user_id}</p>', html)
            self.assertIn('src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIALoAiwMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAEAQIDBQYHAAj/xAA+EAACAQMDAQYDBAgFBAMAAAABAgMABBEFEiExBhMiQVFhMnGBBxRCkRUjM1JiobHBcnPR4fA0U4OSFiRj/8QAGAEAAwEBAAAAAAAAAAAAAAAAAAECAwT/xAAhEQEBAAIBBQADAQAAAAAAAAAAAQIRIQMSEyIxBEFRMv/aAAwDAQACEQMRAD8ApdlOCVJilA9qDRhaeEqRUqVY/agIljqVYuOlA61rVnosQM5LzMPBCnxH39hWH1HtZqt6SEm+7xeSQjH5nrRsOjuY4hmWREH8TAUO2qaZHw+oWw/8orkrs8p3Suzt5ljkmkwPSi03W01bSmPh1G1P/lFFxTW8/wCxnik/wODXGKlhYo4KHafUVIdnMeOtJtrn2l9ob+z2gTGWIHmOTxA/L0rf6bdw6jZpcQdDwynqp9DRLsztozTsVJspQtMtowtPCYFSBacFoBgUYpdtShfanCOg1HspQtSBTT1joIxEpNQuU0/T7i8kGRChbb+8fIUXHH7VUduB3fZa8I4zsX82FMq5Ze3c15dSXNy5eWRssT/SoRXsZNTJCSMngUqaMUtTrEBTto9BS2AtOTrUxQegp0KKTjFGzEW3Tmtr2Bm/W3FsT8Y3ge461k7aBSecjPoK0XZUG01iCV2xCTsYngDPrUb1VWbjd90fQ17uz6GrEw89KQxD0rVmCEdOCYoru/al2UAOFp+2pglO7ukFAsdTJFUkaZ4qg7V9qotAK28EQmvXXcAx8KDyJ9flRoNJHDms19os8CdnJrbvU75pExHuG7rnpWA1HtRrGo5E97Iqf9uLwL/KqcnJJJyTyTTB6eFsmpe9HXmhxXqk4IMw/dpvfe1Nit5peIonf/CpNErpGoldws5seu2lwrtv8D98T5ClWdlOQKIOj6gF3G0lA+VL+h7/ADg2z5o3iOzL+Ikv50+Fx+VExazdxq6AoyuMMrLkEUK9jcp8ULCoWjZeqkUcDmNpD9pWtow76KzlX/LIz/Orex+05GKi/wBNKjzaB84+hrmYFPWnspI+hOzd/Y9pIhJp9wNgO2TeMGM+hHlVtqWlSWOwlhJG44dfWuc/YL3sWs6nP3Tvbm2WN8DgsWyPrjP511zUre5a3Oy3dYAcjPUfSjZa1WcC08ITRtpp9xdlvu8e7HU5xii/0Ff+cQ/9hTNlIYtzAHhc8mubfaxos1pr36SjjJs7uNArjOFdVClT6E4z9a6hCo6McCjBDb3dvJZ3scc1rKMSRyDhh/zzoJ80Hg16ur9pvsmBmefszeRvEefutw2Cvsr+f1xWCvuymu2Dypd6bNGYly3Gcj1GOoo3BN34K7Ndmm1MrLclkgPQDq1b7TezOkWmCtojN5s/NAdm7uKaxtQjpvWMBlBGVOB1rQCXbgKCzE8heTXJ1Mra7ulhjJsbDDCi4htwF/hUCorpZERQqybc8kEdfWq267R2NhcyW94jiaM7WVVyyn0PpUD9sNJKssYuctg/Bwp/OokrTuxGd+sm+NnYEtwG6028t9rjxHcylvpiqtdVjvjczWmR3T78/M/7V6+7UwF2PcSyuqEBU9+tGqfdFfdKWJYMSF6emao59NkvorpoQhkiheVhnHhXkmiZtSvZCSmnuqN4hwePriiNAvIDPdQ38cxSe3eJu4UGRQQc4B4/OtsZqubO7YdQSQByScADzre9j/su17tB3dxcwvp9ieTLOhDsP4VPP1PHzrbfZNo2lWuiw6utpDJfSSSZdxvMQDYC5PmBjkAV1GHVZZiESAsxHlXQ5bdcKbs1otp2YtVtNLjxGgwWPJZvNifWryz1IEstw3TzxUSWjZzKyxE8kA5JohLNGBwAT/FSBkd/bpIzQKQHOW9zRAvkIzio4rNozjajURsP/aH5CgcMA9pEIt0Mu4jqDUC5B6VZTRWzyMQ2zPkvSmpZRsvhdvqKnZ2IIS2eCfpVTrUch1W2dz4WiwPoTWkitHjOUIY+lAdrrQnTVuliYSw9AB5H/fFT1OcW34/rnyxmr6ZYG4QR26RnLFjHwQ3qCKCv7DUV7v7q/expHgiTOSc53Z+oH0qWCNYrOKUOx7yZixbyq/t8SwA7iMVzSuy4xjksNVn08PCYbdGGTvQOzn1J9c0BZ6PPNexx3bblbh22ADOfLFbvS7m2tdKiimljWVVIdGO1s/WhZdSsY0YW+ya4x4Ej5wfeq7qjsilWztr+S6gEbiC2O0IMoGfzPv0rIXSrp+pyxq7pA3xBfMeWa3lqhijKs+535ds9SaxnaC3Iv+SADkZbpVYjq46xFvbSPYxzW91dGJkHWQkDjpRvZLR7++1i1kRFMaSKJXYHaRkdfn6VDpiy21mIrmGVYGwVZfEFJ8uPKtRpOpwrJb2Nqpgt3IVn6MV/F75I8z0otsqJj+3Svs60+zsex1p3AjeJ90m8IBnnGf5VdNdqobudqKPPFV+i2DafpUVnHKFSMEbIxhVBJOF9hmpHsIWkKd/JzyciujnTjsltExzqiGcSB/Iii0mMkKzIuR7VTR6XtZhHdMKJ+73aRFUvPkMUS0aWav3uFYMrdc1MCQMEGs93t3G2JGYkUX+kphxgU9lpS7VJ5A3euKfbJGqYZ/BnkjyqueWbYpiZDnyzzQ6NeDI28day21Xn3lIJQYQzZ45HWpLx49Qt2tWQrvXbn2NU9m8pcBztq0ik8XJ+E+Qp7L45pqVn3Kz+Eho3AkXJwSDjPt1qbTZ2SIk8c81vNa02x1G2l7yJGmZCA/Q5xxXOdNbO1WBKtgcVhnh2uzp9TvjQ7ILlf18UcgH76g1RyOZ7i4SxjVLeEeMqoG4+gxS3WppaWUrsSqRDLZ/pWIn7VXD4hgTbHkkgeZPmaWMtXlnMWohvIjveS2lERyMtxj3rKa1qdtJMkQIfBwSDzVcNRukeQRSOFcgYqQXzpMXeFA0g8ZC4zWsx1WWfV3NLDszqM6TNbyOxtxxhh0Fa7s9bC47U6Z3eZIxIzMf3gvNYOylzO7xOsZZT4ScK1dR+zINJrHiXDQWytj/Fn+wFLKcpmXq6KJXjYlTk586azyyPnnPtRcv6wZbaMedMeHCgq4OfStnGhUT/AIc596cGkHUtT0Ming1IC2c0GiKyudzAmk2N5g0WpcDJbim7082NMnPvvcOfAjfnRltdoVx4unQmsjFqiM+xJFYivS66Lfh5VUg8gDJrHvjfx5NvDdBOdoon7+4UhQOfKsMe0uxgDIvPPw1lu1Xbu4eJ7LS5toYYknQYIHovp86rGy1GWFk5antj9okGjiSz05Uub8DDsTlIT746n2/Oq6wmETQtISV4P0rlioXhc9S3NdS0sJd6XbndwY12uOopdbiNfxvtB9tIwNKlMTcGQM/PWqHs1pcN2hkmlZQeF24q17Zq66bAjtiTvMNjowweazlhdyQ4jt15I25qMZ6tM9TPlorzTtGjw33mXcDjI8qqryGwYB4ppWZemXoaUO5ZVkJxy2aECsoId/PypyJyylERRRxyp8Q5A3nnFdj+zCIG61W9fwhO5tVPQEqgLY/9hXF4Zf8A7OwYbB4Gc5xWkXv7q6aCzvmjEOBs3EAHHXr15qvnKP8AU1HeZZweCVx7mvJPEBjvowPdxXDG0q+nOP0oZCOuXP8ArUUmiSAZmuzjGcZJP9aPJE+J3tbq2BwbmAH/ADBTTqNiODewc/8A6D/WuDw6DGwV2uX6HPFSppFsAZC8yKvG71FLyH4ncxq+mDj9IW3y71aYdZ0YHnUrQH/NFcTS1geTbGWLjpnjipzZ27ncxYk9TmjyDxRQxalcPdO0NzFGgTKt3eM/Soo9Rnmi33F9huQF7rJNCaj2ikubZYEhjjHRjGuM+1UvfyNnLYBOdo6GnMBc9LGfV70wtEZmwRtPlxVNJU7HIzQ8ta4zTLK2joFG1ePKtL2U1lbNv0fdNtjckxOfwnzWszakGJcfL/n86kmQSoy55xkH3qcpvinhlcbuOh67ZfpPT5Ih+0XxR+zelYVBJbtiVGVumDx/zirbQO0bOq2l/KVccRy46+xq8vYoZ1K3EaPgdcVlzjw6rJ1PaMZ3rRO6g9TjPr6UPJIxbHryKNubVQQIx4iTx7UJKLiAhYyO8fgYq5ywy2ttD0kztPdTeEQoTGPMnBxn2qr7PXjJqneSMdsn7Q+nv9K0JJ0bs3LIWzKxAUHzJwD/AHrJaT/18RzgbuTVTmVG/aNto3326u5rGGeNCMsQ554PIHrVtqNuNP0pjqN8ivjC7F5J9KyV7PJDemeFikobcpX8Jp91etqjl7t3MpXHB4rK4tpkKl15UjRLXcp/eJ5q8sdVgfTCJ13PgADzrJS2ZwpQhx5kDp9KdbS/d7jAkBUdPelcTmTUfp5O93JBGGG4KR8qy80erTSvL3p8ZzwSBWi0qfTr8fcr+2RJSSVkXzqzHZyBPDFczBB0HFTvR2bcoLUgNNpwrqcyX8NRSr4c1IelRvypohU6ykw2w+fI+dHA45/4Kqo22OG9DmrYcjI6Hn6UspyUQzQqWDcqOuR5VqOzkV7qsf3GGaCSXH6vvJe7JH16/nWVuiwCopwxJqa1n7qDvMOpTlGHBBo1uKxzuN4dD/8AhGqW0bT3sCQIo+JpUA/PNYy9e3sdYUXE8cqhusDiQKM+ZHn8qr9W1nUtcMZ1C8kmWJcRox4X5D+/WhbWza4uobeNgHkbAJ6CiYSKy6lq67YXyypa20LZTb3pPrnp/KqXTP8Aqlp+qKGv5lhOY4j3SZ8wvH9qjg/UTI2fnT1qaRPu17d53g+o5oTIySAfCeooyfxID7ZoSEZeSs2iS2vHVxGx5HT1qd2t5pD38ZVh0dev19aqbrjDqeUP8qnim7zBHBzzT1wNr7T7ZyyyQyI4HwuD/UVeR3eoRoFFtuA/Fu61joriSKQ9y5R1OePOrFe1t/EojMaOV43Ecn+dZ3CrmUZA9aUUjda9XQwS/gph6UueMV7pzSCFl280bZzBwYyefw/6UKxDZ9BSYZfEBgetPW0iZizdzuz154xUt4dsRGM7uFpIpVnDiTG9s5/tTH3GYB/wpwP70jMij2ryOef6UTAzwzLNEcSKcqfQ8GowMuR7/wBqkUgDPpg/ypbMO3MpYnJLEk0sSpJIVcZHl7Ui/AT75p9pjvuRzT2ci1hJaFFLZdRj5io4xsk54zSXDGO2MqybXiI8PkR6V6C+tZwu9tj+ef7VGr9VuIp1UEZHGeflQUWYZypJxmrWUIy5DZwevqKBvVUESAjjHn1pwVJcP3U6v+E9TTZVJkJHSpJU760z5gUIl4yIFKA44yaJu/AFPWlGKTzr1Wg7cvpTGyflSgUpGRTBEHFSIM5XoG61EvBqRTtYfOkSKNsSKferGMCUrnrsINVxG2XHvR6Eq67fUilkIllaMTpEoCgAEk/Kon4Rseaf0JrwyGDZPQH+demP06ikaEfCT65pgfY2RUhH6r0OQaglPh96cnIpryu4IYnBOcZpqKWOACfairNIjjeoPzosbUbwAAe1O5FIrlBDAEkc9OlSFQGzij5kTh9o3etCMMmp2cg+2I7rHtQEsDd43HnRUBwtP3+1SpU+dLSV6tEwtKelJXvKgGedP60w05aChJ/jB9qNHhdD/EP6UFN8Q+QoxvhT5rRkIkPw49FI/Ko5/gP+If0qRun0amS/D9UqDqOX9mmPQUPMMEZomb9nH8zQ8/wp8j/WrxIsJxijYmzQCdaLg61NVBM3wUJ580XL8NCN8VI6IhNLkeppkfQfOlPWgP/Z"', html)

    def test_display_user_posts(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertIn(f'{self.post.title}', html)
            self.assertIn('<h2 class="display-6">Posts</h2>', html)
            self.assertEqual(resp.status_code, 200)

    def test_show_user_post_and_correct_date_formatting(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/post/{self.post_id}/{self.post.title}")
            html = resp.get_data(as_text=True)

            self.assertIn(f'<h1 style="margin-bottom:0;" class="display-5">{self.post.title}</h1>', html)
            self.assertIn(f'{self.post.content}', html)
            self.assertIn('<i>By John Doe on Thursday, March 07, 2024, 03:42 PM</i>', html)
            self.assertEqual(resp.status_code, 200)

    def test_add_user_post(self):
        with app.test_client() as client:
            sample_post_data = {"title": "Sad Depressing Nights...", "content": "There are nights... when even the best of us get sad..."}
            resp = client.post(f'users/{self.user_id}/new-post', data=sample_post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn(f'<h1 style="margin-bottom:0;" class="display-5">{sample_post_data["title"]}</h1>', html)
            self.assertIn(f'{sample_post_data["content"]}', html)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user_post(self):
        with app.test_client() as client:
            delete_action_call = {'ACTION': 'delete'}
            resp = client.post(f'users/{self.user_id}/post/{self.post_id}/{self.post.title}', data = delete_action_call, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn(f'Very Happy Days!', html)
            self.assertIn('<h2 class="display-6" style="margin-top:50px; margin-bottom:50px;">No Posts</h2>', html)
            self.assertEqual(resp.status_code, 200)

    def test_edit_user_post(self):
        with app.test_client() as client:
            edit_post_data = {"title":"No more being happy!!", "content":"JUST NO MORE!!!!!"}
            resp = client.post(f'users/{self.user_id}/post/{self.post_id}/{self.post.title}/edit', data=edit_post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn(f'Very Happy Days!', html)
            self.assertNotIn(f'There are days, when people are happy!', html)
            self.assertIn(f'<h1 style="margin-bottom:0;" class="display-5">{self.post.title}</h1>', html)
            self.assertIn(f'{self.post.content}', html)
            self.assertIn(f'<i>By John Doe on Thursday, March 07, 2024, 03:42 PM</i>',html)
            self.assertEqual(resp.status_code, 200)

    def test_tag_list(self):
        with app.test_client() as client:
            resp = client.get('/tags')
            html = resp.get_data(as_text=True)

            self.assertIn('Cool', html)
            self.assertIn('<h1 class="display-2">Tags</h1>', html)
            self.assertIn('<h2 class="display-6">Add tag</h2>', html)
            self.assertEqual(resp.status_code, 200)

    def test_tag_add(self):
        with app.test_client() as client:
            resp = client.post('/tags', data={'tag_name':'Awesome!'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn('Awesome!</h1>', html)
            self.assertIn('ID: 11', html)
            self.assertIn('No posts', html)
            self.assertEqual(resp.status_code, 200)

    def test_tag_delete(self):
        with app.test_client() as client:
            resp = client.post(f'/tags/{self.tag_id}', data={'ACTION':'delete'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn('No Tags', html)
            self.assertEqual(resp.status_code, 200)

    def test_tag_edit(self):
        with app.test_client() as client:
            resp = client.post(f'/tags/{self.tag_id}/edit', data={"tag_name": 'Uncool!'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn('Uncool!', html)
            self.assertNotIn('Cool', html)
            self.assertEqual(resp.status_code, 200)