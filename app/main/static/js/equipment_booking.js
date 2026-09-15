const bookingData = document.getElementById('booking-data');
const fullyBookedDays = JSON.parse(bookingData.dataset.fullyBooked);  

const fp = flatpickr("#loan-period", {
    minDate: "today",
    mode: "range",
    allowInput:true,  
    altInput: true, 
    altFormat: "F j, Y", 
    dateFormat: "Y-m-d",
    onChange: function(selectedDates, dateStr, instance) {
        // Check if both dates are selected
        if (selectedDates.length === 2) {
            const startDate = selectedDates[0]; // JS Date Object
            const endDate = selectedDates[1];   // JS Date Object

            // To get them as formatted strings, use the built-in instance formatter:
            const startDateStr = instance.formatDate(startDate, "Y-m-d");
            const endDateStr = instance.formatDate(endDate, "Y-m-d");
            let timeDifference = endDate - startDate;
            let daysDifference = timeDifference / (1000 * 3600 * 24); //not including today

            //validation check
            if (daysDifference <= 3){
                document.querySelector("div.disabled")?.classList.remove("disabled");
                document.querySelector(".disabled-notice").style.display = "none";
            } else{
                alert("Maximum 3 days allowed! If you need to make a special request, please make note of it in the 'Extra notes' box")
                fp.clear()
            }
            
            // add verification that start date cannot be weekend
            // block bookings for today
            document.getElementById('loan-start-date').value = startDateStr;
            document.getElementById('loan-end-date').value = endDateStr;

            fetch('/get_available_equipment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    loan_start_date: startDateStr,
                    loan_end_date: endDateStr
                })
            })

            .then(response => response.json())
            .then(data => {
                let updated_quantity_dict = data
                console.log('Success:', updated_quantity_dict);
                let selectElements = document.querySelectorAll(".quantity-select")
                for (const [type, quantity] of Object.entries(updated_quantity_dict)){
                    if (quantity == "OFF_LIMITS"){
                        let offLimits = document.createElement('div')
                        offLimits.textContent = 'Not available for your year group';
                        offLimits.style.display = "block"
                        offLimits.className = "off-limits-msg"
                        document.querySelectorAll(".container").forEach(function(card){
                            if (card.dataset.equipId == type){
                                card.appendChild(offLimits);
                            }
                        }); // FIX THiS LATER & ADD MESSGA FOR FULLY BOOKED
                         // <p class="unavailable-msg" style="display: none;">Fully booked for these dates</p>
                    }
                    selectElements.forEach(function(select) {
                        if (select.dataset.id == type){
                            select.innerHTML = "";
                            select.style.display = "block"
                            for (let i = 0; i < quantity+1;i++){
                                select.add(new Option(String(i),i))
                            }
                            
                        }
                    })
                }
            })
            .catch(error => {
                console.error('Error:', error);
            })
        }
    }   
});

const tablinks = document.querySelectorAll(".tablinks");
tablinks.forEach(function(tab){
    tab.addEventListener('click',function(){ //when a tablink is clicked
    selectedcat = tab.dataset.catId;
    const tabcontent = document.querySelectorAll(".tabcontent");
    tabcontent.forEach(function(content){
        if (content.dataset.catId != selectedcat){ //if item doesn't belong to selected category
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
    for (let i = 0; i < tablinks.length; i++) { //makes non selected tab links inactive
        tablinks[i].classList.remove("active");
    }  
    tab.style.display = "block";
    tab.classList.add("active");
    });
});

selectedEquip = []; //list of ids
quants = [] //parallel list with quantities

const equipQuants = document.querySelectorAll(".quantity-select");
equipQuants.forEach(function(select){
    select.addEventListener('change',function(){ //when a quantity drop down's value is changed
    equipId = parseInt(select.closest('[data-equip-id]').dataset.equipId)
    let newQuant = parseInt(select.value)
    if (selectedEquip.includes(equipId) == true){
        quants[selectedEquip.indexOf(equipId)] = newQuant
        if (newQuant === 0){ //if an equipment is set to 0, remove from selected list
            quants.splice(quants[selectedEquip.indexOf(equipId)],1)
            selectedEquip.splice([selectedEquip.indexOf(equipId)],1)
        }
    } else if (newQuant !== 0){
        selectedEquip.push(equipId);
        quants.push(newQuant);
    }            
    console.log(selectedEquip)
    console.log(quants)
    });
});

let form = document.querySelector('form')

if (form !== null){
    form.addEventListener('submit', function(event) { //when form is submitted
        const form = document.querySelector('form');
        if (selectedEquip.length === 0){
            event.preventDefault();  // stops the form from submitting
            document.getElementById('error-message').textContent = "Please select at least one item to loan."; //CHECK IF THESE CHECKS WORK
        }
        
        document.getElementById('selected-equip').value = JSON.stringify(selectedEquip);
        document.getElementById('selected-quants').value = JSON.stringify(quants); 
    });


}


