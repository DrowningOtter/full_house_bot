function showSidebar() {
    const sidebar = document.querySelector('.sidebar')
    sidebar.style.display = 'flex'
}
function hideSidebar() {
    const sidebar = document.querySelector('.sidebar')
    sidebar.style.display = 'none'
}


function autoResize(textarea) {
    textarea.style.height = '1px';
    textarea.style.height = (textarea.scrollHeight + 2) + 'px';
}
function autoAdjustTextareaHeight() {
    const textareas = document.querySelectorAll('.textarea-widget');
    textareas.forEach(textarea => {
        textarea.style.height = '1px';
        textarea.style.height = (textarea.scrollHeight + 2) + 'px';
    });
}

window.addEventListener('load', autoAdjustTextareaHeight);