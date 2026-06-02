from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Customer

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_url = reverse('register_customer')
        self.admin_url = reverse('register_admin')
        self.customer_login_url = reverse('customer_login')
        self.admin_login_url = reverse('admin_login')
        self.customer_dashboard = reverse('customer_dashboard')
        self.admin_dashboard = reverse('admin_dashboard')

    def test_customer_registration(self):
        response = self.client.post(self.customer_url, {
            'username': 'testcustomer',
            'password': 'password123',
            'email': 'customer@example.com',
            'phone': '1234567890',
            'address': '123 Street'
        })
        self.assertEqual(response.status_code, 302) # Redirects to dashboard
        self.assertTrue(User.objects.filter(username='testcustomer').exists())
        self.assertTrue(Customer.objects.filter(user__username='testcustomer').exists())

    def test_admin_registration(self):
        response = self.client.post(self.admin_url, {
            'username': 'testadmin',
            'password': 'password123',
            'email': 'admin@example.com'
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testadmin')
        self.assertTrue(user.is_staff)

    def test_customer_access_control(self):
        # Register and login as customer
        self.client.post(self.customer_url, {
            'username': 'cust', 'password': 'pw', 'email': 'c@e.com'
        })
        
        # Try accessing admin dashboard
        response = self.client.get(self.admin_dashboard)
        self.assertEqual(response.status_code, 302) # Should redirect (login_required + user_passes_test)

    def test_admin_access_control(self):
        # Register and login as admin
        self.client.post(self.admin_url, {
            'username': 'adm', 'password': 'pw', 'email': 'a@e.com'
        })
        
        # Access admin dashboard
        response = self.client.get(self.admin_dashboard)
        self.assertEqual(response.status_code, 200)

    def test_login_redirects(self):
        # Create users
        User.objects.create_user('c', 'c@e.com', 'pw')
        User.objects.create_user('a', 'a@e.com', 'pw', is_staff=True)

        # Login customer
        response = self.client.post(self.customer_login_url, {'username': 'c', 'password': 'pw'})
        self.assertRedirects(response, self.customer_dashboard)

        # Login admin
        self.client.logout()
        response = self.client.post(self.admin_login_url, {'username': 'a', 'password': 'pw'})
        self.assertRedirects(response, self.admin_dashboard)

    def test_duplicate_registration(self):
        # Register first time
        self.client.post(self.customer_url, {
            'username': 'dupuser',
            'password': 'password123',
            'email': 'dup@example.com',
            'phone': '123',
            'address': 'addr'
        })
        
        # Register second time with same username
        response = self.client.post(self.customer_url, {
            'username': 'dupuser',
            'password': 'password123',
            'email': 'dup2@example.com',
            'phone': '123',
            'address': 'addr'
        })
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['Username already exists.'])

class BookingTimeslotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        self.client.force_login(self.admin_user)
        
        from accounts.models import Tour, TourSupplier, Category, Country, DestinationRegion, City
        self.country = Country.objects.create(name="Denmark")
        self.supplier = TourSupplier.objects.create(company_name="Test Supplier", email="sup@ex.com", phone="123", address=" Copenhagen")
        self.category = Category.objects.create(name="Adventure")
        self.region = DestinationRegion.objects.create(country=self.country, name="Hovedstaden")
        self.city = City.objects.create(region=self.region, country=self.country, name="Copenhagen")
        
        self.tour = Tour.objects.create(
            supplier=self.supplier,
            category=self.category,
            destination_region=self.region,
            city=self.city,
            title="Copenhagen Tour",
            base_price=100.0,
            status="active"
        )
        
        from accounts.models import TimeSlot, TourTimeSlot
        self.timeslot = TimeSlot.objects.create(name="10:00 - 12:30", status="active")
        self.tour_timeslot = TourTimeSlot.objects.create(tour=self.tour, time_slot=self.timeslot)

    def test_get_tour_timeslots_api(self):
        url = reverse('get_tour_timeslots_api', kwargs={'tour_id': self.tour.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('timeslots', data)
        self.assertEqual(len(data['timeslots']), 1)
        self.assertEqual(data['timeslots'][0]['name'], "10:00 - 12:30")

    def test_booking_form_dynamic_choices(self):
        from accounts.admin_panel.forms_additions import BookingForm
        # Test without tour selection
        form = BookingForm()
        self.assertEqual(form.fields['tour_time_slot'].choices, [('', 'Select Tour First')])
        
        # Test with tour selection in data
        form = BookingForm(data={'tour': self.tour.id})
        choices = form.fields['tour_time_slot'].choices
        self.assertEqual(choices, [('', 'Select Time Slot'), ("10:00 - 12:30", "10:00 - 12:30")])
