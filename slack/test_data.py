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
        "item_user": "U5H8EPHFD",
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