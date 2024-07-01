document.addEventListener("DOMContentLoaded", async event => {
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
        }).catch(error => showEmailSubmitError("Не удалось подписаться. Попробуйте позже"))
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

    const categories = {
        "important": {
            name: "Важное",
            color: "#F07427"
        },
        "event": {
            name: "Мероприятие",
            color: "#36D593"
        },
        "study": {
            name: "Обучение",
            color: "#627CFF"
        }
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
        let color = categories[category].color
        if(!categories[category] || !categories[category].color) color = "#00AAF9" // Default Event Card Color
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
        if(categories[category] && categories[category].name) displayCategory = categories[category].name
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

    const fetchRecentEvents = async function() {
        //let data = await fetch()        
        return [
            {
                id: "321843249",
                title: "Перенос экзамена для группы 4 АДМО (2 курс)",
                text: "Внимание студентов 2 курса 4 группы АДМО! Экзамен по дисциплине Математический анализ (преподаватель Семёнов В.И.) переносится с 8:30 на 10:10\nПродолжительность экзамена осталась неизменной - 5 часов",
                category: "study",
                created_at: new Date().getTime() - 1000000,
                event_time: new Date().getTime() + 300000
            },
            {
                id: "321843250",
                title: "День физмата",
                text: "Завтра пройдёт день физмата. Почему так поздно? Ну, проект делается именно в такое время, поэтому приходится импровизировать. Конечно же, мы могли провести не день физмата, а что-то иное, но нам эта идея показалась странной\nКстати, в тексте оповещения можно использовать <b>HTML разметку</b>!\nЖдём на дне физмата всех учащихся и преподавателей. Приходите!\nДобавим ещё немного текста, чтобы это сообщение можно было листать вверх и вниз. Не зря ведь переделывался скорлл бар, верно?",
                category: "event",
                created_at: new Date().getTime() - 1100000,
                event_time: new Date().getTime() + 1010500
            },
        ]
    }

    // CALENDAR SCRIPT
    const events = {
        
    } // key:value = monthNumber:[{title,description,timestamp,category}]
    async function fecthAllEvents() {
        let data = await fetch("/events_all").then(response => {
            if(response.status == 200) return response.json()
        }).catch(err => {
            // TODO Handle connect error
        })
        return []
    }

    const refreshBtn = document.getElementById("refresh")
    let refreshClicked = false
    refreshBtn.addEventListener("click", () => {
        if(refreshClicked) return
        refreshBtn.style.animation = "refresh-rotate 1s infinite"
        refreshClicked = true
        // TODO Do some sync stuff
        
        // Temporary anim solution
        setTimeout(() => {
            refreshBtn.style.animation = "none"
            refreshClicked = false
        }, 2000)
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

        let monthName = monthStart.toLocaleString("default", {month: "long"})
        currentMonthText.textContent = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`
        currentCalendar = {month, year}
        
        let millisecondsInDay = 24 * 60 * 60 * 1000
        let cellIndex = 0
        let monthStartDay = monthStart.getDay() - 1
        if(monthStartDay == -1) monthStartDay = 6
        for(cellIndex; cellIndex < monthStartDay; cellIndex++) {
            let cell = calendar.children.item(cellIndex)
            let offsetDayTimestamp = monthStart.getTime() - millisecondsInDay * (monthStart.getDay() - cellIndex - 1)
            let offsetedDay = new Date(offsetDayTimestamp)
            if(!cell.classList.contains("inactive")) cell.classList.add("inactive")
            if(cell.classList.contains("current-date")) cell.classList.remove("current-date")
            if(offsetedDay.toDateString() == updateDate.toDateString()) cell.classList.add("current-date")
            cell.children.item(0).textContent = offsetedDay.getDate()
            cell.children.item(1).textContent = ""
        }

        let monthDay = 1
        let monthEnded = false
        while(!monthEnded) {
            let cell = calendar.children.item(cellIndex)
            let monthDate = new Date(monthStart.getTime() + millisecondsInDay * (monthDay - 1))
            if(monthDate.getMonth() != monthStart.getMonth()) {
                monthEnded = true
                continue
            }
            cellIndex++
            if(cell.classList.contains("inactive")) cell.classList.remove("inactive")
            if(cell.classList.contains("current-date")) cell.classList.remove("current-date")
            if(monthDate.toDateString() == updateDate.toDateString()) cell.classList.add("current-date")
            cell.children.item(0).textContent = monthDate.getDate()
            monthDay++
            // TODO Make server sync
            cell.children.item(1).textContent = ""
        }

        monthDay = 1
        for(cellIndex; cellIndex < calendar.children.length; cellIndex++) {
            let cell = calendar.children.item(cellIndex)
            if(!cell.classList.contains("inactive")) cell.classList.add("inactive")
            if(cell.classList.contains("current-date")) cell.classList.remove("current-date")
            if(monthDay == updateDate.getDate() && currentCalendar.month + 1 == updateDate.getMonth()) cell.classList.add("current-date")
            cell.children.item(0).textContent = monthDay
            monthDay++
            cell.children.item(1).textContent = ""
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

    function buildCalendarLayout() {
        calendar.innerHTML = ""
        let totalCells = 6 * 7
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
        }
    }
    


    const recentEvents = await fetchRecentEvents()
    if(recentEvents.length != 0) document.getElementById("events-carousel-empty").style.display = "none" 
    recentEvents.forEach((event) => {
        let eventCard = createEventCard(event.title, event.text, event.event_time, event.category)
        eventsCarousel.append(eventCard)
    })

    buildCalendarLayout()
    let now = new Date()
    updateCalendar(now.getMonth(), now.getFullYear())
    console.log("Calendar script loaded")
})