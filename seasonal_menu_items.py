from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

class Season(Enum):
    SPRING = ("Spring", [3, 4, 5])
    SUMMER = ("Summer", [6, 7, 8])
    FALL = ("Fall", [9, 10, 11])
    WINTER = ("Winter", [12, 1, 2])

    def __init__(self, label: str, months: List[int]):
        self.label = label
        self.months = months

class Holiday(Enum):
    NEW_YEAR = ("New Year's Day", 1, 1)
    VALENTINE = ("Valentine's Day", 2, 14)
    EASTER = ("Easter", None, None)  # Dynamic date
    INDEPENDENCE_DAY = ("Independence Day", 7, 4)
    HALLOWEEN = ("Halloween", 10, 31)
    THANKSGIVING = ("Thanksgiving", None, None)  # 4th Thursday of November
    CHRISTMAS = ("Christmas", 12, 25)

    def __init__(self, label: str, month: Optional[int], day: Optional[int]):
        self.label = label
        self.month = month
        self.day = day

@dataclass
class Ingredient:
    name: str
    peak_seasons: List[Season]
    shelf_life_days: int
    base_cost: float
    local_sourcing: bool = False

class PricingStrategy:
    @staticmethod
    def calculate_seasonal_price(base_price: float, popularity: float, 
                               ingredient_availability: float) -> float:
        seasonal_factor = 1 + (0.3 * (1 - ingredient_availability))
        popularity_factor = 1 + (0.2 * popularity)
        return base_price * seasonal_factor * popularity_factor

class MenuItem:
    def __init__(self, name: str, description: str, base_price: float,
                 ingredients: List[Ingredient], seasons: List[Season] = None,
                 holidays: List[Holiday] = None):
        self.name = name
        self.description = description
        self.base_price = base_price
        self.ingredients = ingredients
        self.seasons = seasons or []
        self.holidays = holidays or []
        self.sales_history: Dict[str, int] = defaultdict(int)
        self.popularity_score = 0.5  # Initial neutral popularity

    def update_popularity(self, sales_count: int, max_sales: int):
        self.popularity_score = min(1.0, sales_count / max_sales)

class SeasonalMenu:
    def __init__(self):
        self.menu_items: List[MenuItem] = []
        self.sales_history: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def add_item(self, item: MenuItem):
        self.menu_items.append(item)

    def calculate_ingredient_availability(self, ingredient: Ingredient) -> float:
        current_season = self.get_current_season()
        if current_season in ingredient.peak_seasons:
            return 1.0
        
        current_month = datetime.now().month
        min_distance = float('inf')
        
        for season in ingredient.peak_seasons:
            for peak_month in season.months:
                distance = min((current_month - peak_month) % 12,
                             (peak_month - current_month) % 12)
                min_distance = min(min_distance, distance)
        
        return max(0.2, 1 - (min_distance / 6))

    def get_current_season(self) -> Season:
        current_month = datetime.now().month
        for season in Season:
            if current_month in season.months:
                return season
        return Season.WINTER

    def get_current_holiday(self) -> Optional[Holiday]:
        today = datetime.now()
        
        for holiday in Holiday:
            if holiday == Holiday.EASTER:
                easter_date = self._calculate_easter_date(today.year)
                if today.date() == easter_date:
                    return holiday
            elif holiday == Holiday.THANKSGIVING:
                thanksgiving = self._calculate_thanksgiving_date(today.year)
                if today.date() == thanksgiving:
                    return holiday
            elif holiday.month == today.month and holiday.day == today.day:
                return holiday
        return None

    def _calculate_easter_date(self, year: int) -> datetime.date:
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return datetime(year, month, day).date()

    def _calculate_thanksgiving_date(self, year: int) -> datetime.date:
        first = datetime(year, 11, 1)
        while first.weekday() != 4:  # 4 is Thursday
            first += timedelta(days=1)
        return (first + timedelta(weeks=3)).date()

    def get_seasonal_items(self) -> List[Dict]:
        current_season = self.get_current_season()
        current_holiday = self.get_current_holiday()
        
        max_sales = max((sum(item.sales_history.values()) 
                        for item in self.menu_items), default=1)

        seasonal_items = []
        for item in self.menu_items:
            if current_season in item.seasons or current_holiday in item.holidays:
                availability_score = sum(self.calculate_ingredient_availability(ing) 
                                      for ing in item.ingredients) / len(item.ingredients)
                
                item.update_popularity(sum(item.sales_history.values()), max_sales)
                
                current_price = PricingStrategy.calculate_seasonal_price(
                    item.base_price, 
                    item.popularity_score,
                    availability_score
                )
                
                seasonal_items.append({
                    "name": item.name,
                    "description": item.description,
                    "price": round(current_price, 2),
                    "availability": availability_score,
                    "popularity": item.popularity_score
                })
        
        return sorted(seasonal_items, 
                     key=lambda x: (x["availability"], x["popularity"]), 
                     reverse=True)

    def record_sale(self, item_name: str, quantity: int = 1):
        date_key = datetime.now().strftime("%Y-%m")
        for item in self.menu_items:
            if item.name == item_name:
                item.sales_history[date_key] += quantity
                break
