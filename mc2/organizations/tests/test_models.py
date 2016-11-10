from django.contrib.auth.models import Group

from mock import Mock

from mc2.organizations.tests.base import OrganizationTestCase
from mc2.organizations.models import Organization, OrganizationUserRelation


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

    def test_for_admin_user_is_superuser(self):
        self.user1.is_superuser = True
        OrganizationUserRelation.objects.filter(user=self.user1).delete()
        self.assertEqual(set(Organization.objects.for_admin_user(self.user1)),
                         {self.organization1, self.organization2})

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

    def test_for_user_is_superuser(self):
        self.user1.is_superuser = True
        OrganizationUserRelation.objects.filter(user=self.user1).delete()
        self.assertEqual(set(Organization.objects.for_user(self.user1)),
                         {self.organization1, self.organization2})

    def test_for_user_inactive(self):
        self.user1.is_active = False
        self.assertEqual(
            Organization.objects.for_user(self.user1).count(), 0)


class TestRelationPermissions(OrganizationTestCase):

    def setUp(self):
        self.user = self.mk_user()
        self.organization = self.mk_organization(users=[self.user])
        self.relation = self.organization.organizationuserrelation_set.get(
            user=self.user)

    def test_permissions(self):
        group = Group.objects.create(name='Foo')
        self.grant_perms(group, 'organizations.add_organization')
        self.grant_perms(self.relation, 'organizations.change_organization')
        self.grant_perms(self.user, 'organizations.delete_organization')
        self.relation.groups.add(group)
        self.assertEqual(set([
            'organizations.add_organization',
            'organizations.change_organization']),
            set(self.relation.permissions()))

    def test_has_perms_no_user_perms(self):
        perms = ['organizations.add_organization']

        self.assertFalse(self.user.has_perms(perms))
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.relation.is_admin)
        self.assertTrue(self.relation.has_perms(perms))

        self.relation.is_admin = False
        self.assertFalse(self.relation.has_perms(perms))

        self.grant_perms(self.relation, perms)
        self.assertTrue(self.relation.has_perms(perms))

        self.user.is_active = False
        self.relation.user = self.user
        self.assertFalse(self.relation.has_perms(perms))

    def test_has_perms_with_user_perms(self):
        perms = ['organizations.add_organization']
        self.grant_perms(self.user, perms)
        self.assertTrue(self.user.has_perms(perms))
        self.relation.is_admin = False
        self.assertTrue(self.relation.has_perms(perms))

        self.user.is_active = False
        self.relation.user = self.user
        self.assertFalse(self.relation.has_perms(perms))

    def test_has_perms_for_obj(self):
        perms = ['organizations.add_organization']
        obj = Mock(organization=self.organization)
        self.assertTrue(self.relation.has_perms(perms, obj=obj))
        obj = Mock(organization=self.mk_organization(name='Other Foo'))
        self.assertFalse(self.relation.has_perms(perms, obj=obj))

    def test_organization_has_perms_no_relation(self):
        perms = ['organizations.add_organization']
        self.organization.organizationuserrelation_set.all().delete()
        self.assertFalse(self.organization.has_perms(self.user, perms))
        self.user.is_superuser = True
        self.assertTrue(self.organization.has_perms(self.user, perms))

    def test_organization_has_perms_with_relation(self):
        perms = ['organizations.add_organization']
        self.assertTrue(self.organization.has_perms(self.user, perms))
        self.relation.is_admin = False
        self.relation.save()
        self.assertFalse(self.organization.has_perms(self.user, perms))
