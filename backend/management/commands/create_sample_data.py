"""
Custom management command to create sample data for development.
This creates users with proper password hashing and default notification preferences.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from apps.authentication.models import User
from apps.customers.models import Customer, Conversation
from apps.messaging.models import Message, InternalComment, CommentMention
import uuid


class Command(BaseCommand):
    help = 'Create sample data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='password123',
            help='Password for all sample users (default: password123)'
        )

    def handle(self, *args, **options):
        password = options['password']
        hashed_password = make_password(password)
        
        self.stdout.write(self.style.SUCCESS('Creating sample users...'))
        
        # Create System Admin
        admin_user, created = User.objects.get_or_create(
            email='admin@respondio.local',
            defaults={
                'id': uuid.UUID('11111111-1111-1111-1111-111111111111'),
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'password': hashed_password,
                'is_superuser': True,
                'is_staff': True,
                'role': User.Role.SYSTEM_ADMIN,
                'designation': 'System Administrator',
                'password_change_required': False,
                'password_last_changed': timezone.now(),
            }
        )
        if created:
            self.stdout.write(f'Created admin user: {admin_user.email}')

        # Create Manager
        manager_user, created = User.objects.get_or_create(
            email='sarah.johnson@respondio.local',
            defaults={
                'id': uuid.UUID('22222222-2222-2222-2222-222222222222'),
                'username': 'manager1',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'password': hashed_password,
                'role': User.Role.MANAGER,
                'designation': 'Sales Manager',
                'respond_io_account_id': 'mgr_001',
                'password_change_required': True,
            }
        )
        if created:
            self.stdout.write(f'Created manager user: {manager_user.email}')

        # Create Sales Representatives
        sales_user1, created = User.objects.get_or_create(
            email='michael.chen@respondio.local',
            defaults={
                'id': uuid.UUID('33333333-3333-3333-3333-333333333333'),
                'username': 'salesperson1',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'password': hashed_password,
                'role': User.Role.BASIC_USER,
                'designation': 'Sales Representative',
                'respond_io_account_id': 'sales_001',
                'password_change_required': True,
            }
        )
        if created:
            self.stdout.write(f'Created sales user: {sales_user1.email}')

        sales_user2, created = User.objects.get_or_create(
            email='emily.rodriguez@respondio.local',
            defaults={
                'id': uuid.UUID('44444444-4444-4444-4444-444444444444'),
                'username': 'salesperson2',
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'password': hashed_password,
                'role': User.Role.BASIC_USER,
                'designation': 'Senior Sales Representative',
                'respond_io_account_id': 'sales_002',
                'password_change_required': True,
            }
        )
        if created:
            self.stdout.write(f'Created sales user: {sales_user2.email}')

        self.stdout.write(self.style.SUCCESS('Creating sample customers...'))

        # Create Customers
        customer1, created = Customer.objects.get_or_create(
            phone_number='+1234567890',
            defaults={
                'id': uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
                'name': 'John Smith',
                'status': Customer.Status.ASSIGNED,
                'assigned_user': sales_user1,
                'respond_io_contact_id': 'contact_001',
                'email': 'john.smith@example.com',
                'language': 'en',
                'country_code': 'US',
                'first_contact_date': timezone.now() - timezone.timedelta(days=5),
                'last_message_date': timezone.now() - timezone.timedelta(hours=2),
                'assignment_history': [
                    {
                        'assigned_to': str(sales_user1.id),
                        'assigned_by': str(manager_user.id),
                        'assigned_at': (timezone.now() - timezone.timedelta(days=5)).isoformat(),
                        'previous_assignee': None,
                    }
                ]
            }
        )
        if created:
            self.stdout.write(f'Created customer: {customer1.name}')

        customer2, created = Customer.objects.get_or_create(
            phone_number='+1987654321',
            defaults={
                'id': uuid.UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                'name': 'Maria Garcia',
                'status': Customer.Status.ASSIGNED,
                'assigned_user': sales_user2,
                'respond_io_contact_id': 'contact_002',
                'email': 'maria.garcia@example.com',
                'language': 'es',
                'country_code': 'MX',
                'first_contact_date': timezone.now() - timezone.timedelta(days=4),
                'last_message_date': timezone.now() - timezone.timedelta(hours=1),
                'assignment_history': [
                    {
                        'assigned_to': str(sales_user2.id),
                        'assigned_by': str(manager_user.id),
                        'assigned_at': (timezone.now() - timezone.timedelta(days=4)).isoformat(),
                        'previous_assignee': None,
                    }
                ]
            }
        )
        if created:
            self.stdout.write(f'Created customer: {customer2.name}')

        customer3, created = Customer.objects.get_or_create(
            phone_number='+441234567890',
            defaults={
                'id': uuid.UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
                'name': 'David Wilson',
                'status': Customer.Status.UNASSIGNED,
                'assigned_user': None,
                'respond_io_contact_id': 'contact_003',
                'email': 'david.wilson@example.co.uk',
                'language': 'en',
                'country_code': 'GB',
                'first_contact_date': timezone.now() - timezone.timedelta(days=2),
                'last_message_date': timezone.now() - timezone.timedelta(days=1),
                'assignment_history': []
            }
        )
        if created:
            self.stdout.write(f'Created customer: {customer3.name}')

        self.stdout.write(self.style.SUCCESS('Creating sample conversations...'))

        # Create Conversations
        conv1, created = Conversation.objects.get_or_create(
            customer=customer1,
            defaults={
                'id': uuid.UUID('dddddddd-dddd-dddd-dddd-dddddddddddd'),
                'assigned_user': sales_user1,
                'status': Conversation.Status.ACTIVE,
                'respond_io_conversation_id': 'conv_001',
                'subject': 'Product Inquiry',
                'priority': 'normal',
                'last_message_at': timezone.now() - timezone.timedelta(hours=2),
                'message_count': 0,
                'internal_comment_count': 0
            }
        )
        if created:
            self.stdout.write(f'Created conversation: {conv1.subject}')

        conv2, created = Conversation.objects.get_or_create(
            customer=customer2,
            defaults={
                'id': uuid.UUID('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'),
                'assigned_user': sales_user2,
                'status': Conversation.Status.ACTIVE,
                'respond_io_conversation_id': 'conv_002',
                'subject': 'Support Request',
                'priority': 'high',
                'last_message_at': timezone.now() - timezone.timedelta(hours=1),
                'message_count': 0,
                'internal_comment_count': 0
            }
        )
        if created:
            self.stdout.write(f'Created conversation: {conv2.subject}')

        conv3, created = Conversation.objects.get_or_create(
            customer=customer3,
            defaults={
                'id': uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'),
                'assigned_user': None,
                'status': Conversation.Status.ACTIVE,
                'respond_io_conversation_id': 'conv_003',
                'subject': '',
                'priority': 'normal',
                'last_message_at': timezone.now() - timezone.timedelta(days=1),
                'message_count': 0,
                'internal_comment_count': 0
            }
        )
        if created:
            self.stdout.write(f'Created conversation for unassigned customer')

        self.stdout.write(self.style.SUCCESS('Creating sample messages...'))

        # Create Messages
        msg1, created = Message.objects.get_or_create(
            conversation=conv1,
            sender_type=Message.SenderType.CUSTOMER,
            defaults={
                'id': uuid.UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479'),
                'message_type': Message.MessageType.TEXT,
                'content': "Hi, I'm interested in your premium software package. Can you tell me more about the features?",
                'sender_customer': customer1,
                'status': Message.Status.READ,
                'read_by_user': True,
                'read_at': timezone.now() - timezone.timedelta(hours=2, minutes=50),
                'respond_io_message_id': 'msg_001',
                'created_at': timezone.now() - timezone.timedelta(hours=3),
                'sent_at': timezone.now() - timezone.timedelta(hours=3),
            }
        )
        if created:
            conv1.message_count += 1
            conv1.save()

        msg2, created = Message.objects.get_or_create(
            conversation=conv1,
            sender_type=Message.SenderType.USER,
            defaults={
                'id': uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'),
                'message_type': Message.MessageType.TEXT,
                'content': "Hello John! Thanks for your interest. Our premium package includes advanced analytics, custom integrations, and 24/7 support. Would you like me to schedule a demo?",
                'sender_user': sales_user1,
                'status': Message.Status.DELIVERED,
                'reply_to': msg1,
                'respond_io_message_id': 'msg_002',
                'created_at': timezone.now() - timezone.timedelta(hours=2, minutes=45),
                'sent_at': timezone.now() - timezone.timedelta(hours=2, minutes=45),
            }
        )
        if created:
            conv1.message_count += 1
            conv1.save()

        self.stdout.write(self.style.SUCCESS('Creating sample comments...'))

        # Create Internal Comment
        comment1, created = InternalComment.objects.get_or_create(
            conversation=conv1,
            author=sales_user1,
            defaults={
                'id': uuid.UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8'),
                'content': 'This customer seems very interested. High potential for conversion. @sarah.johnson should review the pricing options.',
                'priority': InternalComment.Priority.NORMAL,
                'is_private': False,
                'notify_assigned_user': True,
                'notify_managers': True,
                'created_at': timezone.now() - timezone.timedelta(hours=2, minutes=30),
            }
        )
        if created:
            conv1.internal_comment_count += 1
            conv1.save()
            self.stdout.write(f'Created internal comment')

            # Create Comment Mention
            mention1, created = CommentMention.objects.get_or_create(
                comment=comment1,
                mentioned_user=manager_user,
                mentioned_by=sales_user1,
                defaults={
                    'id': uuid.UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8'),
                    'position_start': 85,
                    'position_end': 99,
                    'notification_sent': True,
                    'acknowledged': False,
                }
            )
            if created:
                self.stdout.write(f'Created mention for {manager_user.full_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Sample data created successfully!\n\n'
                f'Login credentials (password: {password}):\n'
                f'- Admin: admin@respondio.local\n'
                f'- Manager: sarah.johnson@respondio.local\n'
                f'- Sales Rep 1: michael.chen@respondio.local\n'
                f'- Sales Rep 2: emily.rodriguez@respondio.local\n\n'
                f'Created:\n'
                f'- 4 users with different roles\n'
                f'- 3 customers (2 assigned, 1 unassigned)\n'
                f'- 3 conversations\n'
                f'- Sample messages and internal comments\n'
                f'- User mentions and notifications\n'
            )
        ) 