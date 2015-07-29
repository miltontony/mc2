from organizations.tests.base import OrganizationTestCase
from organizations.models import Organization, OrganizationUserRelation


class TestOrganizationManager(OrganizationTestCase):

    def setUp(self):
        self.user1 = self.mk_user(username='user1', email='user1@gmail.com')
        self.user2 = self.mk_user(username='user2', email='user2@gmail.com')
        self.organization1 = self.mk_organization(
            users=[self.user1, self.user2])
        self.organization2 = self.mk_organization(
            users=[self.user1, self.user2])

    def test_for_admin_user(self):
        self.assertEqual(set(Organization.objects.for_admin_user(self.user1)),
                         {self.organization1, self.organization2})

        self.organization2.organizationuserrelation_set.filter(
            user=self.user1).update(is_admin=False)
        self.assertEqual(set(Organization.objects.for_admin_user(self.user1)),
                         {self.organization1})

        self.organization1.organizationuserrelation_set.filter(
            user=self.user1).update(is_admin=False)
        self.assertEqual(
            Organization.objects.for_admin_user(self.user1).count(), 0)

    def test_for_admin_user_inactive(self):
        self.user1.is_active = False
        self.assertEqual(
            Organization.objects.for_admin_user(self.user1).count(), 0)

    def test_for_user(self):
        OrganizationUserRelation.objects.update(is_admin=False)
        self.assertEqual(set(Organization.objects.for_user(self.user1)),
                         {self.organization1, self.organization2})

        self.organization2.organizationuserrelation_set.filter(
            user=self.user1).delete()
        self.assertEqual(set(Organization.objects.for_user(self.user1)),
                         {self.organization1})

        self.organization1.organizationuserrelation_set.filter(
            user=self.user1).delete()
        self.assertEqual(Organization.objects.for_user(self.user1).count(), 0)

    def test_for_user_inactive(self):
        self.user1.is_active = False
        self.assertEqual(
            Organization.objects.for_user(self.user1).count(), 0)
