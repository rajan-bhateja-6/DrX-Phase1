scope_example = '''
PARENT INTERFACE - FLOW 

LOGIN / SIGNUP (Parent)
Parent clicks “Login / Sign Up”
Chooses login via:
Email → enters email → OTP or password
Mobile number → enters number → OTP or password
If account exists → redirect to parent dashboard
If new → redirected to parent onboarding


ONBOARDING FLOW (Parent)
Selects role as Parent
Enters name, phone number or email
Enters child’s invite code or phone/email to link (optional)
If no invite code, system waits for child to add parent later
Accepts T&Cs, privacy policy, and notification consent
Chooses notification preference: SMS, email, in-app
Redirected to Parent Dashboard


PARENT DASHBOARD OVERVIEW
Greeting banner: “Welcome, [Name]”
View linked child/children (if connected)
Notifications center
Access to major modules:
SilentShield Alerts
Wellness Summary
My Child’s Submissions
Reports Dashboard
Wall of Fame
Settings


SILENTSHIELD ALERTS (Emergency Monitoring)
If child uses SilentShield:
Parent receives alert with a secure link (SMS, email, or in-app)
Alert includes: Timestamp, child’s name, location, and audio snippet
Parent can acknowledge alert → seen status sent back to child
Link expires after a defined time window (e.g., 15 mins for non-app users)


WELLNESS SUMMARY (Emotional Trends)
Weekly summary of child’s emotional check-ins from CareMate
Includes mood graphs, general trends (anonymized if multiple kids)
Shows suggestions CareMate provided (if permitted by child)
Parent gets notified if child trends negative for multiple days
Encouraged to initiate conversation (offline or through app counselor)


MY CHILD’S CONTENT (Creative & Story Submissions)
View uploaded stories or talents by the child (if privacy set to “Parent View”)
Stories show approval status and can be liked or commented on (if enabled)
Parent can encourage with badges or positive emoji reactions
Child receives non-intrusive notifications of feedback


REPORTS DASHBOARD (Child's Reports)
View all safety reports submitted by the child (bullying, suggestions)
Track status: Open / In Review / Resolved
If necessary, escalate the is sue to school or platform support
Add parent remarks (if allowed by student)


SETTINGS (Parent)
Edit profile (name, contact)
Manage notification types and frequency
Link/unlink children manually
View app permissions and privacy settings
Contact support or raise a technical issue


NOTIFICATIONS (Parent)
“Your child triggered SilentShield at [Time]”
“Your child uploaded a new story”
“Your child earned a badge: Brave Voice”
“Counselor connected with your child this week”
“You’ve successfully nominated someone to the Wall of Fame”


Edge Cases Handled (Parent)
If not linked to a student, dashboard offers retry or waiting state
If a student removes a parent from trusted contacts → parent is notified
If permissions (location/audio) not granted by child → some alerts are limited

'''