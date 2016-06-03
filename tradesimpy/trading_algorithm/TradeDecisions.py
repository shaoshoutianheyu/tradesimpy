from TradeDecision import TradeDecision


class TradeDecisions(object):
	def __init__(self):
		self.is_empty = True
		self.open = []
		self.close = []

	def add(self, ticker, open_or_close, long_or_short=None, share_count=None, position_percent=None):
		self.is_empty = False

		open_or_close = open_or_close.lower()
		if(open_or_close == 'open'):
			self.add_open(ticker, long_or_short, share_count, position_percent)
		elif(open_or_close == 'close'):
			self.add_close(ticker, share_count, position_percent)
		else:
			raise AttributeError("The TradeDecision parameter open_or_close must be set to either 'open' or 'close': %s" % open_or_close)

	def add_open(self, ticker, long_or_short=None, share_count=None, position_percent=None):
		self.open.append(TradeDecision(ticker, 'open', long_or_short, share_count, position_percent))

	def add_close(self, ticker, share_count=None, position_percent=None):
		self.close.append(TradeDecision(ticker, 'close', None, share_count, position_percent))
