from frisky.test import FriskyTestCase


class MarkovTestCase(FriskyTestCase):

    def test_markov_runs_without_crashing(self):
        self.send_message('?learn lorem Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.send_message('?learn lorem Donec tristique fermentum leo non vulputate')
        self.send_message('?learn lorem Nunc ut tellus vitae lorem molestie convallis')
        self.send_message('?learn lorem Aliquam in scelerisque risus, eu commodo orci')
        self.send_message('?learn lorem Donec venenatis convallis neque sed viverra')
        self.send_message('?learn lorem Vivamus blandit lacus eu nisl mattis, et interdum lacus dapibus')
        self.send_message('?learn lorem Duis aliquam tortor mi, molestie venenatis arcu tempus id')
        self.send_message('?learn lorem Proin sem metus, blandit eu vestibulum non, porttitor porttitor risus')
        self.send_message('?learn lorem Aenean accumsan enim eu lacus eleifend rhoncus')
        self.send_message('?learn lorem Quisque maximus volutpat nibh ultrices tempus')
        self.send_message('?learn lorem Etiam blandit, diam sit amet vestibulum placerat, augue elit feugiat nisl, et tempus est erat ac risus')
        self.send_message('?learn lorem Cras ultrices ante ipsum')
        self.send_message('?learn lorem Nulla ut imperdiet orci, ut semper lorem')
        self.send_message('?learn lorem Proin nulla leo, facilisis et lectus id, mattis sollicitudin dui')
        self.send_message('?learn lorem Nullam id porttitor metus')
        self.send_message('?markov lorem')

    def test_markov_with_no_parameter(self):
        self.send_message('?learn lorem Lorem ipsum dolor sit amet, consectetur adipiscing elit')
        self.send_message('?learn lorem Donec tristique fermentum leo non vulputate')
        self.send_message('?learn lorem Nunc ut tellus vitae lorem molestie convallis')
        self.send_message('?learn lorem Aliquam in scelerisque risus, eu commodo orci')
        self.send_message('?learn lorem Donec venenatis convallis neque sed viverra')
        self.send_message('?learn lorem Vivamus blandit lacus eu nisl mattis, et interdum lacus dapibus')
        self.send_message('?learn lorem Duis aliquam tortor mi, molestie venenatis arcu tempus id')
        self.send_message('?learn lorem Proin sem metus, blandit eu vestibulum non, porttitor porttitor risus')
        self.send_message('?learn lorem Aenean accumsan enim eu lacus eleifend rhoncus')
        self.send_message('?learn lorem Quisque maximus volutpat nibh ultrices tempus')
        self.send_message('?learn lorem Etiam blandit, diam sit amet vestibulum placerat, augue elit feugiat nisl, et tempus est erat ac risus')
        self.send_message('?learn lorem Cras ultrices ante ipsum')
        self.send_message('?learn lorem Nulla ut imperdiet orci, ut semper lorem')
        self.send_message('?learn lorem Proin nulla leo, facilisis et lectus id, mattis sollicitudin dui')
        self.send_message('?learn lorem Nullam id porttitor metus')
        self.send_message('?markov')
