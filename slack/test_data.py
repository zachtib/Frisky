user_json = '''{
        "id": "W012A3CDE",
        "team_id": "T012AB3C4",
        "name": "spengler",
        "deleted": false,
        "color": "9f69e7",
        "real_name": "Egon Spengler",
        "tz": "America/Los_Angeles",
        "tz_label": "Pacific Daylight Time",
        "tz_offset": -25200,
        "profile": {
            "avatar_hash": "ge3b51ca72de",
            "status_text": "Print is dead",
            "status_emoji": ":books:",
            "real_name": "Real Name",
            "display_name": "displayname",
            "real_name_normalized": "Real Name Normalized",
            "display_name_normalized": "displaynamenormalized",
            "email": "spengler@ghostbusters.example.com",
            "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "team": "T012AB3C4"
        },
        "is_admin": true,
        "is_owner": false,
        "is_primary_owner": false,
        "is_restricted": false,
        "is_ultra_restricted": false,
        "is_bot": false,
        "updated": 1502138686,
        "is_app_user": false,
        "has_2fa": false
    }'''

profile_json = '''{
        "avatar_hash": "ge3b51ca72de",
        "status_text": "Print is dead",
        "status_emoji": ":books:",
        "real_name": "Egon Spengler",
        "display_name": "spengler",
        "real_name_normalized": "Egon Spengler",
        "display_name_normalized": "spengler",
        "email": "spengler@ghostbusters.example.com",
        "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
        "team": "T012AB3C4"
    }'''

reg_event_json = '''{
            "token": "z26uFbvR1xHJEdHE1OQiO6t8",
            "team_id": "T061EG9RZ",
            "api_app_id": "A0FFV41KK",
            "event": {
                    "type": "reaction_added",
                    "user": "U061F1EUR",
                    "item": {
                            "type": "message",
                            "channel": "C061EG9SL",
                            "ts": "1464196127.000002"
                    },
                    "reaction": "slightly_smiling_face",
                    "item_user": "U0M4RL1NY",
                    "event_ts": "1465244570.336841"
            },
            "type": "event_callback",
            "authed_users": [
                    "U061F7AUR"
            ],
            "event_id": "Ev9UQ52YNA",
            "event_time": 1234567890
    }'''

item_event_json = '''{
            "token": "z26uFbvR1xHJEdHE1OQiO6t8",
            "team_id": "T061EG9RZ",
            "api_app_id": "A0FFV41KK",
            "event": {
                    "type": "reaction_added",
                    "user": "U061F1EUR",
                    "item": {
                            "type": "message",
                            "channel": "C061EG9SL",
                            "ts": "1464196127.000002"
                    },
                    "reaction": "slightly_smiling_face",
                    "item_user": "U0M4RL1NY",
                    "event_ts": "1465244570.336841"
            },
            "type": "event_callback",
            "authed_users": [
                    "U061F7AUR"
            ],
            "event_id": "Ev9UQ52YNA",
            "event_time": 1234567890
    }'''

bot_event_json = '''{
        "api_app_id": "ARNN86LBU",
        "authed_users": [
            "US3BT1NJK"
        ],
        "event": {
            "attachments": [
                {
                    "color": "6E3E74",
                    "fallback": "I don't know what this field is",
                    "id": 1,
                    "mrkdwn_in": [
                        "text"
                    ],
                    "text": "Expensive Cardboard 3/4",
                    "thumb_height": 204,
                    "thumb_url": "https://imgflip.com/memegenerator/224675250/PHALLIC",
                    "thumb_width": 146,
                    "title": "Kess, Dissident Mage :mana-1::mana-u::mana-b::mana-r:",
                    "title_link": "https://www.youtube.com/watch?v=oHg5SJYRHA0"
                }
            ],
            "bot_id": "B5HF86T18",
            "channel": "C5HBKKEAE",
            "channel_type": "channel",
            "event_ts": "1582222822.004400",
            "subtype": "bot_message",
            "text": "",
            "ts": "1582222822.004400",
            "type": "message",
            "username": "Scryfall"
        },
        "event_id": "EvUBUBKW0N",
        "event_time": 1582222822,
        "team_id": "T5J4V03V4",
        "token": "NONEYAFUCKINGBIZNASS",
        "type": "event_callback"
    }'''

no_user_reaction_json = '''{
    "api_app_id": "ARNN86LBU",
    "authed_users": [
        "US3BT1NJK"
    ],
    "event": {
        "event_ts": "1582233893.005700",
        "item": {
            "channel": "G98JUGVN1",
            "ts": "1582233843.005600",
            "type": "message"
        },
        "reaction": "cry",
        "type": "reaction_added",
        "user": "U5HEAEPGD"
    },
    "event_id": "EvUA38PA77",
    "event_time": 1582233893,
    "team_id": "T5J4V03V4",
    "token": "BITCHGETAOUTAHERE",
    "type": "event_callback"
}'''

message_deleted_event = '''{
    "api_app_id": "ARNN86LBU",
    "authed_users": [
        "US3BT1NJK"
    ],
    "event": {
        "channel": "CSTSDLCDS",
        "channel_type": "channel",
        "deleted_ts": "1582297826.141900",
        "event_ts": "1582297852.016600",
        "hidden": true,
        "subtype": "message_deleted",
        "ts": "",
        "type": "message"
    },
    "event_id": "EvUB8VV90V",
    "event_time": 1582297852,
    "team_id": "T5J4V03V4",
    "token": "SUCKATHISISSECRET",
    "type": "event_callback"
}'''

complete_and_utter_rubbish = '''{"msg": "just some rubbish for test coverage"}'''

dm_json = '''{
        "id": "D00000000",
        "created": 1582815028,
        "is_archived": false,
        "is_im": true,
        "is_org_shared": false,
        "user": "U00000000",
        "last_read": "0000000000.000000",
        "latest": {
            "bot_id": "B00000000",
            "type": "message",
            "text": "pong",
            "user": "U00000000",
            "ts": "1582815032.000300",
            "team": "T00000000",
            "bot_profile": {
                "id": "B00000000",
                "deleted": false,
                "name": "Risky",
                "updated": 1581702916,
                "app_id": "A00000000",
                "icons": {
                    "image_36": "https://avatars.slack-edge.com/2020-02-14/952745718468_58cea6ae8be276fc1f1e_36.png",
                    "image_48": "https://avatars.slack-edge.com/2020-02-14/952745718468_58cea6ae8be276fc1f1e_48.png",
                    "image_72": "https://avatars.slack-edge.com/2020-02-14/952745718468_58cea6ae8be276fc1f1e_72.png"
                },
                "team_id": "T00000000"
            },
            "reactions": [
                {
                    "name": "upvote",
                    "users": [
                        "U00000000"
                    ],
                    "count": 1
                }
            ]
        },
        "unread_count": 2,
        "unread_count_display": 1,
        "is_open": false,
        "priority": 0
    }'''

reaction_added_but_no_item_user_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "reaction_added",
        "user": "U0XXXXXXX",
        "reaction": "thumbsup",
        "item": {
            "type": "message",
            "channel": "C0XXXXXXX",
            "ts": "1360782400.XXXXXX"
        },
        "event_ts": "1360782804.XXXXXX"
    },
    "event_context": "EC12345",
    "event_id": "Ev0XXXXXXX",
    "event_time": 1234567890
}
'''.strip()

message_sent_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "message",
        "channel": "C0XXXXXXX",
        "user": "U0XXXXXXX",
        "text": "Live long and prospect.",
        "ts": "1355517523.XXXXXX",
        "event_ts": "1355517523.XXXXXX",
        "channel_type": "channel"
    },
    "type": "event_callback",
    "authed_users": [
            "UXXXXXXX1"
    ],
    "authed_teams": [
            "TXXXXXXXX"
    ],
    "authorizations": [
        {
            "enterprise_id": "E12345",
            "team_id": "T12345",
            "user_id": "U12345",
            "is_bot": false
        }
    ],
    "event_context": "EC12345",
    "event_id": "Ev0XXXXXXX",
    "event_time": 1234567890
}'''.strip()

reaction_event_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "reaction_added",
        "user": "U0XXXXXXX",
        "reaction": "thumbsup",
        "item_user": "U0XXXXXXX",
        "item": {
            "type": "message",
            "channel": "C0XXXXXXX",
            "ts": "1360782400.XXXXXX"
        },
        "event_ts": "1360782804.XXXXXX"
    },
    "type": "event_callback",
    "authed_users": [
            "UXXXXXXX1"
    ],
    "authed_teams": [
            "TXXXXXXXX"
    ],
    "authorizations": [
        {
            "enterprise_id": "E12345",
            "team_id": "T12345",
            "user_id": "U12345",
            "is_bot": false
        }
    ],
    "event_context": "EC12345",
    "event_id": "Ev0XXXXXXX",
    "event_time": 1234567890
}'''.strip()

user_joined_payload = '''
{
    "token": "XXYYZZ",
    "team_id": "TXXXXXXXX",
    "api_app_id": "AXXXXXXXXX",
    "event": {
        "type": "message",
        "subtype": "channel_join",
        "text": "<@U0XXXXXXX|bobby> has joined the channel",
        "ts": "1403051575.000407",
        "user": "U0XXXXXXX"
    },
    "type": "event_callback",
    "authed_users": [
            "UXXXXXXX1"
    ],
    "authed_teams": [
            "TXXXXXXXX"
    ],
    "authorizations": [
        {
            "enterprise_id": "E12345",
            "team_id": "T12345",
            "user_id": "U12345",
            "is_bot": false
        }
    ],
    "event_context": "EC12345",
    "event_id": "Ev0XXXXXXX",
    "event_time": 1234567890
}
'''

message_changed_payload = '''
{
  "token": "XXYYZZ",
  "team_id": "TXXXXXXXX",
  "api_app_id": "AXXXXXXXXX",
  "event": {
    "type": "message",
    "subtype": "message_changed",
    "hidden": true,
    "message": {
      "client_msg_id": "6dc63734-a2bc-0000-0000-000000000000",
      "type": "message",
      "text": "nice",
      "user": "U0XXXXXXX",
      "team": "TXXXXXXXX",
      "edited": {
        "user": "U214XXXXXXX",
        "ts": "1622000000.000000"
      },
      "blocks": [
        {
          "type": "rich_text",
          "block_id": "mAsp",
          "elements": [
            {
              "type": "rich_text_section",
              "elements": [
                {
                  "type": "text",
                  "text": "nice"
                }
              ]
            }
          ]
        }
      ],
      "ts": "1622000000.002500",
      "source_team": "TXXXXXXXX",
      "user_team": "TXXXXXXXX"
    },
    "channel": "C0XXXXXXX",
    "previous_message": {
      "client_msg_id": "6dc63734-a2bc-4c3c-0000-000000000000",
      "type": "message",
      "text": "?ping ping",
      "user": "U214XXXXXXX",
      "ts": "1622000000.002500",
      "team": "TXXXXXXXX",
      "edited": {
        "user": "U214XXXXXXX",
        "ts": "1622000000.000000"
      },
      "blocks": [
        {
          "type": "rich_text",
          "block_id": "xoWk",
          "elements": [
            {
              "type": "rich_text_section",
              "elements": [
                {
                  "type": "text",
                  "text": "?ping ping"
                }
              ]
            }
          ]
        }
      ]
    },
    "event_ts": "1622600000.003200",
    "ts": "1622600000.003200",
    "channel_type": "channel"
  },
  "type": "event_callback",
  "event_id": "Ev0XXXXXXX",
  "event_time": 1622600000,
  "authed_users": [
    "U214XXXXXXX"
  ],
  "authorizations": [
    {
      "enterprise_id": null,
      "team_id": "TXXXXXXXX",
      "user_id": "U214XXXXXXX",
      "is_bot": true,
      "is_enterprise_install": false
    }
  ],
  "is_ext_shared_channel": false,
  "event_context": "2-message-T5J4V03V4-000000000-000000000"
}
'''.strip()

message_deleted_payload = '''
{
  "token": "XXYYZZ",
  "team_id": "TXXXXXXXX",
  "api_app_id": "AXXXXXXXXX",
  "event": {
    "type": "message",
    "subtype": "message_deleted",
    "hidden": true,
    "deleted_ts": "1622000000.002500",
    "channel": "C0XXXXXXX",
    "previous_message": {
      "client_msg_id": "6dc63734-a2bc-4c3c-0000-000000000000",
      "type": "message",
      "text": "nice",
      "user": "U0XXXXXXX",
      "ts": "1622000000.002500",
      "team": "TXXXXXXXX",
      "edited": {
        "user": "U214XXXXXXX",
        "ts": "1622600000.000000"
      },
      "blocks": [
        {
          "type": "rich_text",
          "block_id": "mAsp",
          "elements": [
            {
              "type": "rich_text_section",
              "elements": [
                {
                  "type": "text",
                  "text": "nice"
                }
              ]
            }
          ]
        }
      ]
    },
    "event_ts": "1622600000.003300",
    "ts": "1622600000.003300",
    "channel_type": "channel"
  },
  "type": "event_callback",
  "event_id": "Ev0XXXXXXX",
  "event_time": 1622657607,
  "authed_users": [
    "U214XXXXXXX"
  ],
  "authorizations": [
    {
      "enterprise_id": null,
      "team_id": "TXXXXXXXX",
      "user_id": "U214XXXXXXX",
      "is_bot": true,
      "is_enterprise_install": false
    }
  ],
  "is_ext_shared_channel": false,
  "event_context": "2-message-TXXXXXXXX-000000000-000000000"
}
'''.strip()

message_replied_payload = '''
{
  "token": "XXYYZZ",
  "team_id": "TXXXXXXXX",
  "api_app_id": "AXXXXXXXXX",
  "event": {
    "type": "message",
    "message": {
      "type": "message",
      "user": "U0XXXXXXX",
      "text": "Was there was there was there what was there was there what was there was there there was there.",
      "thread_ts": "1482960137.000000",
      "reply_count": 1,
      "replies": [
        {
          "user": "U0XXXXXXX",
          "ts": "1483037603.000000"
        }
      ],
      "ts": "1482960137.000000"
    },
    "hidden": true,
    "channel": "C0XXXXXXX",
    "event_ts": "1483037604.000000",
    "ts": "1483037604.000000"
  },
  "type": "event_callback",
  "event_context": "EC12345",
  "event_id": "Ev0XXXXXXX",
  "event_time": 1234567890,
  "authed_users": [
    "U214XXXXXXX"
  ]
}
'''.strip()

unsupported_payload = '''
{
    "event": {
        "type": "unsupported_event_type"
    }
}
'''.strip()
