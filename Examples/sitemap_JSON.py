sitemap_JSON_example = """{
  "app": "GoldenHearts",
  "version": "1.0",
  "sitemap": {
    "Home": {
      "path": "/",
      "children": {
        "Login": "/login",
        "SignUp": "/signup",
        "About": "/about",
        "FAQ": "/faq",
        "ContactSupport": "/support"
      }
    },
    "Auth": {
      "SignUp": {
        "path": "/signup",
        "steps": [
          "PersonalDetails",
          "Interests",
          "ProfilePhoto",
          "Verification"
        ]
      },
      "Login": {
        "path": "/login",
        "methods": ["Email", "PhoneNumber", "SocialLogin"]
      },
      "PasswordReset": "/reset-password"
    },
    "Profile": {
      "path": "/profile",
      "children": {
        "ViewProfile": "/profile/view",
        "EditProfile": "/profile/edit",
        "Preferences": "/profile/preferences",
        "PhotoGallery": "/profile/photos",
        "AccountSettings": "/profile/settings"
      }
    },
    "Discover": {
      "path": "/discover",
      "children": {
        "Matches": "/discover/matches",
        "Nearby": "/discover/nearby",
        "Search": "/discover/search",
        "Filters": [
          "AgeRange",
          "Location",
          "Interests",
          "Lifestyle",
          "RelationshipType"
        ]
      }
    },
    "Connections": {
      "path": "/connections",
      "children": {
        "Likes": "/connections/likes",
        "Favorites": "/connections/favorites",
        "Visitors": "/connections/visitors",
        "BlockedUsers": "/connections/blocked"
      }
    },
    "Chat": {
      "path": "/chat",
      "children": {
        "Inbox": "/chat/inbox",
        "ChatRoom": "/chat/:userId",
        "VoiceCall": "/chat/voice/:userId",
        "VideoCall": "/chat/video/:userId"
      }
    },
    "Events": {
      "path": "/events",
      "children": {
        "LocalEvents": "/events/local",
        "VirtualEvents": "/events/virtual",
        "CreateEvent": "/events/create",
        "RSVP": "/events/:eventId/rsvp"
      }
    },
    "Safety": {
      "path": "/safety",
      "children": {
        "Guidelines": "/safety/guidelines",
        "ReportUser": "/safety/report",
        "HelpResources": "/safety/resources"
      }
    },
    "Accessibility": {
      "path": "/accessibility",
      "features": [
        "LargeText",
        "VoiceAssistance",
        "ColorContrastModes",
        "SimpleNavigation"
      ]
    },
    "Premium": {
      "path": "/premium",
      "children": {
        "Plans": "/premium/plans",
        "Upgrade": "/premium/upgrade",
        "Benefits": "/premium/benefits"
      }
    },
    "Notifications": "/notifications",
    "Legal": {
      "TermsOfService": "/terms",
      "PrivacyPolicy": "/privacy"
    }
  }
}
"""