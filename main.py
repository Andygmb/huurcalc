from math import ceil, floor
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
        'Bare/Small': 8,
        'Modern': 11,
        'Modern with bath': 12,
        'High end': 14.75,
    }
    ENERGY_RATINGS = ["A++", "A+", "A", "B", "C", "D", "E", "F", "G", ]
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
        Returns the sum of the points for the living space, the general points, the points for both, the adjusted WOZ
        points, and the luxury points, rounded up to the nearest integer.
        """
        return floor(
            self.points_for_living_space() +
            self.general_points() +
            self.points_for_both() +
            self.woz_points_adjusted() +
            self.lux_points(),
        )

    def woz_points_unadjusted(self) -> float:  # AI3
        """
        Returns the WOZ points based on the WOZ value, the total living space, the build year, and whether the
        apartment is located in Amsterdam or Utrecht.
        """
        if self.amsterdam_or_ultrecht and self.build_year > 2018 and self.total_living_space_sqm < 40:
            return round(self.woz_value / 12090 + self.woz_value / self.total_living_space_sqm / 80, 2)  # TODO what
            # are these
        return round(self.woz_value / 12090 + self.woz_value / self.total_living_space_sqm / 189, 2)  # TODO what are
        # these

    def woz_points_adjusted(self) -> float:  # AJ3
        """
        Returns the adjusted WOZ points based on the unadjusted WOZ points and the move-in year parameter. If the
        adjusted WOZ points are less than or equal to the unadjusted WOZ points, returns the unadjusted WOZ points.
        """
        some_woz_calculation = round(
            self.points_for_living_space() +
            self.general_points() +
            self.points_for_both() +
            self.woz_points_unadjusted(), 0
        )
        if self.move_in_year == 2023:
            if some_woz_calculation > 149:  # TODO whats this number from
                return ceil(0.5 * (self.points_for_living_space() + self.general_points() + self.points_for_both()))
            else:
                return self.woz_points_unadjusted()
        elif some_woz_calculation > 142:  # TODO whats this number from
            return ceil(0.5 * (self.points_for_living_space() + self.general_points() + self.points_for_both()))
        else:
            return self.woz_points_unadjusted()

    def max_legal_rent_price(self) -> float:  # Q5
        """
        Returns the maximum legal rent price based on the number of points, which is the product of 5.44 and the
        number of points, minus 10.4 if the result is greater than or equal to 208, and rounded to two decimal places.
        """
        if 5.44 * self.number_of_points() - 10.4 < 208:
            return 208.00
        else:
            return round(5.44 * self.number_of_points() - 10.4, 2)

    def can_rent_be_reduced(self) -> tuple[bool, str]:  # R5
        """
        Returns a tuple indicating whether the rent can be reduced and an explanation. The first element is a boolean
        indicating whether the maximum legal rent price is less than or equal to the threshold for rent reduction,
        which is 763 for move-in year 2022 and 808 for move-in year 2023. The second element is a string explaining
        the result.
        """
        if self.move_in_year == 2023:
            if self.max_legal_rent_price() > 808:
                return False, "No, If it is above 808, it cannot be reduced"
            else:
                return True, "Possibly. It is below 808 euro so would qualify for a reduction if this calculation is " \
                             "correct "
        else:
            if self.max_legal_rent_price() > 763:
                return False, "No, If it is above 763, it cannot be reduced"
            else:
                return True, "Possibly. It is below 763 euro so would qualify for a reduction if this calculation is " \
                             "correct "

    def points_for_living_space(self) -> float:  # T3
        """
        Returns the points for the living space based on the total living space, the total space of closets and
        storage that is heated, and whether the apartment has outdoor space. If the apartment has outdoor space,
        the points are adjusted based on the outdoor space's size and whether it is shared with other residents.
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
        return self.total_living_space_sqm - 1 + 0.75 * \
            self.total_space_closets_storage_heated + outdoor_space_points + outdoor_space_bonus_points

    def points_from_energy_label(self) -> float | int:  # AH3
        """
        Returns the points from the energy label based on the energy index, energy label, total living space,
        build year, and whether the apartment is single or multi-occupancy. If the apartment has no energy label and
        was built before 1976, the points are zero. If the apartment has no energy label and was built in or after
        1976, the points are based on the build year. Otherwise, the points are based on the energy label and the
        size of the apartment.
        """
        if self.energy_index:
            for index_range, values in self.ENERGY_INDEX_PTS.items():
                if index_range[0] <= self.energy_index <= index_range[1]:
                    return values[self.single_or_multi]
        else:
            if self.build_year < 1976 and not self.energy_label:
                return 0.0
            elif self.build_year >= 1976 and not self.energy_label:
                for index_range, values in self.YEAR_RATING_PTS.items():
                    if index_range[0] <= self.build_year <= index_range[1]:
                        return values[self.single_or_multi]
            else:
                for index_range, values in self.ENERGY_RATINGS_PTS.items():
                    if index_range[0] <= self.total_living_space_sqm <= index_range[1]:
                        return values[self.single_or_multi][self.ENERGY_RATINGS.index(self.energy_label)]

        raise Exception

    def general_points(self) -> float:  # AK3
        """
        Returns the general points based on whether the apartment is a national monument, has a video intercom, and the
        number of main rooms and the heating type.
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

    def calculate_points(self) -> float:
        print(f"""
{self.points_from_energy_label()=} ✔
{self.points_for_living_space()=} ✔
{self.woz_points_unadjusted()=} ✔
{self.max_legal_rent_price()=} ✔
{self.woz_points_adjusted()=} ✔
{self.number_of_points()=}✔ 
{self.points_for_both()=} ✔
{self.general_points()=} ✔
{self.lux_points()=} ✔
""")
        return self.number_of_points()


calculator = HuurCalc(
    # advanced calc values
    move_in_year=2023,  # K5
    number_of_main_rooms=2,  # K8
    total_living_space_sqm=45,  # K10
    has_outdoor_space=False,  # K12
    outdoor_space_sqm=0,  # L12
    outdoor_space_shared=False,  # ?
    outdoor_space_residents=0,  # Q12
    kitchen_description="Basic Essential",  # K14
    bathroom_description="Modern",  # K18
    woz_value=292000,  # K21
    build_year=2019,  # K23
    amsterdam_or_ultrecht=True,  # K25
    has_video_intercom=False,  # AB3
    heating_type="Central",  # AC3
    estimated_renovation=0,  # AA3
    renovation_without_ei_improvment=False,  # Z3
    number_of_closets_storage_rooms_heated=0,  # M3
    total_space_closets_storage_heated=0,  # N3
    size_of_storage_room_or_bike_shed_unheated_sqm=0,  # O3
    energy_label="A",  # R22
    energy_index=0,  # R24
    national_monument=False,  # AG3
    single_or_multi=1,  # AD3 # single = 0, multi = 1
    carport=False,  # P3
    major_renovation=False,  # Y3
)


print(f"""Points calculated: {calculator.calculate_points()}
Max legal rent price: €{calculator.max_legal_rent_price()}
Can rent be reduced? {calculator.can_rent_be_reduced()}
""")
