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
                return
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
                document.querySelectorAll(".off-limits-msg").forEach(function(message){
                    message.remove()
                });
                document.querySelectorAll(".unavailable-msg").forEach(function(message){
                    message.remove()
                });
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
                            if (card.dataset.id == type){
                                card.appendChild(offLimits);
                                card.querySelector(".quantity-select").style.display = "none";
                                card.querySelector(".quantity-select").selectedIndex = -1;
                                card.querySelector('label[for="quantity"]').style.display = "none";

                            }
                        }); 
                    } else if (quantity <= 0){
                        let unavailable = document.createElement('div')
                        unavailable.textContent = 'Fully booked for these dates';
                        unavailable.style.display = "block"
                        unavailable.className = "unavailable-msg"
                        document.querySelectorAll(".container").forEach(function(card){
                            if (card.dataset.id === type){
                                card.appendChild(unavailable);
                                card.querySelector(".quantity-select").style.display = "none";
                                card.querySelector(".quantity-select").selectedIndex = -1; 
                                card.querySelector('label[for="quantity"]').style.display = "none";
                            }
                        }); 
                    } else{
                        selectElements.forEach(function(select) {
                            if (select.dataset.id == type){
                                select.closest('.container').querySelector('label[for="quantity"]').style.display = "";
                                select.innerHTML = "";
                                select.style.display = ""
                                for (let i = 0; i < quantity+1;i++){
                                    select.add(new Option(String(i),i))
                                }
                                
                            }
                        })
                    }
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



let form = document.querySelector('form')

if (form !== null){
    form.addEventListener('submit', function(event) { //when form is submitted
        const form = document.querySelector('form');

        const items = {}
        document.querySelectorAll(".equip-card").forEach(function(card){
            const id = card.dataset.equipId
            const qty = parseInt(card.querySelector(".quantity-select").value)
            if (qty>0){
                items[id] = qty
            }

        });
        if (Object.keys(items).length === 0){
            event.preventDefault();  // stops the form from submitting
            document.getElementById('error-message').textContent = "Please select at least one item to loan."; //CHECK IF THESE CHECKS WORK
        } else{
            document.getElementById('selected-equip').value = JSON.stringify(Object.keys(items).map(Number));
            document.getElementById('selected-quants').value = JSON.stringify(Object.values(items).map(Number)); 
        }
 
    });


}


