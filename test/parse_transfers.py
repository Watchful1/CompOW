import discord_logging

log = discord_logging.init_logging(debug=True)

import overggparser

fields = overggparser.parse_transfers("https://www.over.gg/transfers")

