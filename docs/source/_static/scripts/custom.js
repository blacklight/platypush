document.addEventListener("DOMContentLoaded", function() {
  const processList = (list, level, addTitle) => {
    const title = list.parentElement.querySelector('a')
    list.classList.add('grid')
    if (addTitle)
      title.classList.add('grid-title')

    list.querySelectorAll(`li.toctree-l${level}`).forEach((item) => {
      const link = item.querySelector('a')
      if (link) {
        item.style.cursor = 'pointer'
        item.addEventListener('click', () => link.click())
      }

      const name = item.querySelector('a').innerText
      const img = document.createElement('img')
      img.src = `https://static.platypush.tech/icons/${name.toLowerCase()}-64.png`
      img.alt = ' '
      item.prepend(img)
    })
  }

  const tocWrappers = document.querySelectorAll('.toctree-wrapper.compound')

  if (!tocWrappers.length) {
    return
  }

  if (window.location.pathname.endsWith('/index.html')) {
    if (tocWrappers.length < 2) {
      return
    }

    const referenceLists = [
      ...tocWrappers[1].querySelectorAll('ul li.toctree-l1 ul')
    ].slice(0, 4)

    referenceLists.forEach((list) => processList(list, 2, true))
  } else if (window.location.pathname.endsWith('/plugins.html') || window.location.pathname.endsWith('/backends.html')) {
    if (tocWrappers.length < 1) {
      return
    }

    const list = tocWrappers[0].querySelector('ul')
    if (list)
      processList(list, 1, false)
  }
})
