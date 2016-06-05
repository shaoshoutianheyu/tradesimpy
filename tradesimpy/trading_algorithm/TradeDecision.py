
class TradeDecision(object):
	def __init__(self, ticker, open_or_close, long_or_short=None, share_count=None, position_percent=None):
		self.ticker = ticker
		self.share_count = None
		self.position_percent = None

		# Give priority to share count then position percent
		if(share_count):
			self.share_count = share_count
		elif(position_percent != None):
			self.position_percent = position_percent
		else:
			raise ValueError("You must provide either a share count or position percent in TradeDecision")

		# Make trade decision has proper open/close positions
		self.long_or_short = None
		self.open_or_close = open_or_close.lower()
		if(self.open_or_close == 'open'):
			if(long_or_short != 'long' and long_or_short != 'short'):
				raise ValueError("The TradeDecision parameter long_or_short must be set to either 'long' or 'short': %s" \
					% long_or_short)
			else:
				self.long_or_short = long_or_short.lower()
		elif(self.open_or_close == 'close'):
			pass
		else:
			raise ValueError("The TradeDecision parameter open_or_close must be set to either 'open' or 'close': %s" \
				% open_or_close)
