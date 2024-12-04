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

