from astroquery import alma
q = alma.AlmaClass()
q.cache_location = '/Users/kavelaarsj/Dropbox/PyCharmProjects/alma2cadc/'
alma.Alma.cache_location = '/Users/kavelaarsj/Dropbox/PyCharmProjects/alma2cadc/'
q.retrieve_data_from_uid('uid://A001/X74/X29', cache=False)
