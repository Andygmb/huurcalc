from enum import Enum



class HuurCalc:

    room_studio_sqm: int = 0 # C4
    total_shared_area_sqm: int = 0 # D4
    shared_living_room: bool = False # e4
    shared_kitchen: bool = False # F4
    shared_shower: bool = False # G4
    shared_toilet: bool = False # H4
    total_residents: int = 1 #

    # advanced calc
    move_in_year: int = 2023 # K%
    number_of_main_rooms: int = 1 # K8
    total_living_space_sqm: int = 74 # K10
    has_outdoor_space: bool = True # K12
    outdoor_space_sqm: int = 0 # L12
    outdoor_space_shared: bool = True # ?
    outdoor_space_residents: int = 2 # Q12

    class KitchenChoices(Enum):
        BARE_SMALL = 'Bare/small'
        BASIC_ESSENTIAL = 'Basic Essential'
        MODERN = 'Modern'
        LARGE = 'Large'
        JAMIES_KITCHEN = 'Jamie Oliver\'s Kitchen'

    class BathroomChoices(Enum):
        BASIC = 'Basic'
        MODERN = 'Modern'
        MODERN_WITH_BATH = 'Modern with bath'

    kitchen_description: str = KitchenChoices.BARE_SMALL # K14
    bathroom_description: str = BathroomChoices.BASIC # K18
    woz_value: int = 0 # K21
    build_year: int = 1995 # K23
    amsterdam_or_ultrecht: bool = False # K25

    energy_label: str = "C" # R22
    energy_index: int = 0 # R24
    national_monument: bool = False #AG3


    # Q9 = points
    # Q5 = max rent price
    # R5 = can it be reduced?

    # number of points
    # =ROUND(T3+AK3+AO3+AJ3+AP3,0)

    # max legal rent price
    # =IF(5.44 * Q9 - 10.4 < 208, 208, 5.44 * Q9 - 10.4)

    # can this rent price be reduced?
    # =IF(K5=2023,IF(Q5>808,"No, If it is above 808, it cannot be reduced","Possibly. It is below 808 euro so would qualify for a reduction if this calculation is correct"),IF(Q5>763,"No, If it is above 763, it cannot be reduced","Possibly. It is below 763 euro so would qualify for a reduction if this calculation is correct"))

    # Points from Energy label # AH3
    # =IF(ISBLANK(R24),IF(AND(K23<1976,R22="None"),0,IF(AND(K23>=1976,R22="None"),INDEX($'Energy Data Dont touch'.$A$20:$D$66,MATCH(K23,$'Energy Data Dont touch'.$A$20:$A$66,0),IF(AD3="Single",3,IF(AD3="Multi",4))),IF(K10<=25,VLOOKUP("*"&(R22)&"*",$'Energy Data Dont touch'.$B$3:$D$11,IF(AD3="Single",2,IF(AD3="Multi",3)),),IF(AND(K10>25,K10<=40),VLOOKUP("*"&(R22)&"*",$'Energy Data Dont touch'.$G$3:$I$11,IF(AD3="Single",2,IF(AD3="Multi",3)),0),IF(AND(K10>40,$K10<=200),VLOOKUP("*"&(R22)&"*",$'Energy Data Dont touch'.$L$3:$N$11,IF(AD3="Single",2,IF(AD3="Multi",3)),0)))))),VLOOKUP(R24,$'Energy Data Dont touch'.$G$19:$I$319,IF(AD3="Single",2,3),0))


    # Points (living space) # T3
    # 75
    # =K10-1+0.75*N3+IF(K12="No",0,IF(K12="Yes",2))+(IF(K12="Yes",(ROUNDUP(L12/24.99,0)*2),IF(K12="No",-5,IF(K12="Shared",(ROUNDUP(L12/Q12/24.99,0)*2)))))

    # Major Renovation # Y3
    # False

    # Renovation without EI improvement #Z3
    # False

    # Estimated Renovation # AA3
    # null

    # Video Intercom # AB3
    # False

    # Heating # AC3
    # Central

    # Single/Multi Family # AD3
    # Multi

    # WOZ (unadjusted for 33% rule) # AI3
    # =IF(AND(K25="Yes",K23>2018,K10<40),K21/12090+K21/K10/80,K21/12090+K21/K10/189)

    # WOZ (adjusted if 33% rule applies) # AJ3
    # =IF(K5=2023,IF(ROUND(T3+AK3+AO3+AI3,0)>149,0.5*(T3+AK3+AO3),AI3),IF(ROUND(T3+AK3+AO3+AI3,0)>142,0.5*(T3+AK3+AO3),AI3))

    # General # AK3
    # =ROUND(IF(AG3="Yes",50,0)+IF(AB3="Yes",0.25,0)+(K8*IF(AC3="Central",2,IF(AC3="Block",1.5,IF(AC3="None",0))))+(M3*IF(AC3="Central",2,IF(AC3="Block",1.5,IF(AC3="None",0))))+AH3+AA3/10000*2,0)

    # Points for both # AO3
    # =VLOOKUP(K14,$'Kitchen and Bathroom'.$D$2:$E$6,2,0)+VLOOKUP(K18,$'Kitchen and Bathroom'.$D$29:$E$31,2,0)

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