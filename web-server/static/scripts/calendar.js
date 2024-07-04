document.addEventListener("DOMContentLoaded", async event => {
    // Fetch data from sever
    let eventsArray = []
    let millisecondsInDay = 24 * 60 * 60 * 1000

    function getAllEvents() {
        return new Promise((resolve, reject) => {
            fetch("/events").then(async response => {
                if(response.status == 200) eventsArray = await response.json()
                resolve(eventsArray)
            }).catch(err => {
                reject(err)
            })
        })
    }

    function getRecentEvents() {
        let result = []
        let nowTime = new Date().getTime()
        for(let i = 0; i < eventsArray.length; i++) {
            let eventTime = new Date(eventsArray[i].event_time).getTime() // Formatting to Date in case we got string instead of timestamp
            if(eventTime - nowTime <= millisecondsInDay) result.push(eventsArray[i])
        }
        return result
    }

    function getEventsByDate(date) {
        let resArray = []
        for(let i = 0; i < eventsArray.length; i++) {
            let eventDate = new Date(eventsArray[i].event_time)
            if(date.toDateString() == eventDate.toDateString()) resArray.push(eventsArray[i])
            else console.log(date.toDateString(), eventDate.toDateString())
        }
        return resArray
    }

    // EMAIL SUB MODAL SCRIPT
    const modal = document.getElementById("email-sub-modal")
    const modalForm = document.getElementById("email-sub-form")
    const modalFormComment = document.getElementById("email-form-comment")
    document.getElementById("mail-subscribe").addEventListener("click", () => {
        modal.style.display = "flex"    
    })
    function hideEmailModal() {
        if(modal.style.display == "none") return
        modal.style.display = "none"
        modalFormComment.textContent = ""
        // Anims?
    }
    function showEmailSubmitError(text) {
        modalFormComment.textContent = text
        modalFormComment.style.color = "red"
    }
    modal.addEventListener("click", event => {
        if(event.target.id == modal.id) hideEmailModal()
    })
    document.getElementById("email-sub-modal-close").addEventListener("click", () => hideEmailModal())
    modalForm.addEventListener("submit", async event => {
        event.preventDefault()
        const formData = new FormData(modalForm)
        let email = ""
        let categories = []
        formData.forEach((value, key) => {
            if(key == "email") email = value
            else if(value == "on") categories.push(key)
        })
        if(email.trim() == "") return showEmailSubmitError("Укажите адрес email")
        if(categories.length == 0) return showEmailSubmitError("Необходимо выбрать как минимум одну категорию уведомлений")

        fetch("/sub_email", {
            method: "POST",
            body: {email, categories}
        }).then(response => {
            modalFormComment.textContent = "Вы успешно подписались на email рассылку"
            modalFormComment.style.color = "green"
            setTimeout(() => {
                hideEmailModal()
            }, 3000)
        }).catch(() => showEmailSubmitError("Не удалось подписаться. Попробуйте позже"))
    })

    // EVENTS CARDS SCRIPT
    let cardWidth = 325 // From style.css
    let gap = 10

    const eventsCarousel = document.getElementById("events-carousel")
    document.getElementById("previous-event").addEventListener("click", () => {
        eventsCarousel.scrollLeft -= cardWidth + gap
    })
    document.getElementById("next-event").addEventListener("click", () => {
        eventsCarousel.scrollLeft += cardWidth + gap
    })

    const categoriesColors = {
        "Важное": "#F07427",
        "Мероприятие": "#36D593",
        "Обучение": "#627CFF"
    }

    function createEventCard(title, text, timestamp, category) {
        const cardTime = new Date(timestamp)
        let hours = cardTime.getHours()
        if(hours < 10) hours = `0${hours}`
        let minutes = cardTime.getMinutes()
        if(minutes < 10) minutes = `0${minutes}`

        const card = document.createElement("div")
        card.className = "event-card"

        const eventDate = document.createElement("div")
        eventDate.className = "event-date"

        const colorLine = document.createElement("div")
        let color
        if(!categoriesColors[category]) color = "#00AAF9" // Default Event Card Color
        else color = categoriesColors[category]
        colorLine.style.background = color
        colorLine.className = "color-line"
        eventDate.append(colorLine)

        const dateNumber = document.createElement("div")
        dateNumber.className = "date-number"
        dateNumber.textContent = cardTime.getDate()
        eventDate.append(dateNumber)

        const dateBlock = document.createElement("div")
        dateBlock.className = "date-block"
        const dateName = document.createElement("div")
        dateName.textContent = cardTime.toLocaleString('ru', {
            month: 'long',
            day: 'numeric'
        }).split(' ')[1]
        dateBlock.append(dateName)
        const dateTime = document.createElement("div")
        dateTime.textContent = `в ${hours}:${minutes}`
        dateBlock.append(dateTime)
        eventDate.append(dateBlock)

        const eventCategory = document.createElement("div")
        eventCategory.className = "event-category"
        let displayCategory = ""
        displayCategory = category
        eventCategory.textContent = displayCategory
        eventDate.append(eventCategory)

        const eventTitle = document.createElement("div")
        eventTitle.className = "event-title"
        eventTitle.textContent = title
        
        const eventTextContainer = document.createElement("div")
        eventTextContainer.className = "event-text-container"
        const eventText = document.createElement("div")
        eventText.className = "event-text"
        eventText.innerHTML = text.split("\n").join("<br>")
        eventTextContainer.append(eventText)

        card.append(eventDate)
        card.append(eventTitle)
        card.append(eventTextContainer)
        return card
    }

    // CALENDAR SCRIPT
    const refreshBtn = document.getElementById("refresh")
    let refreshClicked = false
    refreshBtn.addEventListener("click", async () => {
        if(refreshClicked) return
        refreshBtn.style.animation = "refresh-rotate 1s infinite"
        refreshClicked = true

        await getAllEvents()

        refreshBtn.style.animation = "none"
        refreshClicked = false
    })

    const calendar = document.getElementById("calendar")
    const currentMonthText = document.getElementById("current-month")
    let currentCalendar = {
        month: null,
        year: null
    }
    function updateCalendar(month, year) {
        let updateDate = new Date()
        let monthStart = new Date()
        monthStart.setFullYear(year, month, 1)
        let details = calendar.getElementsByClassName("calendar-cells-details")
        for(let i = 0; i < details.length; i++) {
            let detailBlock = details.item(i)
            hideDateDetails(detailBlock, true)
        }

        let monthName = monthStart.toLocaleString("default", {month: "long"})
        currentMonthText.textContent = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`
        currentCalendar = {month, year}
        
        // Works like offset for previous month in calendar
        let monthStartDay = monthStart.getDay() - 1
        if(monthStartDay == -1) monthStartDay = 6

        let currentCellDate = new Date(monthStart.getTime() - millisecondsInDay * monthStartDay)

        let cells = calendar.getElementsByClassName("calendar-cell")
        for(let i = 0; i < cells.length; i++) {
            let cell = cells.item(i)
            
            if(currentCellDate.getMonth() != monthStart.getMonth()) cell.classList.add("inactive")
            else cell.classList.remove("inactive")
            if(currentCellDate.toDateString() == updateDate.toDateString()) cell.classList.add("current-date")
            else cell.classList.remove("current-date")

            cell.children.item(0).textContent = currentCellDate.getDate()
            
            let dayEvents = getEventsByDate(currentCellDate) 
            cell.children.item(1).textContent = dayEvents.length
            cell.setAttribute("data-datestr", currentCellDate.toISOString())

            currentCellDate.setTime(currentCellDate.getTime() + millisecondsInDay)
        }
    }

    function outOfMonthsBounds(month, checkPrevious) {
        if(checkPrevious) return month - 1 < 0
        else return month + 1 >= 12
    }
    document.getElementById("previous-month").addEventListener("click", () => {
        let monthBack = currentCalendar.month
        let yearBack = currentCalendar.year
        if(outOfMonthsBounds(monthBack, true)) {
            monthBack = 11
            yearBack--
        } else monthBack--
        updateCalendar(monthBack, yearBack)
    })
    document.getElementById("next-month").addEventListener("click", () => {
        let monthFurther = currentCalendar.month
        let yearFurther = currentCalendar.year
        if(outOfMonthsBounds(monthFurther, false)) {
            monthFurther = 0
            yearFurther++
        } else monthFurther++
        updateCalendar(monthFurther, yearFurther)
    })
    document.getElementById("home-month").addEventListener("click", () => {
        let currentDate = new Date()
        if(currentCalendar.month == currentDate.getMonth() && currentCalendar.year == currentDate.getFullYear()) return
        updateCalendar(currentDate.getMonth(), currentDate.getFullYear())
    })


    /**
     * 
     * @param {Node} detailBar 
     */
    function hideDateDetails(detailBar, noAnims) {
        if(!detailBar.hasAttribute("data-showing")) return
        function closeDetails() {
            detailBar.style.animation = "none"
            detailBar.style.display = "none"
            detailBar.removeAttribute("data-showing")
        }
        if(noAnims === true) return closeDetails()
        detailBar.style.animation = ".5s open-details reverse"
        detailBar.addEventListener("animationend", closeDetails, {once: true})
    }


    function setDateDetails(date, detailBar) {
        let selectedDate = new Date(date)
        let selectedMonth = selectedDate.toLocaleString('ru', {
            month: 'long',
            day: 'numeric'
        }).split(' ')[1]

        const detailsContent = document.createElement("div")
        detailsContent.className = "calendar-details-content"

        const detailsHeader = document.createElement("div")
        detailsHeader.className = "calendar-details-header"
        const detailsTitle = document.createElement("h2")
        detailsTitle.textContent = `События на ${selectedDate.getDate()} ${selectedMonth}`
        detailsHeader.append(detailsTitle)
        const detailsClose = document.createElement("span")
        detailsClose.className = "material-symbols-rounded"
        detailsClose.textContent = "close"
        detailsClose.addEventListener("click", () => {
            hideDateDetails(detailBar, false)
        })
        detailsHeader.append(detailsClose)
        detailsContent.append(detailsHeader)

        const detailsCards = document.createElement("div")
        detailsCards.className = "calendar-details-cards"
        
        let dateEvents = getEventsByDate(selectedDate)
        for(let i = 0; i < dateEvents.length; i++) {
            let selectedEvent = dateEvents[i]
            let displayCard = createEventCard(selectedEvent.title, selectedEvent.description, selectedEvent.event_time, selectedEvent.category)
            detailsCards.append(displayCard)
        }
        if(dateEvents.length == 0) { // Add "Events empty" caption
            const emptyMessage = document.createElement("span")
            emptyMessage.textContent = "На эту дату не назначено событий"
            detailsCards.append(emptyMessage)
        }
        detailsContent.append(detailsCards)

        detailBar.innerHTML = ""
        detailBar.append(detailsContent)
    }

    /**
     * 
     * @param {Node} cell 
     * @param {Node} detailBar 
     */
    function showDateDetails(cell, detailBar) {
        let allDetails = calendar.getElementsByClassName("calendar-cells-details")
        for(let i = 0; i < allDetails.length; i++) {
            let currentDetails = allDetails.item(i)
            if(currentDetails == detailBar) continue
            if(currentDetails.hasAttribute("data-showing")) hideDateDetails(currentDetails)
        }
        // If details aren't displayed
        if(!detailBar.hasAttribute("data-showing")) {
            detailBar.style.display = "flex"
            detailBar.style.animation = ".5s open-details"
            detailBar.addEventListener("animationend", () => {
                detailBar.style.animation = "none"
            }, {once: true})
        }
        detailBar.setAttribute("data-showing", cell.getAttribute("data-datestr"))
        setDateDetails(cell.getAttribute("data-datestr"), detailBar)
    }

    function buildCalendarLayout() {
        calendar.innerHTML = ""
        let totalCells = 6 * 7
        let toBind = []
        for(let i = 0; i < totalCells; i++) {
            const cell = document.createElement("div")
            cell.className = "calendar-cell"

            const dateNumber = document.createElement("div")
            dateNumber.className = "date-number"
            cell.append(dateNumber)

            const cellDesc = document.createElement("div")
            cellDesc.className = "description"
            cell.append(cellDesc)

            calendar.append(cell)
            toBind.push(cell)

            // Each last day create new desc
            if((i+1)%7 == 0) {
                const details = document.createElement("div")
                details.className = "calendar-cells-details"

                details.style.display = "none"
                toBind.forEach((bindCell) => {
                    bindCell.addEventListener("click", () => {
                        if(bindCell.classList.contains("inactive")) return
                        showDateDetails(bindCell, details)
                    })
                })
                calendar.append(details)
                toBind = []
            }
        }
    }

    await getAllEvents()
    buildCalendarLayout()

    const recentEvents = getRecentEvents()
    if(recentEvents.length != 0) document.getElementById("events-carousel-empty").style.display = "none" 
    recentEvents.forEach((event) => {
        let eventCard = createEventCard(event.title, event.description, event.event_time, event.category)
        eventsCarousel.append(eventCard)
    })

    let now = new Date()
    updateCalendar(now.getMonth(), now.getFullYear())
    console.log("Calendar script loaded")
})