import logging
import httpx
from config import Settings
from models import Signal
log=logging.getLogger(__name__)
def format_signal(s:Signal, live_price:float|None=None)->str:
    action = "Buy" if s.direction.value == "bullish" else "Sell"
    live_line = f'\n<b>Live price now:</b> {live_price:.8g}' if live_price else ''
    return (f'<b>{s.symbol} — {s.direction.value.title()}</b> vs {s.comparison_symbol}\n'
    f'{s.timeframe} entry · {s.htf_timeframe} trend\n\n'
    f'<b>Order:</b> Limit {action} @ {s.entry_low:.8g} – {s.entry_high:.8g}{live_line}\n'
    f'<b>Stop:</b> {s.invalidation:.8g}\n'
    f'<b>Targets:</b> {s.target_one:.8g} / {s.target_two:.8g}\n'
    f'<b>R:R:</b> {s.rr:.2f}\n\n'
    f'Confirmed: {", ".join(s.rationale)}')
class Notifier:
    def __init__(self,c:Settings):self.c=c
    async def send(self,s:Signal,live_price:float|None=None):
        msg=format_signal(s,live_price)
        if self.c.dry_run:log.info('DRY RUN\n%s',msg);return
        async with httpx.AsyncClient(timeout=15) as client:
            if self.c.telegram_bot_token and self.c.telegram_chat_id:
                r=await client.post('https://api.telegram.org/bot'+self.c.telegram_bot_token.get_secret_value()+'/sendMessage',json={'chat_id':self.c.telegram_chat_id,'text':msg,'parse_mode':'HTML'})
            elif self.c.discord_webhook_url:r=await client.post(self.c.discord_webhook_url.get_secret_value(),json={'content':msg})
            else:raise RuntimeError('No private channel destination')
            r.raise_for_status()