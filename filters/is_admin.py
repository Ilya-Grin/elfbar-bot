from aiogram.dispatcher.filters import BoundFilter
from loader import db


class IsAdmin(BoundFilter):
    async def check(self, message):
        admins_id = db.admins_get()
        admins = 0
        for admin in admins_id:
            if admin == message.from_user.id:
                admins += 1
        return admins != 0
