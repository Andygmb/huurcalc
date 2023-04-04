from enum import Enum
from math import ceil
from dataclasses import dataclass


@dataclass
class HuurCalc:
    room_studio_sqm: int = 0  # C4
    total_shared_area_sqm: int = 0  # D4
    shared_living_room: bool = False  # e4
    shared_kitchen: bool = False  # F4
    shared_shower: bool = False  # G4
    shared_toilet: bool = False  # H4
    total_residents: int = 1  #

    # advanced calc
    move_in_year: int = 2023  # K5
    number_of_main_rooms: int = 1  # K8
    total_living_space_sqm: int = 74  # K10
    has_outdoor_space: bool = True  # K12
    outdoor_space_sqm: int = 0  # L12
    outdoor_space_shared: bool = True  # ?
    outdoor_space_residents: int = 2  # Q12
    kitchen_description: str = "Modern"  # K14
    bathroom_description: str = "Modern"  # K18
    woz_value: int = 0  # K21
    build_year: int = 1995  # K23
    amsterdam_or_ultrecht: bool = False  # K25
    has_video_intercom: bool = False  # AB3
    heating_type: str = "Central"  # AC3
    # TODO: is estimated_renovation a point value? ask Shane
    estimated_renovation: int = 0  # AA3
    renovation_without_ei_improvment: bool = False  # Z3
    number_of_closets_storage_rooms_heated: int = 0  # M3
    total_space_closets_storage_heated: int = 0  # N3
    size_of_storage_room_or_bike_shed_unheated_sqm: float = 0  # O3
    energy_label: str = "C"  # R22
    energy_index: int = 3  # R24
    national_monument: bool = False  # AG3
    single_or_multi: int = 1  # AD3 # single = 0, multi = 1
    carport: bool = False  # P3
    major_renovation: bool = False  # Y3
    # TODO add calculations for each type based upon values in the Kitchen and Bathroom subsheet
    KITCHEN_CHOICES = {
        'Bare/Small': 1,
        'Basic Essential': 5.5,
        'Modern': 9,
        'Large': 13.25,
        'Jamies Kitchen': 20.25,
    }
    BATHROOM_CHOICES = {
        'Basic': 8,
        'Modern': 9.75,
        'Modern with bath': 11.75,
    }
    ENERGY_RATINGS = [
        "A++",
        "A+",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
    ]
    ENERGY_RATINGS_PTS = {
        (0, 25): [[52, 48, 44, 40, 36, 32, 22, 4, 0], [48, 44, 40, 36, 32, 28, 15, 1, 0]],
        (25, 40): [[48, 44, 40, 36, 32, 22, 14, 4, 0], [44, 40, 36, 32, 28, 15, 11, 1, 0]],
        (40, 200): [[44, 40, 36, 32, 22, 14, 8, 4, 0], [40, 36, 32, 28, 15, 11, 5, 1, 0]]
    }
    YEAR_RATING_PTS = {
        (0, 1976): [0, 0],
        (1977, 1978): [4, 1],
        (1979, 1983): [8, 5],
        (1984, 1991): [14, 11],
        (1992, 1997): [22, 11],
        (1998, 1999): [22, 15],
        (2000, 2001): [32, 28],
        (2002, 2023): [36, 32],
    }
    ENERGY_INDEX_PTS = {
        (0, 0.60): (44, 40),
        (0.61, 0.80): (40, 36),
        (0.81, 1.20): (36, 32),
        (1.21, 1.40): (32, 28),
        (1.41, 1.80): (22, 15),
        (1.81, 2.10): (14, 11),
        (2.11, 2.40): (8, 5),
        (2.41, 2.70): (4, 1),
        (2.71, float('inf')): (0, 0)
    }

    HEATING_TYPE_MULTIPLIERS = {
        'Central': 2,
        'Block': 1.5,
        'None': 0,
        None: 0
    }

    def lux_points(self) -> float:  # AP3
        return 0.0  # AP3

    def number_of_points(self) -> float:  # Q9
        """
        # number of points # Q9
        # =ROUND(self.points_for_living_space()+self.general()+self.points_for_both()+AJ3+AP3,0)
        """
        return ceil(
            self.points_for_living_space() +
            self.general() +
            self.points_for_both() +
            self.woz_points_adjusted() +
            self.lux_points()
        )

    def woz_points_unadjusted(self) -> float:  # AI3
        """
        # WOZ (unadjusted for 33% rule)
        # =IF(AND(self.amsterdam_or_ultrecht="Yes",self.build_year>2018,self.total_living_space_sqm<40),
        #     self.woz_value/12090+self.woz_value/self.total_living_space_sqm/80,
        #     self.woz_value/12090+self.woz_value/self.total_living_space_sqm/189
        #     )
        """
        if self.amsterdam_or_ultrecht and self.build_year > 2018 and self.total_living_space_sqm < 40:
            return self.woz_value / 12090 + self.woz_value / self.total_living_space_sqm / 80  # TODO what are these
        return self.woz_value / 12090 + self.woz_value / self.total_living_space_sqm / 189  # TODO what are these

    def woz_points_adjusted(self) -> float:  # AJ3
        """
        WOZ (adjusted if 33% rule applies)
        # =IF(self.move_in_year=2023,
            IF(ROUND(self.points_for_living_space()+self.general()+self.points_for_both()+AI3,0)>149,
                0.5*(self.points_for_living_space()+self.general()+self.points_for_both()),
                AI3),
            IF(ROUND(self.points_for_living_space()+self.general()+self.points_for_both()+AI3,0)>142,
                0.5*(self.points_for_living_space()+self.general()+self.points_for_both()),
                AI3)
            )
        """
        # what is this
        some_woz_calculation = ceil(
            self.points_for_living_space() +
            self.general() +
            self.points_for_both() +
            self.woz_points_unadjusted()
        )
        if self.move_in_year == 2023:
            if some_woz_calculation > 149:  # TODO whats this number from
                return 0.5 * self.points_for_living_space() + self.general() + self.points_for_both()
        elif some_woz_calculation > 142:  # TODO whats this number from
            return 0.5 * self.points_for_living_space() + self.general() + self.points_for_both()
        return self.woz_points_unadjusted()

    def max_legal_rent_price(self) -> float:  # Q5
        if 5.44 * self.number_of_points() - 10.4 < 208:
            return 208
        else:
            return 5.44 * self.number_of_points() - 10.4

    def can_rent_be_reduced(self) -> tuple[bool, str]:  # R5
        """
        # can this rent price be reduced? # R5
        # =IF(self.move_in_year=2023,
            IF(Q5>808,
                "No, If it is above 808, it cannot be reduced",
                "Possibly. It is below 808 euro so would qualify for a reduction if this calculation is correct"
                ),
            IF(Q5>763,
                "No, If it is above 763, it cannot be reduced",
                "Possibly. It is below 763 euro so would qualify for a reduction if this calculation is correct")
                )
        """
        if self.move_in_year == 2023:
            if self.max_legal_rent_price() > 808:
                return False, "No, If it is above 808, it cannot be reduced"
            else:
                return True, "Possibly. It is below 808 euro so would qualify for a reduction if this calculation is correct"
        else:
            if self.max_legal_rent_price() > 763:
                return False, "No, If it is above 763, it cannot be reduced"
            else:
                return True, "Possibly. It is below 763 euro so would qualify for a reduction if this calculation is correct"

    def points_for_living_space(self) -> float:  # T3
        """
            =self.total_living_space_sqm-1+0.75*N3+outdoor_space_points+(IF(
                self.has_outdoor_space="Yes",
                    (ROUNDUP(self.outdoor_space_sqm/24.99,0)*2),
                    IF(self.has_outdoor_space="No",
                        -5,
                        IF(K12="Shared",
                            (ROUNDUP(self.outdoor_space_sqm/self.outdoor_space_residents/24.99,0)*2))
                            )
                    ))
        """
        # TODO better name here than bonus points
        # TODO 24.99 and * 2 are magic numbers
        outdoor_space_points = 2 if self.has_outdoor_space else 0
        outdoor_space_bonus_points = -5  # default if not has_outdoor_space
        if self.has_outdoor_space:
            if self.outdoor_space_shared:
                outdoor_space_bonus_points = ceil(self.outdoor_space_sqm / self.outdoor_space_residents / 24.99) * 2
            else:
                outdoor_space_bonus_points = ceil(self.outdoor_space_sqm / 24.99) * 2
        return self.total_living_space_sqm - 1 + 0.75 * self.total_space_closets_storage_heated + outdoor_space_points + outdoor_space_bonus_points

    def points_from_energy_label(self) -> float | int:  # AH3
        # Points from Energy label # AH3
        """
         =IF(ISBLANK(self.energy_index),
            IF(AND(self.build_year<1976,self.energy_label="None"),
                0,
                IF(AND(self.build_year>=1976,self.energy_label="None"),
                    INDEX($'Energy Data Dont touch'.$A$20:$D$66,MATCH(self.build_year,$'Energy Data Dont touch'.$A$20:$A$66,0),IF(AD3="Single",3,IF(AD3="Multi",4))),
                    IF(self.total_living_space_sqm<=25,
                        VLOOKUP("*"&(self.energy_label)&"*",$'Energy Data Dont touch'.$B$3:$D$11,IF(AD3="Single",2,IF(AD3="Multi",3)),),
                        IF(AND(self.total_living_space_sqm>25,self.total_living_space_sqm<=40),
                            VLOOKUP("*"&(self.energy_label)&"*",$'Energy Data Dont touch'.$G$3:$I$11,IF(AD3="Single",2,IF(AD3="Multi",3)),0),
                            IF(AND(self.total_living_space_sqm>40,$self.total_living_space_sqm<=200),
                                VLOOKUP("*"&(self.energy_label)&"*",$'Energy Data Dont touch'.$L$3:$N$11,IF(AD3="Single",2,IF(AD3="Multi",3)),0)
                                ))
                            )))
            ,VLOOKUP(self.energy_index,$'Energy Data Dont touch'.$G$19:$I$319,IF(AD3="Single",2,3),0))
        """
        if self.energy_index:
            for index_range, values in self.ENERGY_INDEX_PTS.items():
                if index_range[0] <= self.energy_index <= index_range[1]:
                    return values[0] if self.single_or_multi == 0 else values[1]
        else:
            if self.build_year < 1976 and not self.energy_label:
                return 0.0
            elif self.build_year >= 1976 and not self.energy_label:
                for index_range, values in self.YEAR_RATING_PTS.items():
                    if index_range[0] <= self.build_year <= index_range[1]:
                        return values[0] if self.single_or_multi == 0 else values[1]
            else:
                for index_range, values in self.ENERGY_RATINGS_PTS.items():
                    if index_range[0] <= self.total_living_space_sqm <= index_range[1]:
                        return values[0][self.ENERGY_RATINGS.index(self.energy_label)] if self.single_or_multi == 0 else values[1][self.ENERGY_RATINGS.index(self.energy_label)]

        raise Exception

    def general(self) -> float:  # AK3
        """
        =ROUND(
            IF(
                self.national_monument="Yes",
                    50,
                    0
                ) +
                IF(AB3="Yes",
                    0.25,
                    0
                ) +
                (self.number_of_main_rooms * IF(
                    AC3="Central",
                    2,
                    IF(AC3="Block",
                        1.5,
                        IF(AC3="None",0))))
                + (
                    M3 * IF(
                        AC3="Central",
                            2,
                            IF(AC3="Block",
                                1.5,
                                IF(AC3="None",
                                0
                                ))))+AH3+AA3/10000*2,0)
        """
        national_monument_pts = 50 if self.national_monument else 0
        video_intercom_pts = 0.25 if self.has_video_intercom else 0
        main_rooms_pts = self.number_of_main_rooms * self.HEATING_TYPE_MULTIPLIERS[self.heating_type]
        closets_storage_room_pts = self.number_of_closets_storage_rooms_heated * self.HEATING_TYPE_MULTIPLIERS[
            self.heating_type]
        return ceil(
            national_monument_pts +
            video_intercom_pts +
            main_rooms_pts +
            closets_storage_room_pts +
            self.points_from_energy_label() +
            (self.estimated_renovation / 10000 * 2)
        )

    def points_for_both(self) -> float:  # AO3
        kitchen_pts = self.KITCHEN_CHOICES[self.kitchen_description]
        bathroom_pts = self.BATHROOM_CHOICES[self.bathroom_description]
        return kitchen_pts + bathroom_pts

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
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def calculate_points(self, simple=False, advanced=False) -> float:
        if simple:
            return sum([self.dependant_room_sqm_points,
                        self.heating_points,
                        self.bonus_points(bonus_type="kitchen"),
                        self.bonus_points(bonus_type="toilet"),
                        self.bonus_points(bonus_type="shower"),
                        self.heating_control,
                        self.balcony,
                        self.bedshed])
        elif advanced:
            return ceil(
                self.points_for_living_space() +
                self.general() +
                self.points_for_both() +
                self.woz_points_adjusted() +
                self.lux_points()
            )
        return 0.0

    @property
    def estimated_rent_price(self) -> float:
        points = self.calculate_points(simple=True)
        return round(
            self.MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_1 * points ** 2 +
            self.MAGIC_NUMBER_RENT_PRICE_MULTIPLIER_2 * points
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
        return 3  # assume present

    @property
    def balcony(self) -> int:
        return 6  # assume present

    @property
    def bedshed(self) -> int:
        return 3  # assume present

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
    room_studio_sqm=0,  # C4
    total_shared_area_sqm=0,  # D4
    shared_living_room=False,  # e4
    shared_kitchen=False,  # F4
    shared_shower=False,  # G4
    shared_toilet=False,  # H4
    total_residents=1,  #
    # advanced calc values
    move_in_year=2023,  # K5
    number_of_main_rooms=1,  # K8
    total_living_space_sqm=74,  # K10
    has_outdoor_space=True,  # K12
    outdoor_space_sqm=0,  # L12
    outdoor_space_shared=True,  # ?
    outdoor_space_residents=2,  # Q12
    kitchen_description="Modern",  # K14
    bathroom_description="Modern",  # K18
    woz_value=0,  # K21
    build_year=1995,  # K23
    amsterdam_or_ultrecht=False,  # K25
    has_video_intercom=False,  # AB3
    heating_type="Central",  # AC3
    estimated_renovation=0,  # AA3
    renovation_without_ei_improvment=False,  # Z3
    number_of_closets_storage_rooms_heated=0,  # M3
    total_space_closets_storage_heated=0,  # N3
    size_of_storage_room_or_bike_shed_unheated_sqm=0,  # O3
    energy_label="C",  # R22
    energy_index=3,  # R24
    national_monument=False,  # AG3
    single_or_multi=1,  # AD3 # single = 0, multi = 1
    carport=False,  # P3
    major_renovation=False,  # Y3
)

# print(calculator.calculate_points(simple=True))
# print(calculator.estimated_rent_price)
# print(calculator.points_for_both())
print(calculator.calculate_points(advanced=True))
