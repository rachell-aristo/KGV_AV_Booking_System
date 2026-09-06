const bookingDataEl = document.getElementById('booking-data');
const fullyBookedDays = JSON.parse(bookingDataEl.dataset.fullyBooked);   
// Parses the python array into format JS understands from html file
   const fp = flatpickr("#booking-date", {
      minDate: "today",
      allowInput:true,
      disable: [
         function(date) {
            return date.getDay() === 0 || date.getDay() === 6;
         }
      ],  altInput: true, altFormat: "F j, Y", dateFormat: "Y-m-d",
      // how this works is if function returns true, date gets disabled. So it goes through dates dynamically, not pre determined all at once
   });
   let selectedStudioId = "";
   let bookingdate = "";
   let options = "";
   function fetchBookedSlots() {
      console.log("Reached fetch booked slots")
      options = document.querySelectorAll('#timeslot-select option'); //selects all option elements that are children of this id
      fetch(`/booked_slots?date=${bookingdate}&studio=${selectedStudioId}`)
      // asynchronus fetch, sends data request to server 
      .then(response => response.json()) //take raw HTML data and JSONify
      .then(data => { //now that data is called 'data' and parsed into this function
         options.forEach(function(option) { //for loop that runs this function for each timeslot option element
            if (data.includes(parseInt(option.value))) { //if any of timeslot options are in booked slots, disable it
               option.disabled = true;
            } else {
               option.disabled = false;
            }
         });
         document.getElementById('timeslot-select').selectedIndex = 0; 
         //automatically resets selected time slot to first placeholder value
         });
   }

   const studioCards = document.querySelectorAll('.studio-card');

   studioCards.forEach(function(card){
      card.addEventListener('click',function(){
         selectedStudioId = this.dataset.studioId;
         document.getElementById('selected-studio-space').value = selectedStudioId;
         console.log("Selected Studio ID:", selectedStudioId);

         let setupOptions = document.querySelectorAll('#setup-select option');
         document.getElementById('setup-select').disabled = false; //enables setup options after studio is picked
         document.getElementById('setup-select').selectedIndex = 0; //resets setup option to placeholder (in case studio was changed, not first time selected)
         setupOptions.forEach(function(option) {
            if (option.dataset.studio === selectedStudioId) { 
               //if in the setup options, the option is applicable to the selectedStudio (by checking if the value of data-studio matches the currently selected studio_id) 
               option.style.display = 'block'; //display the optioj
            } else {
               option.style.display = 'none'; //otherwise hide it
            }
         });
         fetchBookedSlots() //rechecks if timeslot options need to be updated since studio changed
         console.log("get booked")
         fp.set("disable", [function(date) { 
            return date.getDay() === 0 || date.getDay() === 6;
            allowInput:true;
         }, ...(fullyBookedDays[selectedStudioId]|| [])]); //disables days on calendar where the studio is fully booked
         if ((fullyBookedDays[selectedStudioId]|| []).includes(bookingdate)){ //if the currently selected booking date is in fully booked days array, clear date selection
            fp.clear();
            document.getElementById('timeslot-select').selectedIndex = 0; //go back to placeholder timeslot option
         }
      });
   });
   

   document.getElementById('booking-date').addEventListener('change', function() { //when booking date is changed:
      bookingdate = this.value; //set var to new bookingdate value
      options = document.querySelectorAll('#timeslot-select option'); 
      document.getElementById('timeslot-select').disabled = false; //show all timeslots
      document.getElementById('timeslot-select').selectedIndex = 0; //set current time slots to placeholder
      fetchBookedSlots() //removes timeslots which are full
   });

   document.querySelector('form').addEventListener('submit', function(event) { //when form is submitted
    if (!document.getElementById("setup-select").value){ //if setup has no value
      event.preventDefault();  // stops the form from submitting
      document.getElementById('error-message').textContent = "Please select a setup option.";
    }
    if (!document.getElementById("timeslot-select").value){
      event.preventDefault();  // stops the form from submitting
      document.getElementById('error-message').textContent = "Please select a timeslot.";
    }
    //The reason we need these js validation checks is because it's possible for user to select the placeholder option
     
    });