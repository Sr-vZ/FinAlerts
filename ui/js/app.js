// // Example HTMX loading content dynamically (if using HTMX)
// document.querySelectorAll('a').forEach(link => {
//     link.addEventListener('click', event => {
//         const href = link.getAttribute('href');
//         if (href.startsWith('/')) {
//             event.preventDefault();
//             fetch(href)
//                 .then(response => response.text())
//                 .then(html => {
//                     document.getElementById('content').innerHTML = html;
//                 });
//         }
//     });
// });

function periodic_updates() {
    time = new Date()
    hours = time.getHours()
    if (hours > 9 && hours < 16) {
        setInterval(async () => {

        }, 1000);
    }
    else {
        index_ticker("nifty50")
    }
}


async function index_ticker(symbol) {
    // document.getElementById("index-ticker")
    res = await fetch("/nse_indices?symbol=" + symbol)
    data = await res.json()
    console.log(data)
    document.getElementById("index-ticker").querySelector('.stat-value').innerHTML = data['LTP']
    document.getElementById("index-ticker").querySelector('.stat-title').innerHTML = data['Name']
}

async function ohlc_data(symbol) {
    date = new Date()
    const today = new Date();
    const yyyy = today.getFullYear();
    let mm = today.getMonth() + 1; // Months start at 0!
    let dd = today.getDate();

    if (dd < 10) dd = '0' + dd;
    if (mm < 10) mm = '0' + mm;

    const end_date = dd + '-' + mm + '-' + yyyy;
    dd = dd - 7
    if (dd < 10) dd = '0' + dd
    const st_date = dd + '-' + mm + '-' + yyyy;
    // end_date = `${date.getDay()}-${date.getMonth() + 1}-${date.getFullYear()}`
    // st_date = `${parseInt(date.getDay()) - 7}-${date.getMonth() + 1}-${date.getFullYear()}`
    res = await fetch(`/indices/?symbol=NIFTY%2050&startdate=${st_date}&enddate=${end_date}&realtime=false`)
    data = await res.json()
    console.log(data)

}

periodic_updates()