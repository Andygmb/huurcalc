class HuurCalc:
    room_studio_sqm: int = 0 # C4
    total_shared_area_sqm: int = 0 # D4
    shared_living_room: bool = False # e4
    shared_kitchen: bool = False # F4
    shared_shower: bool = False # G4
    shared_toilet: bool = False # H4
    total_residents: int = 1 # I4
    user_input_args = [
        room_studio_sqm,
        total_shared_area_sqm,
        shared_living_room,
        shared_kitchen,
        shared_shower,
        shared_toilet,
        total_residents
    ]

    # ask shane where these numbers are from
    MAGIC_NUMBER_DEPENDANT_ROOM_MULTIPLIER = 5
    MAGIC_NUMBER_HEATING_MULTIPLIER = 0.75
    MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_1 = -0.0019
    MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_2 = 2.3917
    MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_3 = 7.5176


    bonus_points_data = {
        'kitchen': {
            "max_residents": 5,
            "shared_points": 4,
            "own_points": 20
        },
        'toilet': {
            "max_residents": 5,
            "shared_points": 4,
            "own_points": 22
        },
        'shower': {
            "max_residents": 8,
            "shared_points": 3,
            "own_points": 15
        }
    }

    def __init__(self, *args, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def calculate_points(self) -> float:
        return sum([self.dependant_room_sqm_points,
                    self.heating_points,
                    self.bonus_points(bonus_type="kitchen"),
                    self.bonus_points(bonus_type="toilet"),
                    self.bonus_points(bonus_type="shower"),
                    self.heating_control,
                    self.balcony,
                    self.bedshed])

    @property
    def estimated_rent_price(self) -> float:
        points = self.calculate_points()
        return round(
            self.MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_1 * points**2 +
            self.MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_2*points
            + self.MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_3,
            2
        )

    @property
    def dependant_room_sqm_points(self) -> float:
        return round(
            (self.room_studio_sqm + self.total_shared_area_sqm / (self.total_residents + 1))
             * self.MAGIC_NUMBER_DEPENDANT_ROOM_MULTIPLIER,
            1)

    @property
    def heating_points(self) -> float:
        return round(self.MAGIC_NUMBER_HEATING_MULTIPLIER * self.room_studio_sqm, 2)

    @property
    def heating_control(self) -> int:
        return 3 # assume present

    @property
    def balcony(self) -> int:
        return 6 # assume present

    @property
    def bedshed(self) -> int:
        return 3 # assume present

    def bonus_points(self, bonus_type=None) -> int:
        bonus_data = self.bonus_points_data.get(bonus_type)
        if not bonus_data or bonus_type is None:
            return 0
        if getattr(self, f"shared_{bonus_type}"):
            if self.total_residents > bonus_data['max_residents']:
                return 0
            else:
                return bonus_data['shared_points']
        else:
            return bonus_data['own_points']


calculator = HuurCalc(
    room_studio_sqm = 59,
    total_shared_area_sqm = 0,
    shared_living_room = False,
    shared_kitchen = False,
    shared_shower = False,
    shared_toilet = False,
    total_residents = 1
)

print(calculator.calculate_points())
print(calculator.estimated_rent_price)