# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


class Check(object):

    name = u'check'

    def __init__(self, optparser, logger):
        u"""Create new check plugin instance.

        Call the usual optparse methods (like `add_option`) on `optparser` to
        define custom options. `logger` is a logging object.
        """
        pass

    def check_args(self, opts, args):
        """Return error message if `opts` or `args` fail consistency check."""
        pass

    def obtain_data(self, opts, args):
        """Do whatever is necessary to measure data points from the system."""
        pass

    def states(self):
        """Return list of State objects from measured data."""
        return []

    def performances(self):
        """Return list of performance data strings from measured data."""
        return []

    @property
    def shortname(self):
        """Short check name for the headline. Override if necessary."""
        return self.name.split()[0].upper()

    @property
    def default_message(self):
        """Fallback OK message string if nothing special happened."""
        return None
