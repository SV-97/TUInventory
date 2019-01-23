import unittest

try:
    import classes
    skip_classes = False
except:
    skip_classes = True

import slots

from utils import absolute_path


@unittest.skipIf(skip_classes, "Critical error in classes, can't import!")
class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        this.CSession = classes.setup_context_session(classes.engine)

    def test_user(self):
        user = classes.User("e@mail.com", "password")
        with self.CSession() as session:
            session.add(user)
            print(user.uid)
            session.expunge(user)

        print(user.uid)
        #self.assertEqual(user.e_mail, "e@mail.com")


if __name__ == "__main__":
    unittest.main()