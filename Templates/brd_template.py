from Examples.Scope_for_BRD import scope_example

brd_template = f"""
BRD (Business requirement document)

Purpose: Captures high-level business needs and goals, written from a business perspective for stakeholders and product teams.

Format:

1)Document Control:
    Document Title
    Version
    Date
    Author
    Stakeholders
    Deliverables (e.g. Mobile app (Android), Web App)
2)Executive Summary:
    Overview of the business problem/opportunity
    Background
3)Business Objectives:
    Primary Goals
    Success Metrics (e.g., 20% increase in conversion rate)
4)Business Requirements:
    [BR-1] User should be able to register with email and phone number
    [BR-2] Admin should see daily sales analytics

5)Scope:
    (Give scope for each individual deliverable separately. It should be very well detailed and in a hierarchical threaded pattern and it should be for each and every single)
    Sample example - {scope_example}
6)Assumptions and Constraints (it should also include all the out of scope items as well.)
7)Dependencies
8)Approval and Sign-off

"""