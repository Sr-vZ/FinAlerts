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

async function index_ticker(symbol) {
    // document.getElementById("index-ticker")
    res = await fetch("nse_indices?symbol=" + symbol)
    data = await res.json()
    console.log(data)
    document.getElementById("index-ticker").querySelector('.stat-value').innerHTML = data['LTP']
    document.getElementById("index-ticker").querySelector('.stat-title').innerHTML = data['Name']
}