from frisky.plugin import FriskyApiPlugin


class BabyTrackerPlugin(FriskyApiPlugin):
    commands = ['baby']
    command_aliases = {
        'hasasiahadthebabyyet': 'baby',
    }
    url = 'https://hasasiahadthebabyyet.herokuapp.com/api/'
    json_property = 'display'
