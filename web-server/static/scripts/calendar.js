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

    console.log("Calendar script loaded")
})