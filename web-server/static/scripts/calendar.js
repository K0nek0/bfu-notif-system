document.addEventListener("DOMContentLoaded", event => {
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
        for(cellIndex; cellIndex < monthStart.getDay() - 1; cellIndex++) {
            let cell = calendar.children.item(cellIndex)
            let offsetDayTimestamp = monthStart.getTime() - millisecondsInDay * (monthStart.getDay() - cellIndex - 1)
            let offsetedDay = new Date(offsetDayTimestamp)
            if(!cell.classList.contains("inactive")) cell.classList.add("inactive")
            cell.children.item(0).textContent = offsetedDay.getDate()
            cell.children.item(1).textContent = ""
        }

        let monthDay = 1
        let monthEnded = false
        while(!monthEnded) {
            let cell = calendar.children.item(cellIndex)
            cellIndex++
            let monthDate = new Date(monthStart.getTime() + millisecondsInDay * (monthDay - 1))
            if(monthDate.getMonth() != monthStart.getMonth()) {
                monthEnded = true
                continue
            }
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
            cell.children.item(0).textContent = monthDay
            monthDay++
            cell.children.item(1).textContent = ""
        }
    }

    let now = new Date()
    updateCalendar(now.getMonth(), now.getFullYear())
    console.log("Calendar script loaded")
})