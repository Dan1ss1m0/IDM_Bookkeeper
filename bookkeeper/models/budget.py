from dataclasses import dataclass
from datetime import datetime, timedelta
from datetime import date

from ..repository.abstract_repository import AbstractRepository
from ..models.expense import Expense


@dataclass
class Budget:
    """
    ...
    """
    mounthly: int = 60000
    weekly: int = 14000
    daily: int = 2000
    daily_spents: int = 0
    weekly_spents: int = 0
    mounthly_spents: int = 0
    pk: int = 0

    def __init__(self, mounthly: int, weekly: int, daily:int,daily_spents: int = 0, weekly_spents: int = 0, mounthly_spents:int = 0, pk: int = 0):
        self.daily_spents = daily_spents
        self.weekly_spents = weekly_spents
        self.mounthly_spents = mounthly_spents
        self.pk = pk

    def update_spent(self, exp_repo: AbstractRepository[Expense]) -> None:  
        """ Обновляет траты за период бюждетов по заданному репозиторию exp_repo """


        date = datetime.now().isoformat()[:10]  # YYYY-MM-DD format

        daily_exps = exp_repo.get_all_like(like={"expense_date": f"{date}"}, where = None)  

        weekday_now = datetime.now().weekday()
        day_now = datetime.fromisoformat(date)
        first_week_day = day_now - timedelta(days=weekday_now)

        weekly_exps = []
        for i in range(7):
            weekday = first_week_day + timedelta(days=i)
            date_mask = f"{weekday.isoformat()[:10]}"
            weekly_exps += exp_repo.get_all_like(like={"expense_date": date_mask}, where = None)   
        
        mounthly_exps = exp_repo.get_all_like(like={"expense_date": f"{date[:7]}-"}, where = None) 

        self.daily_spents = sum(int(exp.amount) for exp in daily_exps) 
        self.weekly_spents = sum(int(exp.amount) for exp in weekly_exps)
        self.mounthly_spents = sum(int(exp.amount) for exp in mounthly_exps)