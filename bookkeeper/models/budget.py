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
    monthly: float = 56000
    weekly: float =14000
    daily: float = 2000
    dayly_spents: float = 0
    weekly_spents: float = 0
    mounyhly_spents: float = 0
    pk: int = 0

    def __init__(self, mounthly: float, weekly: float, daily:float,dayly_spents: float = 0, weekly_spents: float = 0, mounyhly_spents:float = 0, pk: int = 0):
        self.dayly_spents = dayly_spents
        self.weekly_spents = weekly_spents
        self.mounyhly_spents = mounyhly_spents
        self.pk = pk

    def update_spent(self, exp_repo: AbstractRepository[Expense]) -> None:  
        """ Обновляет траты за период бюждетов по заданному репозиторию exp_repo """


        date = datetime.now().isoformat()[:10]  # YYYY-MM-DD format

        daily_exps = exp_repo.get_all_like(like={"expense_date": f"{date}"})  

        weekday_now = datetime.now().weekday()
        day_now = datetime.fromisoformat(date)
        first_week_day = day_now - timedelta(days=weekday_now)

        weekly_exps = []
        for i in range(7):
            weekday = first_week_day + timedelta(days=i)
            date_mask = f"{weekday.isoformat()[:10]}"
            weekly_exps += exp_repo.get_all_like(like={"expense_date": date_mask})   
        
        mounthly_exps = exp_repo.get_all_like(like={"expense_date": f"{date[:7]}-"}) 

        self.dayly_spents = sum(int(exp.amount) for exp in daily_exps) 
        self.weekly_spents = sum(int(exp.amount) for exp in weekly_exps)
        self.mounthly_spents = sum(int(exp.amount) for exp in mounthly_exps)