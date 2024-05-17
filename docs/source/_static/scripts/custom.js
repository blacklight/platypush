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

const addClipboard = (parent) => {
  const pre = parent.tagName === 'PRE' ? parent : parent.querySelector('pre')
  if (!pre)
    return

  const clipboard = document.createElement('i')
  const setClipboard = (img, text) => {
    clipboard.innerHTML = `<img src="https://static.platypush.tech/icons/${img}-64.png" alt="${text}">`
  }

  clipboard.classList.add('clipboard')
  setClipboard('clipboard-bw', 'Copy')
  clipboard.onclick = () => {
    if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
      setClipboard('ok', 'Copied!')
      setTimeout(() => setClipboard('clipboard-bw', 'Copy'), 2000)
      return navigator.clipboard.writeText(pre.innerText.trim())
    }

    return Promise.reject('The Clipboard API is not available.');
  }

  pre.style.position = 'relative'
  pre.appendChild(clipboard)
}

const Tabs = () => {
  let selectedTab = null
  let parent = null
  let data = {}

  const init = (obj) => {
    data = obj
    if (Object.keys(data).length && selectedTab == null)
      selectedTab = Object.keys(data)[0]
  }

  const select = (name) => {
    if (!parent) {
      console.warn('Cannot select tab: parent not set')
      return
    }

    if (!data[name]) {
      console.warn(`Cannot select tab: invalid name: ${name}`)
      return
    }

    const tabsBody = parent.querySelector('.body')
    selectedTab = name
    tabsBody.innerHTML = data[selectedTab]
    parent.querySelectorAll('.tabs li').forEach(
      (tab) => tab.classList.remove('selected')
    )

    const tab = [...parent.querySelectorAll('.tabs li')].find(
      (t) => t.innerText === name
    )

    if (!tab) {
      console.warn(`Cannot select tab: invalid name: ${name}`)
      return
    }

    addClipboard(tabsBody)
    tab.classList.add('selected')
  }

  const mount = (p) => {
    const tabs = document.createElement('div')
    tabs.classList.add('tabs')
    parent = p

    const tabsList = document.createElement('ul')
    Object.keys(data).forEach((title) => {
      const tab = document.createElement('li')
      tab.innerText = title
      tab.onclick = (event) => {
        event.stopPropagation()
        select(title)
      },

      tabsList.appendChild(tab)
    })

    const tabsBody = document.createElement('div')
    tabsBody.classList.add('body')

    tabs.appendChild(tabsList)
    tabs.appendChild(tabsBody)
    parent.innerHTML = ''
    parent.appendChild(tabs)
    select(selectedTab)
  }

  return {
    init,
    select,
    mount,
  }
}

const depsTabs = Tabs()

const convertDepsToTabs = () => {
  const depsContainer = document.getElementById('dependencies')
  if (!depsContainer)
    return

  const blocks = [...depsContainer.querySelectorAll('.highlight-bash')].map((block) => block.outerHTML)
  const titles = [...depsContainer.querySelectorAll('p strong')].map((title) => title.innerText)

  if (!(blocks.length && titles.length && blocks.length === titles.length))
    return

  const title = depsContainer.querySelector('h2')
  const tabsData = titles.reduce((obj, title, i) => {
    obj[title] = blocks[i]
    return obj
  }, {})

  depsTabs.init(tabsData)
  depsTabs.mount(depsContainer)
  depsContainer.prepend(title)
}

const generateComponentsGrid = () => {
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
}

const addClipboardToCodeBlocks = () => {
  document.querySelectorAll('pre').forEach((pre) => addClipboard(pre))
}

const renderActionsList = () => {
  const actionsList = document.getElementById('actions')?.querySelector('ul')
  if (!actionsList)
    return

  [...actionsList.querySelectorAll('li')].forEach((li) => {
    const link = li.querySelector('a')
    link.innerHTML = `<code class="docutils literal notranslate"><span class="pre">${link.innerText}</span></code>`
  })
}

const addFilterBar = () => {
  const container = document.querySelector('.bd-main')
  if (!container)
    return

  const referenceSection = document.getElementById('reference')
  if (!referenceSection)
    return

  const header = referenceSection.querySelector('h2')
  if (!header)
    return

  const input = document.createElement('input')
  input.type = 'text'
  input.placeholder = 'Filter'
  input.classList.add('filter-bar')
  input.addEventListener('input', (event) => {
    const filter = event.target.value.toLowerCase()
    referenceSection.querySelectorAll('ul.grid li').forEach((li) => {
      if (li.innerText.toLowerCase().includes(filter)) {
        li.style.display = 'flex'
      } else {
        li.style.display = 'none'
      }
    })
  })

  // Apply the fixed class if the header is above the viewport
  const headerOffsetTop = header.offsetTop
  document.addEventListener('scroll', () => {
    header.classList.toggle('fixed', headerOffsetTop < window.scrollY)
  })

  header.appendChild(input)
}

document.addEventListener("DOMContentLoaded", function() {
  generateComponentsGrid()
  convertDepsToTabs()
  addClipboardToCodeBlocks()
  renderActionsList()
  addFilterBar()
})
