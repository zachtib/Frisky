from learns.queries import add_learn, get_random_learn, get_learn_indexed


def handle_reaction(reaction, reacting_user, commenting_user, original_message, added) -> str:
    if reaction == 'brain' and added:
        if add_learn(commenting_user, original_message):
            return f'Okay, learned {commenting_user}'


def handle_message(*args, **kwargs) -> str:
    if len(args) == 0:
        return
    label = args[0]
    if len(args) == 1:
        # Return a random learn
        # ?learn foobar
        try:
            return get_random_learn(label).content
        except:
            return 'I got nothing, boss'
    elif len(args) == 2:
        # First, see if it's an int index
        # ?learn foobar 2
        try:
            index = int(args[1])
            return get_learn_indexed(label, index).content
        except ValueError:
            if args[1].startswith('?'):
                return "DON'T HURT ME AGAIN"
            if add_learn(label, args[1]):
                return f'Okay, learned {args[0]}'
        except IndexError:
            return 'NO SUCH THING'
    elif len(args) > 2:
        new_learn = ' '.join(args[1:])
        if new_learn.startswith('?'):
            return "DON'T HURT ME AGAIN"
        if add_learn(label, new_learn):
            return f'Okay, learned {args[0]}'
