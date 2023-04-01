class HuurCalc {
  constructor(room_studio_sqm = 0, total_shared_area_sqm = 0, shared_living_room = false, shared_kitchen = false, shared_shower = false, shared_toilet = false, total_residents = 1) {
    this.room_studio_sqm = room_studio_sqm;
    this.total_shared_area_sqm = total_shared_area_sqm;
    this.shared_living_room = shared_living_room;
    this.shared_kitchen = shared_kitchen;
    this.shared_shower = shared_shower;
    this.shared_toilet = shared_toilet;
    this.total_residents = total_residents;
  }

  calculate_points() {
    const dependant_room_sqm_points = parseFloat((this.room_studio_sqm + this.total_shared_area_sqm / (this.total_residents + 1)) * 5).toFixed(1);
    const heating_points = parseFloat(this.room_studio_sqm * 0.75).toFixed(2);
    const kitchen_bonus_points = this.shared_kitchen ? (this.total_residents <= 5 ? 4 : 0) : 20;
    const toilet_bonus_points = this.shared_toilet ? (this.total_residents <= 5 ? 4 : 0) : 22;
    const shower_bonus_points = this.shared_shower ? (this.total_residents <= 8 ? 3 : 0) : 15;
    const bonus_points = parseFloat(kitchen_bonus_points + toilet_bonus_points + shower_bonus_points).toFixed(1);

    return parseFloat(dependant_room_sqm_points) + parseFloat(heating_points) + parseFloat(bonus_points) + 3 + 6 + 3;
  }

  get estimated_rent_price() {
    const points = this.calculate_points();
    const rent_price = -0.0019 * points ** 2 + 2.3917 * points + 7.5176;

    return parseFloat(rent_price).toFixed(2);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var calculateButton = document.getElementById('calculate-button');
  calculateButton.addEventListener('click', function() {
    var roomStudioSqmInput = document.getElementById('room-studio-sqm');
    var totalSharedAreaSqmInput = document.getElementById('total-shared-area-sqm');
    var sharedLivingRoomInput = document.getElementById('shared-living-room');
    var sharedKitchenInput = document.getElementById('shared-kitchen');
    var sharedShowerInput = document.getElementById('shared-shower');
    var sharedToiletInput = document.getElementById('shared-toilet');
    var totalResidentsInput = document.getElementById('total-residents');

    var roomStudioSqm = parseInt(roomStudioSqmInput.value);
    var totalSharedAreaSqm = parseInt(totalSharedAreaSqmInput.value);
    var sharedLivingRoom = sharedLivingRoomInput.checked;
    var sharedKitchen = sharedKitchenInput.checked;
    var sharedShower = sharedShowerInput.checked;
    var sharedToilet = sharedToiletInput.checked;
    var totalResidents = parseInt(totalResidentsInput.value);

    var calculator = new HuurCalc(
      room_studio_sqm = roomStudioSqm,
      total_shared_area_sqm = totalSharedAreaSqm,
      shared_living_room = sharedLivingRoom,
      shared_kitchen = sharedKitchen,
      shared_shower = sharedShower,
      shared_toilet = sharedToilet,
      total_residents = totalResidents
    );

    var pointsOutput = document.getElementById('points-output');
    var rentPriceOutput = document.getElementById('rent-price-output');
    pointsOutput.textContent = calculator.calculate_points();
    rentPriceOutput.textContent = calculator.estimated_rent_price;
  });
});