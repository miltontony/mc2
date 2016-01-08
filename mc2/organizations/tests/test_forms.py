from mc2.organizations.tests.base import OrganizationTestCase
from mc2.organizations.forms import OrganizationFormHelper


class TestForms(OrganizationTestCase):

    def setUp(self):
        self.user = self.mk_user()
        self.organization = self.mk_organization(users=[self.user])

    def form_data(self, form):
        return dict((field.html_name, field.value()) for field in form)

    def formset_data(self, formset):
        initial = self.form_data(formset.management_form)
        for form in formset:
            initial.update(self.form_data(form))
        return initial

    def org_form_data(self, form_helper):
        initial = self.form_data(form_helper.organization_form)
        initial.update(self.formset_data(form_helper.users_formset))
        initial.update(self.formset_data(form_helper.new_users_formset))
        return initial

    def test_organization_form(self):
        data = self.org_form_data(
            OrganizationFormHelper(instance=self.organization))
        data['organization-name'] = 'New Name'
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertTrue(form.is_valid())
        saved_org, _, _ = form.save()
        self.assertEqual(self.organization, saved_org)
        self.assertEqual(saved_org.name, 'New Name')

        # missing name field
        data['organization-name'] = None
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.organization_form.errors['name'],
                         [u'This field is required.'])

    def test_organization_form_add_user(self):
        new_user = self.mk_user(
            username='new_user', email='new_user@gmail.com')
        data = self.org_form_data(
            OrganizationFormHelper(instance=self.organization))
        data['new_users-0-email'] = 'new_user@gmail.com'
        data['new_users-0-is_admin'] = True
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertTrue(form.is_valid())
        _, _, [saved_user_relation] = form.save()
        self.assertEqual(new_user, saved_user_relation.user)
        self.assertTrue(saved_user_relation.is_admin)

        # email does not exist
        data['new_users-0-email'] = 'doesnotexist@gmail.com'
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.new_users_formset[0].errors['email'],
                         [u'A user with this email does not exist.'])

    def test_organization_form_delete_user(self):
        data = self.org_form_data(
            OrganizationFormHelper(instance=self.organization))
        data['users-0-DELETE'] = True
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertTrue(form.is_valid())
        saved_org, _, _ = form.save()
        self.assertEqual(saved_org.users.count(), 0)

    def test_organization_form_change_user(self):
        data = self.org_form_data(
            OrganizationFormHelper(instance=self.organization))
        data['users-0-is_admin'] = False
        form = OrganizationFormHelper(data, instance=self.organization)
        self.assertTrue(form.is_valid())
        _, [updated_user_relation], _ = form.save()
        self.assertEqual(self.user, updated_user_relation.user)
        self.assertFalse(updated_user_relation.is_admin)
