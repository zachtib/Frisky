import importlib
import pkgutil


def help_text(*args, **kwargs):
    return 'Usage: `?help` or `?help <plugin_name>`'


def handle_message(*args, **kwargs) -> str:
    if len(args) == 1:
        # Display help for named plugin
        plugin_name = args[0]
        try:
            plugin = importlib.import_module(f'plugins.{plugin_name}')
            if hasattr(plugin, 'help_text'):
                help_handler = getattr(plugin, 'help_text')
                if callable(help_handler):
                    result = help_handler()
                    return str(result)
            return f'Error: Plugin `{plugin_name}` does not provide help text'
        except ModuleNotFoundError:
            return f'Error: Plugin `{plugin_name}` does not exist'
    else:
        # Display generic help message
        print('Loading...')
        plugins = []
        for plugin in pkgutil.walk_packages(['plugins']):
            _, name, _ = plugin
            plugins.append(name)
        joined_string = ', '.join(plugins)
        return f'Available plugins: {joined_string}'
