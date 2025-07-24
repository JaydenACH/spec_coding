# Application Specification

## Project Overview
<!-- Provide a high-level description of your application -->

### Project Name
Respond IO Alternate Interface

### Purpose
<!-- What problem does this application solve? What is its main goal? -->

### Target Audience
<!-- Who will be using this application? -->

## Functional Requirements

### Core Features
<!-- List the main features and capabilities of your application -->

1. **Feature 1**
   - Description: Chat with customers 
   - User story: When the customer first chat to the respond.io account, manager will receive the notification and manager will have to assign the customer to a salesperson. The salesperson should receive the notification about that assignment. Then he will continue to reply and chat with the customer.
   - Acceptance criteria:
     - [ ] Receives WhatsApp message from customer
     - [ ] Manager assigns customer to salesperson
     - [ ] Salesperson replys and send the message to customer
     - [ ] Realtime messaging experience

2. **Feature 2**
   - Description: Tag other salesperson to a chat with customer
   - User story: Similar to Respond.IO feature, rather that sending a message to the customer, salesperson A can tag salesperson B in the comment within the customer chat. The comment is not visible to the customer, only visible to the salespersons.
   - Acceptance criteria:
     - [ ] Salesperson A tag salesperson B in a comment within a customer chatbox
     - [ ] The comment is only visible to the salesperson
     - [ ] Salesperson B will receive notification when get tagged

### User Authentication & Authorization
<!-- If applicable, describe how users will sign up, log in, and what permissions they'll have -->

- Registration process: This application is an internal usage application. There will not be registration process for outsiders to get an account to access this system. The system admin will create a new user for the staff and a default password. Upon first login, user will be prompted to change password.
- Login/logout functionality: The users will use their new password to login and logout from the system. Each user in the system will also have a correspondent respond.io account to login to respond.io.
- User roles and permissions: There will be 3 types of user roles. Here are their permissions:
  - Basic User: They can login to chat with the customers. After they had been assigned a customer, they can view all their assigned customers in a list view. They cannot see other customers that are assigned to other users. They are the salesperson. 
  - Manager: They will receive first notification when an unassigned customer texted to the respond.io account. Manager will assign the customer to a user. Manager can view all the customers and have the ability to reassign customer to another salesperson or user.
  - System Admin: They will have the access to manage user accounts, force reset on account password, sees everything the manager is seeing. They can also be assigned a customer to chat.
- Password requirements: minimum 8 characters, with alphanumeric comnbinations and at least one uppercase and one number.

### Data Management
<!-- Describe what data your application will handle -->

- Data types and entities:
  - **Users**: id, username, email, password_hash, role (salesperson, manager, admin), respond_io_account_id, created_at, updated_at, last_login, password_expiry_date, designation
  - **Customers**: id, phone_number, name, first_contact_date, status (assigned, unassign), assigned_user_id
  - **Conversations**: id, customer_id, assigned_user_id, status (active, closed), created_at, updated_at
  - **Messages**: id, conversation_id, sender_type (customer, salesperson), sender_id, content, message_type (text, image, file), timestamp, respond_id_message_id
  - **Files**: id, message_id, file_name, file_type (image, pdf, document), file_size, file_path, file_url, thumbnail_url, upload_user_id, respond_io_file_id, created_at
  - **Internal_Comments**: ID, conversation_id, commenter_user_id, tagged_user_ids, content, timestamp, is_read
  - **Notifications**: ID, user_id, type (assignment/tag/new_message), content, is_read, created_at

- Data relationships:
  - Users can be assigned multiple Customers (one-to-many)
  - Customers have one active Conversation at a time (one-to-one)
  - Conversations contain multiple Messages (one-to-many)
  - Messages can have multiple Files attached (one-to-many)
  - Conversations can have multiple Internal_Comments (one-to-many)
  - Users can receive multiple Notifications (one-to-many)
  - Internal_Comments can tag multiple Users (many-to-many)
  - Users can upload multiple Files (one-to-many)

- Data validation rules:
  - Phone numbers must be in valid WhatsApp format
  - User passwords must meet complexity requirements
  - Only managers and system admins can assign customers
  - Basic users can only view their assigned customers
  - Message content cannot be empty (unless it's a file-only message)
  - Internal comments are never sent to customers
  - When an assigned customer sends a message, only the assigned user will get notified
  - File uploads limited to 10MB maximum size
  - Allowed file types: images (jpg, png, gif), documents (pdf, doc, docx), text files (txt)
  - File names must be sanitized to prevent security issues
  - Only assigned salesperson can download customer files

- Data storage requirements:
  - Real-time data sync with Respond.IO API
  - Message history retention for at least 1 year
  - User activity logs for audit purposes
  - Encrypted storage for sensitive customer data

## User Interface Requirements

### Pages/Screens
<!-- List all the pages or screens in your application -->

1. **Login Page**
   - Purpose: User authentication and first-time password change
   - Elements: Username field, password field, "Change Password" modal for first login, "Forgot Password" button for password reset
   - User interactions: Login, password change prompt for new users, Password Reset
   - Password reset is to send a notification to the system admin to force reset. User are not allowed to reset themselves.

2. **Dashboard (Manager/System Admin)**
   - Purpose: Overview of all customers (assigned or unassigned) and system status
   - Elements: Unassigned customer list, Assigned customer list, assignment actions, notification panel, customer statistics
   - User interactions: Assign customers to salespersons, view all conversations, search customers

3. **Dashboard (Basic User/Salesperson)**
   - Purpose: View assigned customers, tagged customers and active conversations
   - Elements: Assigned customer list, tagged customer list, active conversation indicators, notification panel
   - User interactions: Select customer to chat, view conversation history

4. **Chat Interface**
   - Purpose: Real-time messaging with customers and internal commenting
   - Elements: Message history, message input, customer info sidebar, internal comment section, typing indicators
   - User interactions: Send messages to customer, add internal comments, tag other salespersons

5. **Customer Management (Manager/System Admin)**
   - Purpose: Manage customer assignments and view all customer data
   - Elements: Customer list with filters, assignment controls, customer details, conversation history
   - User interactions: Search customers, reassign customers, view full conversation history

6. **User Management (System Admin only)**
   - Purpose: Manage user accounts and permissions
   - Elements: User list, add user form, role assignment, password reset controls
   - User interactions: Create new users, reset passwords, change user roles, deactivate accounts

7. **System Parameters (System Admin only)**
   - Purpose: Save all key-value pairs of system parameters
   - Elements: key, value
   - User interactions: Create new key-value pairs, update new values for any pair, delete any pair, view all key-value pairs


### Navigation
<!-- How will users move through your application? -->

- Navigation structure:
  - **Header Navigation**: Always visible top navigation bar with user info (name, designation) and logout button
  - **Sidebar Navigation**: Role-based menu items on the left side
  - **Contextual Navigation**: Within chat interface for switching between conversations

- Menu items:
  - **Basic User (Salesperson) Menu**:
    - Dashboard (assigned customers overview)
    - My Conversations (list of active chats)
    - Profile Settings
    - Logout
  
  - **Manager Menu**:
    - Dashboard (unassigned customers + assigned customers + overview)
    - All Conversations (view all customer chats)
    - Customer Management (assign/reassign customers)
    - Team Overview (salesperson performance, respond time of each reply to the customer)
    - Profile Settings
    - Logout
  
  - **System Admin Menu**:
    - Dashboard (system overview)
    - All Conversations (view all customer chats)
    - Customer Management (assign/reassign customers)
    - User Management (create/edit/delete users)
    - System Settings
    - Reports & Analytics
    - Profile Settings
    - Logout

- Breadcrumbs/back navigation:
  - **Chat Interface**: "Dashboard > Customer Name > Chat" with back arrow to return to customer list
  - **Customer Management**: "Dashboard > Customer Management > Customer Details" with breadcrumb navigation
  - **User Management**: "Dashboard > User Management > Edit User" with step-by-step navigation
  - **Mobile Navigation**: Hamburger menu with slide-out navigation, back buttons for drill-down views
  - **Quick Navigation**: "Recently viewed conversations" dropdown in header for quick access to recent chats

### Design Requirements
<!-- Visual and UX requirements -->

- Color scheme:
  - **Primary Colors**: Professional blue (#2563eb) for headers and primary actions, white (#ffffff) for backgrounds
  - **Secondary Colors**: Light gray (#f8fafc) for sidebar, dark gray (#374151) for text
  - **Status Colors**: Green (#10b981) for online/active, yellow (#f59e0b) for pending assignments, red (#ef4444) for urgent/overdue
  - **Chat Colors**: Light blue (#dbeafe) for outgoing messages, light gray (#f3f4f6) for incoming messages
  - **Comment Colors**: Light purple (#f3e8ff) background for internal comments to distinguish from customer messages

- Typography:
  - **Primary Font**: Inter or system font stack for clean readability
  - **Header Text**: 18-24px bold for page titles, 16px medium for section headers
  - **Body Text**: 14px regular for general content, 16px for chat messages
  - **Small Text**: 12px for timestamps, status indicators, and metadata
  - **Monospace**: For user IDs, phone numbers, and system codes

- Layout style (grid, flexbox, etc.):
  - **CSS Grid**: Main layout with header, sidebar, and content areas
  - **Flexbox**: For chat interface, message bubbles, and navigation items
  - **Three-column Layout**: Sidebar (customer list) | Main chat area | Customer info panel
  - **Responsive Breakpoints**: Mobile (<768px), Tablet (768px-1024px), Desktop (>1024px)

- Responsive design requirements:
  - **Mobile**: Single column layout with collapsible sidebar, full-screen chat view
  - **Tablet**: Two-column layout with sidebar toggle, condensed customer info
  - **Desktop**: Full three-column layout with all panels visible
  - **Chat Interface**: Messages stack vertically on all screen sizes with appropriate padding
  - **Touch Targets**: Minimum 44px for mobile buttons and interactive elements

- Accessibility requirements:
  - **WCAG 2.1 AA Compliance**: Color contrast ratios of at least 4.5:1
  - **Keyboard Navigation**: Full application navigable via keyboard shortcuts
  - **Screen Reader Support**: Proper ARIA labels for all interactive elements
  - **Focus Indicators**: Clear visual focus states for all clickable elements
  - **High Contrast Mode**: Alternative color scheme for users with visual impairments
  - **Text Scaling**: Support for 200% zoom without horizontal scrolling
  - **Alternative Text**: All images and icons have descriptive alt text
  - **Live Regions**: Screen reader announcements for new messages and notifications


## Technical Requirements

### Technology Stack
<!-- What technologies should be used? -->

- Frontend: Next.JS with Tailwind CSS, Zustand
- Backend: Python (Django Rest Framework)
- Database: Postgresql, Reddis
- Authentication: Keycloak
- Hosting/Deployment: Caddy with Docker container

### Performance Requirements
<!-- How fast should the application be? -->

- Page load times:
  - **Initial Login Page**: < 2 seconds on standard broadband connection
  - **Dashboard Load**: < 3 seconds after authentication
  - **Chat Interface**: < 1.5 seconds to display conversation history
  - **Customer List Refresh**: < 2 seconds to load/update customer assignments
  - **Message History Load**: < 1 second for last 50 messages, < 3 seconds for full conversation history

- Response times:
  - **Message Send/Receive**: < 500ms for real-time message delivery
  - **Customer Assignment**: < 1 second for manager to assign customer to salesperson
  - **Internal Comment Posting**: < 300ms for comment to appear
  - **User Tag Notifications**: < 2 seconds for tagged user to receive notification
  - **API Calls to Respond.IO**: < 3 seconds timeout, with retry mechanism
  - **Search Functionality**: < 1 second for customer/conversation search results
  - **Authentication**: < 2 seconds for login/logout operations

- Concurrent users:
  - **Target Capacity**: Support 500 concurrent active users
  - **Peak Load**: Handle up to 650 concurrent users during business hours
  - **Message Throughput**: Process 1000+ messages per minute across all conversations
  - **Database Connections**: Maintain stable performance with 200+ simultaneous database connections
  - **Real-time Connections**: Support 500+ WebSocket connections for live messaging
  - **Degradation Threshold**: Performance should not degrade significantly until 80% of maximum capacity

- Additional Performance Metrics:
  - **Message Delivery Rate**: 99.9% successful message delivery to Respond.IO
  - **Uptime Requirement**: 99.5% availability during business hours (8 AM - 8 PM)
  - **Memory Usage**: < 512MB RAM per user session
  - **Bandwidth**: Optimize for users on 10 Mbps connections
  - **Mobile Performance**: All response times should be within 1.5x of desktop performance

### Browser/Platform Support
<!-- What browsers or platforms should be supported? -->

- Supported browsers: Chrome, Firefox, Safari, Edge
- Mobile responsiveness:
  - **Supported Devices**: iOS 12+ (iPhone 8 and newer), Android 8.0+ (devices with 3GB+ RAM)
  - **Screen Sizes**: Phones (320px-768px), Tablets (768px-1024px), optimized for common resolutions
  - **Touch Interface**: All buttons minimum 44px touch targets, swipe gestures for navigation
  - **Mobile Layout Adaptations**:
    - Single-column stack layout on phones
    - Collapsible sidebar navigation with hamburger menu
    - Full-screen chat interface when viewing conversations
    - Bottom navigation bar for primary actions
    - Modal overlays for customer assignment and user management
  - **Mobile-Specific Features**:
    - Push notifications for new messages and assignments
    - Offline message queuing (send when connection restored)
    - Quick reply templates for faster mobile typing
    - Voice message support if supported by Respond.IO
    - Pull-to-refresh for conversation updates
  - **Performance on Mobile**:
    - App-like experience with smooth scrolling and transitions
    - Optimized image loading and caching
    - Minimal data usage for users on limited mobile plans
    - Progressive Web App (PWA) capabilities for home screen installation
  - **Mobile Limitations**:
    - User management features limited to essential functions only
    - Advanced reporting may redirect to desktop version
    - File uploads limited to photos and documents < 10MB
    - Internal comments limited to text (no rich formatting on mobile)

## API Requirements
<!-- If your app needs to integrate with external services -->
- None at the moment. To be expand in the future.

### External APIs
1. Assign / unassign conversation
  - **Reference**: https://developers.respond.io/docs/api/c923c5127e8b2-assign-unassign-conversation
  - **Endpoint**: https://api.respond.io/v2/contact/{identifier}/conversation/assignee
  - curl command: 
    ```
    curl --request POST \
    --url https://api.respond.io/v2/contact/phone:customer_phone_number/conversation/assignee \
    --header 'Accept: application/json' \
    --header 'Authorization: Bearer respond_io_token' \
    --header 'Content-Type: application/json' \
    --data '{
    "assignee": null,
    "assignee": email or userID
    }'
    ```
  - Note: null for unassign customer, or email / userID to assign.

2. Send a message
  - **Reference**: https://developers.respond.io/docs/api/a748f5bfb1bb5-send-a-message
  - **Endpoint**: https://api.respond.io/v2/contact/{identifier}/message
  - curl command: 
    ```
    # Text Message
    curl --request POST \
    --url https://api.respond.io/v2/contact/phone:customer_phone_number/message \
    --header 'Accept: application/json' \
    --header 'Authorization: Bearer respond_io_token' \
    --header 'Content-Type: application/json' \
    --data '{
    "channelId": 0,
    "message": {
        "type": "text",
        "text": "There has been an update in your account..."
        }
    }'

    # File Message
    curl --request POST \
    --url https://api.respond.io/v2/contact/phone:customer_phone_number/message \
    --header 'Accept: application/json' \
    --header 'Authorization: Bearer respond_io_token' \
    --header 'Content-Type: application/json' \
    --data '{
    "channelId": 0,
    "message": {
        "type": "attachment",
        "attachment": {
            "type": "image",
            "url": "https://example-bucket.s3.amazonaws.com/sample-image.jpg"
        }
      }
    }'
    

    ```

3. Create a comment
  - **Reference**: https://developers.respond.io/docs/api/0a102dc5152a0-create-a-comment
  - **Endpoint**: https://api.respond.io/v2/contact/{identifier}/comment
  - curl command: 
    ```
    curl --request POST \
    --url https://api.respond.io/v2/contact/phone:customer_phone_number/comment \
    --header 'Accept: application/json' \
    --header 'Authorization: Bearer respond_io_token' \
    --header 'Content-Type: application/json' \
    --data '{
    "text": "{{@user.ID}} This is a comment"
    }'
    ```
  - Note: ID in user.ID refers to the userID in respond.io

4. Upload file for message
  - **Purpose**: Upload file from salesperson to send to customer
  - **Endpoint**: `POST https://{{ your_api_url }}/api/files/upload`
  - **Headers**: Authorization: Bearer token, Content-Type: multipart/form-data
  - **Parameters**: 
    - file: File to upload (max 10MB)
    - conversation_id: ID of the conversation
    - message_text: Optional text to accompany the file
  - **Response**: File URL and metadata for sending via Respond.IO
  - **Security**: Validate file type, scan for malware, encrypt storage

5. Download customer file
  - **Purpose**: Download file received from customer
  - **Endpoint**: `GET https://{{ your_api_url }}/api/files/{file_id}/download`
  - **Headers**: Authorization: Bearer token
  - **Parameters**: 
    - file_id: ID of the file to download
  - **Response**: File stream with appropriate headers
  - **Security**: Verify user has access to the conversation, log download activity

6. Get file metadata
  - **Purpose**: Get file information without downloading
  - **Endpoint**: `GET https://{{ your_api_url }}/api/files/{file_id}/info`
  - **Headers**: Authorization: Bearer token
  - **Response**: 
    ```json
    {
      "id": 123,
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      "uploaded_by": "customer",
      "created_at": "2024-01-15T10:30:00Z",
      "conversation_id": 456
    }
    ```


### Webhook Endpoints
**Purpose**: Receive real-time events and messages from Respond.IO

1. **Message Webhook**
   - **Endpoint**: `https://{{ hosting_url }}/webhook/message`
   - **Method**: POST
   - **Purpose**: Receive incoming messages from customers via Respond.IO
   - **Expected payload**: 
     ```json
     {
        "contact": {
            "id":1,
            "firstName":"John",
            "lastName":"Doe",
            "phone":"+60123456789",
            "email":"johndoe@sample.com",
            "language":"en",
            "profilePic":"https://cdn.chatapi.net/johndoe.png",
            "countryCode":"MY",
            "status":"open",
            "assignee":{
                "id":2,
                "firstName":"John",
                "lastName":"Doe",
                "email":"johndoe@sample.com"
            },
            "created_at":1663274081
        },
        "message":{
            "messageId":1262965213,
            "channelMessageId":123,
            "contactId":123,
            "channelId":123,
            "traffic":"incoming",
            "message":{
                "type":"text",
                "text":"Message text","messageTag":"ACCOUNT_UPDATE"
                },
            "timestamp":1662965213,
            "status":[
                {
                    "value":"pending",
                    "timestamp":1662965213
                },
                {
                    "value":"failed",
                    "timestamp":1662965213,
                    "message":"Failed reason"
                }
            ]
        },
        "channel":{
            "id":1,
            "name":"string",
            "source":"facebook",
            "meta":"{}",
            "created_at":1663274081
        },
        "event_type":"message.received",
        "event_id":"313ba4a0-7dd6-4818-84f0-43a5e987786e"}
     ```

   - **Response**: 200 OK for successful processing
   - **Security**: Verify webhook signature/token from Respond.IO
   - **Actions triggered**:
     - Create new message record in database
     - Notify assigned salesperson (if conversation assigned)
     - Notify manager (if conversation unassigned)
     - Update conversation status to active

2. **Assignment Webhook** (if supported by Respond.IO)
   - **Endpoint**: `https://{{ hosting_url }}/webhook/assignment`
   - **Method**: POST
   - **Purpose**: Receive notifications when conversations are assigned/unassigned
   - **Expected payload**:
     ```json
      {
          "contact":{
              "id":1,
              "firstName":"John",
              "lastName":"Doe",
              "phone":"+60123456789",
              "email":"johndoe@sample.com",
              "language":"en",
              "profilePic":"https://cdn.chatapi.net/johndoe.png",
              "countryCode":"MY",
              "status":"open",
              "assignee":{
                "id":2,
                "firstName":"John",
                "lastName":"Doe",
                "email":"johndoe@sample.com"
              },
              "created_at":1663274081
            },
          "event_type":"contact.assignee.updated",
          "event_id":"cc5f231a-633c-4ffc-bf61-d970fe5e0085"
      }
     ```
   - **Actions triggered**:
     - Update local assignment records
     - Send notifications to relevant users

### Webhook Security
- **Authentication**: Bearer token or webhook signature verification
- **IP Whitelist**: Restrict to Respond.IO IP ranges
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Retry Handling**: Support for Respond.IO webhook retry mechanism


## Security Requirements

### Authentication Security
- Password encryption:
  - Use bcrypt or Argon2 for password hashing with minimum cost factor of 12
  - Implement password salting to prevent rainbow table attacks
  - Store only hashed passwords, never plain text
  - Force password change on first login for admin-created accounts
  - Implement password history (prevent reusing last 5 passwords)

- Session management:
  - Use secure session tokens with 8-hour expiration for active sessions
  - Implement sliding session renewal (extend on activity)
  - Automatic logout after 120 minutes of inactivity
  - Force logout on password change or role modification
  - Single session per user (invalidate previous sessions on new login)
  - Secure session storage using httpOnly and secure cookies

- Token handling:
  - JWT tokens for API authentication with 1-hour expiration
  - Implement refresh token mechanism with 7-day expiration
  - Store Respond.IO API tokens encrypted at rest using AES-256
  - Rotate API tokens every 90 days or on security incidents
  - Implement token revocation for compromised accounts
  - Use different token scopes for different user roles

### Data Security
- Data validation:
  - Validate all phone numbers using international format (E.164)
  - Sanitize and validate all user inputs before database storage
  - Implement rate limiting: 100 API calls per minute per user
  - Validate file uploads (max 10MB, allowed types: images, documents)
  - Check message content length limits (max 4096 characters)
  - Validate user roles and permissions on every API request

- Input sanitization:
  - Escape HTML in all user-generated content to prevent XSS
  - Use parameterized queries for all database interactions (prevent SQL injection)
  - Sanitize internal comments and customer messages before display
  - Remove dangerous file types and scan uploads for malware
  - Validate and sanitize webhook payloads from Respond.IO
  - Implement Content Security Policy (CSP) headers

- HTTPS requirements:
  - Enforce HTTPS on all connections using TLS 1.3 minimum
  - Implement HTTP Strict Transport Security (HSTS) with 1-year max-age
  - Use certificate pinning for critical API connections
  - Redirect all HTTP traffic to HTTPS automatically
  - Implement proper certificate management and auto-renewal
  - Secure all webhook endpoints with HTTPS and signature verification

### API Security
- Webhook security:
  - Verify Respond.IO webhook signatures using HMAC-SHA256
  - Implement IP whitelist for Respond.IO webhook sources
  - Rate limit webhook endpoints (max 1000 requests per minute)
  - Log all webhook attempts for security monitoring
  - Implement retry mechanism with exponential backoff

- External API calls:
  - Encrypt Respond.IO API credentials in configuration
  - Implement request signing for sensitive API calls
  - Use connection pooling with timeout limits (30 seconds)
  - Log all API failures and implement circuit breaker pattern
  - Validate all responses from Respond.IO API before processing

### Access Control
- Role-based permissions:
  - Basic Users: Can only access assigned customer conversations
  - Managers: Can access all conversations and assign customers
  - System Admins: Full system access including user management
  - Implement principle of least privilege for all user roles
  - Audit trail for all user actions and permission changes

- Data access controls:
  - Encrypt customer phone numbers and personal data at rest
  - Implement database-level row security for customer data
  - Log all data access attempts with user identification
  - Implement data retention policies (1 year for messages)
  - Secure backup encryption and access controls

### Security Monitoring
- Audit logging:
  - Log all login attempts (successful and failed)
  - Track customer assignment changes and user actions
  - Monitor API usage patterns and detect anomalies
  - Log all administrative actions and configuration changes
  - Implement centralized logging with secure log storage

- Intrusion detection:
  - Monitor for brute force login attempts (lock after 5 failures)
  - Detect unusual access patterns or role escalation attempts
  - Alert on multiple concurrent sessions from different IPs
  - Monitor for suspicious API usage or webhook manipulation
  - Implement automated incident response for critical security events

## Business Logic & Rules

### Validation Rules
<!-- What rules should the application enforce? -->

- **User Account Rules:**
  - Usernames must be unique across the system
  - Passwords must meet complexity requirements: minimum 8 characters, alphanumeric combinations, at least one uppercase and one number
  - Each user must have a corresponding Respond.IO account ID
  - Users cannot be deleted if they have active customer assignments
  - Only System Admins can create new user accounts

- **Customer Assignment Rules:**
  - A customer can only be assigned to one salesperson at a time
  - Only Managers and System Admins can assign/reassign customers
  - Basic Users can only view customers assigned to them
  - Unassigned customers are visible to Managers and System Admins only
  - Customer reassignment requires logging the previous assignee and reason

- **Message and Communication Rules:**
  - Messages cannot be deleted once sent to customers
  - Internal comments are never visible to customers
  - Only assigned salesperson can send messages to their customers
  - Managers and System Admins can send messages to any customer
  - Message content cannot be empty or exceed 4096 characters
  - File attachments must be under 10MB and of allowed types

- **Notification Rules:**
  - Assigned salesperson gets notified for new customer messages
  - Managers get notified for unassigned customer messages
  - Tagged users in internal comments get immediate notifications
  - Notification preferences can be configured per user
  - System notifications cannot be disabled for critical events

### Workflow Rules
<!-- How should different processes work? -->

- **Customer Onboarding Workflow:**
  1. New customer sends first message to Respond.IO
  2. System creates customer record with "unassigned" status
  3. Manager receives notification about new unassigned customer
  4. Manager assigns customer to available salesperson
  5. Assigned salesperson receives notification
  6. Customer status changes to "assigned"
  7. Salesperson can begin conversation

- **Message Handling Workflow:**
  1. Customer sends message via WhatsApp to Respond.IO
  2. Webhook delivers message to application
  3. System validates message and sender
  4. If customer is assigned: notify assigned salesperson
  5. If customer is unassigned: notify all managers
  6. Message appears in real-time in relevant chat interfaces
  7. System logs message with timestamp and status

- **Internal Comment Workflow:**
  1. Salesperson creates internal comment in customer chat
  2. System validates comment content and user permissions
  3. If users are tagged: send notifications to tagged users
  4. Comment appears with special styling (not visible to customer)
  5. Tagged users receive real-time notification
  6. Comment is logged with timestamp and author

- **Password Reset Workflow:**
  1. User requests password reset from login page
  2. System sends notification to System Admin (not email)
  3. System Admin manually resets password to temporary password
  4. User is notified of temporary password (email)
  5. User logs in with temporary password
  6. System forces password change on first login
  7. New password must meet complexity requirements

- **Session Management Workflow:**
  1. User authenticates with username and password
  2. System validates credentials against Keycloak
  3. If first login: force password change
  4. Generate secure session token (8-hour expiration)
  5. Track user activity for sliding renewal
  6. Auto-logout after 120 minutes of inactivity
  7. Invalidate session on role change or security events

### Business Constraints
<!-- Any limitations or special business requirements? -->

- **Access Limitations:**
  - No public user registration - all accounts created by System Admin only
  - Basic Users cannot see customers assigned to other users
  - Internal application only - no external customer access
  - All users must have corresponding Respond.IO accounts
  - Maximum 500 concurrent users supported

- **Data Retention Constraints:**
  - Message history retained for minimum 1 year
  - User activity logs retained for audit purposes
  - Customer data cannot be permanently deleted (soft delete only)
  - Internal comments are permanent and cannot be edited/deleted
  - System maintains full audit trail of all actions

- **Integration Constraints:**
  - Completely dependent on Respond.IO API availability
  - Cannot send messages without active Respond.IO connection
  - Webhook failures must be logged and retried
  - API rate limits must be respected (per Respond.IO limits)
  - All customer communication must go through Respond.IO

- **Performance Constraints:**
  - Real-time messaging must maintain <500ms response time
  - System must handle peak loads during business hours (8 AM - 8 PM)
  - Database queries must be optimized for concurrent access
  - File uploads limited to 10MB to maintain performance
  - Search results limited to 100 items per query

- **Security Constraints:**
  - All customer data must be encrypted at rest
  - No customer data can be exported without System Admin approval
  - User sessions limited to single device/browser
  - All API communications must use HTTPS
  - Webhook endpoints must verify Respond.IO signatures

- **Operational Constraints:**
  - System requires 24/7 availability during business hours
  - Automatic failover to backup systems required
  - Regular automated backups with 99.9% recovery guarantee
  - System maintenance windows limited to non-business hours
  - All configuration changes require System Admin approval

## Integration Requirements

### File Handling
<!-- If the app handles file uploads/downloads -->

**File Upload Process (Salesperson to Customer):**
1. Salesperson selects file in chat interface (max 10MB)
2. System validates file type and size
3. File uploaded to secure server with virus scanning
4. System generates secure file URL
5. File sent to customer via Respond.IO API
6. File metadata stored in database with message reference
7. File appears in chat history with download link

**File Download Process (Customer to Salesperson):**
1. Customer sends file via WhatsApp to Respond.IO
2. Webhook delivers file URL and metadata to application
3. System downloads and stores file securely on server
4. File metadata stored in database
5. Assigned salesperson notified of new file
6. File appears in chat interface with download button
7. Salesperson can download file with access logging

**Supported File Types:**
- **Images**: JPG, PNG, GIF, WebP (max 10MB)
- **Documents**: PDF, DOC, DOCX, TXT (max 10MB)
- **Archives**: ZIP (contents scanned for security)
- **Spreadsheets**: XLS, XLSX, CSV (max 10MB)

**File Security Measures:**
- All uploads scanned for malware before storage
- Files stored with encrypted names (not original filenames)
- Access controlled by conversation assignment
- Download activity logged for audit trail
- Files automatically deleted after 1 year (configurable)
- Temporary URLs for file access (expire after 24 hours)

**File Storage Infrastructure:**
- Secure file server with encrypted storage
- Regular automated backups
- CDN integration for faster downloads
- Automatic compression for large images
- Thumbnail generation for image files
- File deduplication to save storage space

**File Management Features:**
- Bulk download multiple files from conversation
- File search within conversation history
- File preview for images and PDFs (in browser)

## Testing Requirements

### Testing Strategy

#### Testing Methodology
- **Test-Driven Development (TDD)**: Write tests before implementing features
- **Behavior-Driven Development (BDD)**: Use Gherkin syntax for user story tests
- **Risk-Based Testing**: Focus on critical business workflows and security
- **Continuous Testing**: Automated tests run on every commit and deployment

#### Test Environments
- **Unit Testing**: Local development with mocked dependencies
- **Integration Testing**: Docker containers with test database and Redis
- **End-to-End Testing**: Staging environment mirroring production
- **Performance Testing**: Load testing environment with monitoring
- **Security Testing**: Dedicated security scanning environment

#### Testing Tools & Frameworks

**Frontend Testing (Next.js)**
- **Unit Tests**: Jest + React Testing Library
- **Component Tests**: Storybook for component isolation
- **E2E Tests**: Playwright for full user workflows
- **Visual Tests**: Percy for UI regression testing
- **Accessibility**: axe-core for WCAG compliance

**Backend Testing (Django)**
- **Unit Tests**: pytest with Django test framework
- **API Tests**: pytest-django + Django REST framework test client
- **Database Tests**: pytest-django with test database
- **Mock External APIs**: responses library for Respond.IO API mocking

**Integration Testing**
- **API Integration**: Postman/Newman for API workflow testing
- **Database Integration**: pytest-postgresql for real database tests
- **Authentication**: Keycloak testcontainer for auth flow testing
- **WebSocket Testing**: pytest-asyncio for real-time messaging

**Performance Testing**
- **Load Testing**: Locust for concurrent user simulation
- **Stress Testing**: Apache JMeter for peak load scenarios
- **Database Performance**: pgbench for PostgreSQL optimization
- **Memory Profiling**: memory_profiler for Python memory usage

**Security Testing**
- **SAST**: Bandit for Python static analysis
- **Dependency Scanning**: Safety for Python vulnerabilities
- **Frontend Security**: ESLint security rules + Snyk
- **Penetration Testing**: OWASP ZAP for automated security scans

#### Test Data Management
- **Test Fixtures**: Predefined user accounts, customers, conversations
- **Factory Pattern**: FactoryBoy for generating test data
- **Database Seeding**: Automated test data setup/teardown
- **Mock Data**: Realistic customer data with privacy protection
- **API Mocking**: Wiremock for Respond.IO API responses

#### Test Coverage Requirements
- **Unit Test Coverage**: Minimum 90% code coverage
- **Integration Coverage**: 100% critical API endpoints
- **E2E Coverage**: 100% user workflows and business rules
- **Security Coverage**: All authentication and authorization paths
- **Performance Coverage**: All high-traffic scenarios tested

#### CI/CD Integration
- **Pre-commit Hooks**: Run unit tests and linting before commits
- **Pull Request Gates**: All tests must pass before merge
- **Staging Deployment**: Automated E2E tests after staging deployment
- **Production Monitoring**: Post-deployment smoke tests
- **Rollback Testing**: Automated rollback verification

### Test Cases

#### 1. Authentication & Authorization Tests

**Unit Tests**
```
✓ Password validation enforces complexity requirements
✓ Password hashing uses bcrypt with proper salt
✓ JWT token generation includes correct user roles
✓ Session timeout handling works correctly
✓ Password change validation prevents reuse of last 5 passwords
```

**Integration Tests**
```
✓ Keycloak authentication flow for all user types
✓ First-time login forces password change
✓ Role-based access control blocks unauthorized actions
✓ Session expiration auto-logs out inactive users
✓ Password reset workflow notifies system admin
✓ Multiple login attempts lock account after 5 failures
```

**Security Tests**
```
✓ SQL injection attempts fail on login forms
✓ XSS attacks blocked in username/password fields
✓ Brute force protection activates correctly
✓ JWT tokens cannot be tampered with
✓ Session tokens are httpOnly and secure
✓ Password reset tokens expire after use
```

#### 2. User Management Tests

**Unit Tests - System Admin Functions**
```
✓ Create user validates all required fields
✓ User role assignment restricts permissions correctly
✓ Password reset generates secure temporary password
✓ User deactivation maintains data integrity
✓ Email validation prevents duplicate accounts
```

**Integration Tests**
```
✓ System admin can create all user types (Basic, Manager, Admin)
✓ New user receives email with temporary password
✓ User profile updates sync with Keycloak
✓ Role changes immediately affect user permissions
✓ User deletion soft-deletes with audit trail
✓ Bulk user operations maintain consistency
```

**End-to-End Tests**
```
Scenario: System Admin Creates New Salesperson
  Given I am logged in as System Admin
  When I navigate to User Management
  And I click "Add New User"
  And I enter valid user details with role "Basic User"
  And I click "Create User"
  Then the user should be created successfully
  And the user should receive login credentials
  And the user should appear in the user list
  And the user should be forced to change password on first login
```

#### 3. Customer Assignment Tests

**Unit Tests**
```
✓ Customer assignment validates user permissions
✓ Assignment history tracks all changes
✓ Unassignment clears customer from user dashboard
✓ Assignment notification generation works correctly
✓ Bulk assignment validates all customers
```

**Integration Tests**
```
✓ Manager assigns unassigned customer to salesperson
✓ Customer status updates from "unassigned" to "assigned"
✓ Assigned salesperson receives real-time notification
✓ Previous assignee loses access to reassigned customer
✓ Assignment audit log captures all details
✓ API call to Respond.IO updates assignment
```

**End-to-End Tests**
```
Scenario: Manager Assigns Customer to Salesperson
  Given I am logged in as Manager
  And there are unassigned customers available
  When I navigate to Customer Management
  And I select an unassigned customer
  And I click "Assign Customer"
  And I select a salesperson from the dropdown
  And I click "Confirm Assignment"
  Then the customer should be assigned to the salesperson
  And the salesperson should receive a notification
  And the customer should appear in salesperson's dashboard
  And the customer should not appear in unassigned list
```

#### 4. Real-Time Messaging Tests

**Unit Tests**
```
✓ Message validation checks content length and type
✓ WebSocket connection handling for multiple users
✓ Message encryption/decryption for storage
✓ Typing indicator triggers correctly
✓ Message delivery status updates properly
```

**Integration Tests**
```
✓ Customer message via webhook creates database entry
✓ Assigned salesperson receives real-time notification
✓ Message appears immediately in chat interface
✓ Unassigned customer messages notify all managers
✓ Message delivery to Respond.IO API succeeds
✓ Failed message delivery triggers retry mechanism
```

**Performance Tests**
```
✓ 500 concurrent users can send/receive messages
✓ Message delivery latency < 500ms under normal load
✓ WebSocket connections maintain stability under load
✓ Database can handle 1000+ messages per minute
✓ Memory usage stays within limits for extended sessions
```

**End-to-End Tests**
```
Scenario: Real-Time Message Exchange
  Given I am a salesperson with an assigned customer
  When the customer sends a WhatsApp message
  Then I should receive a real-time notification
  And the message should appear in my chat interface
  When I type a reply message
  Then the customer should see typing indicators
  When I send the reply
  Then the message should be delivered to customer via Respond.IO
  And the message should appear in chat history
```

#### 5. Internal Comments & Tagging Tests

**Unit Tests**
```
✓ Internal comment validation prevents empty content
✓ User tagging parser extracts usernames correctly
✓ Comment visibility restrictions enforced
✓ Tag notification generation works for mentioned users
✓ Comment threading maintains proper relationships
```

**Integration Tests**
```
✓ Internal comment creation via Respond.IO API
✓ Tagged users receive immediate notifications
✓ Comments appear with special styling in chat
✓ Comments are never sent to customer
✓ Multiple user tags in single comment notify all users
✓ Comment audit trail tracks all interactions
```

**End-to-End Tests**
```
Scenario: Salesperson Tags Colleague in Internal Comment
  Given I am chatting with a customer
  When I click "Add Internal Comment"
  And I type "@john.doe Please follow up on this order"
  And I click "Post Comment"
  Then the comment should appear with special styling
  And john.doe should receive a notification
  And the comment should not be visible to the customer
  And the comment should appear in conversation audit log
```

#### 6. File Upload/Download Tests

**Unit Tests**
```
✓ File type validation rejects unauthorized formats
✓ File size validation enforces 10MB limit
✓ Virus scanning integration works correctly
✓ File metadata extraction and storage
✓ Secure file URL generation includes proper expiration
```

**Integration Tests**
```
✓ Salesperson uploads file and sends to customer
✓ Customer file upload via webhook saves to system
✓ File download requires proper authentication
✓ File access control respects conversation assignment
✓ File cleanup removes expired files automatically
✓ Large file upload progress tracking works
```

**Security Tests**
```
✓ Malicious file uploads are blocked and quarantined
✓ File access URLs cannot be guessed or enumerated
✓ Download permissions validate user assignment
✓ File uploads strip dangerous metadata
✓ Archive files are scanned for nested threats
```

**End-to-End Tests**
```
Scenario: File Upload and Download Workflow
  Given I am chatting with an assigned customer
  When I click "Upload File"
  And I select a valid PDF document
  And I click "Send to Customer"
  Then the file should be uploaded and virus scanned
  And the file should be sent to customer via Respond.IO
  And the file should appear in chat history with download link
  When the customer sends a file back
  Then I should receive notification of new file
  And I should be able to download the customer's file
```

#### 7. API Integration Tests

**Respond.IO API Integration**
```
✓ Message sending API handles all message types (text, files)
✓ Customer assignment API syncs with local database
✓ Comment creation API properly formats user tags
✓ Webhook signature verification blocks unauthorized requests
✓ API rate limiting respects Respond.IO limits
✓ Connection timeout and retry logic handles failures
```

**Webhook Processing Tests**
```
✓ Message webhook creates proper database entries
✓ Assignment webhook updates local customer records
✓ Invalid webhook payloads are rejected safely
✓ Webhook replay attacks are prevented
✓ High-volume webhook processing maintains performance
```

#### 8. Dashboard & UI Tests

**Role-Based Dashboard Tests**
```
✓ Basic User dashboard shows only assigned customers
✓ Manager dashboard shows all customers and assignments
✓ System Admin dashboard includes user management
✓ Customer list filtering and search work correctly
✓ Real-time updates appear without page refresh
```

**Responsive Design Tests**
```
✓ Mobile layout adapts properly for phone screens
✓ Tablet layout shows appropriate column arrangement
✓ Chat interface remains usable on all screen sizes
✓ Touch targets meet 44px minimum requirement
✓ Navigation works correctly on mobile devices
```

**Accessibility Tests**
```
✓ All interactive elements are keyboard navigable
✓ Screen reader announcements work for new messages
✓ Color contrast meets WCAG 2.1 AA standards
✓ Focus indicators are clearly visible
✓ Alternative text provided for all images and icons
```

#### 9. Performance Tests

**Load Testing Scenarios**
```
✓ 500 concurrent users browsing dashboards
✓ 250 concurrent users in active chat sessions
✓ 1000 messages per minute processing capacity
✓ Peak business hours simulation (8 AM - 8 PM)
✓ Database connection pool under maximum load
```

**Response Time Tests**
```
✓ Login page loads in < 2 seconds
✓ Dashboard loads in < 3 seconds after authentication
✓ Chat interface loads in < 1.5 seconds
✓ Message send/receive latency < 500ms
✓ Customer search results in < 1 second
```

**Memory and Resource Tests**
```
✓ Memory usage < 512MB per user session
✓ Database query optimization maintains performance
✓ File upload processing doesn't block other operations
✓ WebSocket connections don't leak memory
✓ Background job processing maintains system responsiveness
```

#### 10. Security Penetration Tests

**Authentication Security**
```
✓ Password brute force protection activates correctly
✓ Session hijacking attempts fail
✓ JWT token manipulation is detected and blocked
✓ Privilege escalation attempts are prevented
✓ Multi-factor authentication bypass attempts fail
```

**Data Access Security**
```
✓ SQL injection attacks on all input fields
✓ Cross-site scripting (XSS) prevention
✓ Cross-site request forgery (CSRF) protection
✓ File upload security bypass attempts
✓ API endpoint unauthorized access attempts
```

**Communication Security**
```
✓ All communications use HTTPS/TLS 1.3
✓ Certificate pinning prevents man-in-the-middle attacks
✓ Webhook signature verification cannot be bypassed
✓ API credentials cannot be extracted from client
✓ Database connections use encrypted channels
```

#### 11. Business Logic Tests

**Customer Assignment Business Rules**
```
✓ Customer can only be assigned to one salesperson
✓ Unassigned customers trigger manager notifications
✓ Assignment changes create proper audit trail
✓ Basic users cannot see other users' customers
✓ Reassignment preserves conversation history
```

**Message Business Rules**
```
✓ Internal comments never appear in customer chat
✓ Message delivery failures trigger appropriate alerts
✓ Message history retention meets 1-year requirement
✓ Deleted users' messages remain in conversation history
✓ Message ordering maintains chronological sequence
```

**Notification Business Rules**
```
✓ Notification preferences are respected per user
✓ Critical notifications cannot be disabled
✓ Duplicate notifications are prevented
✓ Notification delivery confirms user receipt
✓ Failed notifications trigger retry mechanism
```

#### 12. Data Integrity Tests

**Database Consistency**
```
✓ Foreign key constraints prevent orphaned records
✓ Transaction rollback maintains data consistency
✓ Concurrent updates don't create data corruption
✓ Backup and restore processes preserve all data
✓ Data migration scripts maintain referential integrity
```

**Data Validation**
```
✓ Phone number format validation enforces E.164 standard
✓ Email address validation prevents invalid formats
✓ User input sanitization prevents malicious content
✓ File metadata validation ensures accuracy
✓ API payload validation rejects malformed data
```

#### 13. Integration Failure Tests

**Respond.IO API Failure Scenarios**
```
✓ Message sending failure triggers retry mechanism
✓ Assignment API failure maintains local state
✓ Webhook delivery failure is logged and alerted
✓ Authentication failure with Respond.IO handled gracefully
✓ Network connectivity issues don't crash application
```

**Database Failure Scenarios**
```
✓ Database connection loss triggers failover
✓ Transaction timeout handling preserves data
✓ Deadlock detection and resolution works correctly
✓ Database recovery after failure maintains integrity
✓ Backup database synchronization is accurate
```

**Third-Party Service Failures**
```
✓ Keycloak authentication failure allows graceful degradation
✓ File storage service failure doesn't block messaging
✓ Email service failure for notifications is handled
✓ Monitoring service failure doesn't affect core functionality
✓ CDN failure has backup file delivery mechanism
```

#### Test Data Requirements

**User Test Data**
```
- 3 System Admin accounts with different permission levels
- 5 Manager accounts with varying customer assignments
- 20 Basic User accounts representing different salesperson scenarios
- Test accounts with expired passwords and locked status
- Accounts with different Respond.IO integration statuses
```

**Customer Test Data**
```
- 100 customer records with various assignment statuses
- Customers with conversation history of different lengths
- Customers with file attachments and internal comments
- International phone numbers in various formats
- Customers with special characters in names and data
```

**Message Test Data**
```
- Text messages of various lengths (1 char to 4096 chars)
- Messages with special characters and Unicode content
- File attachments of all supported types and sizes
- Internal comments with user tags and mentions
- Message threads with complex conversation flows
```

**Performance Test Data**
```
- 10,000 customer records for load testing
- 100,000 message history records
- 1,000 concurrent user sessions simulation data
- File upload test data of various sizes (1KB to 10MB)
- Webhook payload samples for high-volume testing
```


---

## Notes
<!-- Any additional notes, assumptions, or clarifications -->
  - Whichever values used in the spec here for example: token live time should be configurable within the system parameter page that only system admin can access.
  - The code base should be built to be as modular as possible to handle single codebase multi tenant hosting scenario.
  - It should be allowed that the customer can host their own database and put the database link to our code base.
  - To run development setup, expose the necessary backend URL (e.g.: localhost:8000 for django) to `https://sound-mastiff-entirely.ngrok-free.app` via ngrok. Run the command:
    - `ngrok http --url=sound-mastiff-entirely.ngrok-free.app 8000`
  

## Changelog
<!-- Track changes to this specification -->

- [24 July 2025 18:00 GMT +8:00] - Initial specification created
